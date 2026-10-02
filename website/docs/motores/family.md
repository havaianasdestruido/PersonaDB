---
title: "Motor de família (family.py)"
sidebar_label: family — nupcialidade
sidebar_position: 5
description: Hazard de casamento, homogamia, fecundidade de Poisson e divórcio logístico.
---

# `FamilyEngine` — nupcialidade e fecundidade

Arquivo: [`persona_db/engines/family.py`](../referencia-api/engines/family.md)

## Constantes de calibração

| Constante | Valor | Significado |
|---|---|---|
| `P_CASAMENTO_ALGUM_DIA` | 0,72 | fração que se casa ao menos uma vez |
| `P_DIVORCIO` | 0,21 | taxa de referência de divórcio |
| `P_SEGUNDO_CASAMENTO` | 0,38 | recasamento após divórcio ou viuvez |
| `SAME_CLASS_PROB` | 0,58 | homogamia de classe |
| `SAME_EDU_PROB` | 0,55 | homogamia educacional |
| `SAME_RELIGION_PROB` | 0,61 | homogamia religiosa |

## 1. Hazard de primeiro casamento

Curva gaussiana por idade e sexo:

$$h(\text{idade}) = \text{pico} \cdot \exp\!\left(-\tfrac{1}{2}\left(\frac{\text{idade} - \mu}{\sigma}\right)^2\right)$$

| Sexo | $\mu$ | $\sigma$ | pico |
|---|---|---|---|
| masculino | 30,0 | 6,0 | 0,12 |
| feminino | 27,0 | 5,0 | 0,13 |

`first_marriage_age(sex)` devolve `None` para os 28% que nunca se casam e, caso contrário, uma
idade $\mathcal{N}(30; 4^2)$ (homens) ou $\mathcal{N}(27; 4^2)$ (mulheres), **limitada ao intervalo
[16, 55]** anos.

## 2. Homogamia

```python
engine.spouse_class("C1")        # 58% "C1"; senão, classe adjacente
engine.homogamy_age_diff()       # |N(2,5; 4,2²)| anos de diferença
```

O cônjuge nunca "salta" mais de uma posição na ordem `A → B1 → B2 → C1 → C2 → D_E`.

## 3. Fecundidade

$$N_{\text{filhos}} \sim \text{Poisson}(\lambda_{\text{classe}})$$

| Classes | $\lambda$ |
|---|---|
| A, B1, B2 | 1,4 |
| C1 | 1,9 |
| C2, D_E | 2,6 |

Modificadores somam-se a $\lambda$ antes do sorteio: `doenca`, `divorcio` e `superior` (ensino
superior tipicamente reduz a fecundidade esperada).

```python
engine.children_count("C2", {"superior": -0.6})
```

## 4. Divórcio (logístico)

$$\text{logit}(p) = -1{,}35 + 0{,}8\,x_{\text{saúde mental}} + 1{,}2\,x_{\text{antecedente}} + 0{,}3\,x_{\text{dif. classe}} + 0{,}5\,x_{\text{desemprego}} - 0{,}4\,x_{\text{filhos pequenos}} - 0{,}5\,x_{\text{religiosidade}}$$

A probabilidade final é limitada a 0,9. Note o acoplamento explícito com outros motores:
antecedentes criminais do cônjuge (`CriminalEngine`) e transtorno mental (`HealthEngine`) elevam o
risco; filhos pequenos e religiosidade alta protegem.

## 5. Ciclo de vida afetiva

```python
engine.union_lifecycle(sex="feminino", class_label="B2")
# {"casou": True, "primeiro_casamento_idade": 26.4, "conjuge_classe": "B2", "divorcio": False, …}
```

É o atalho usado por `gen_08_relacionamentos` para montar, de uma vez, namoro → casamento →
(eventual) divórcio → recasamento, preservando a ordem cronológica.

## 6. Mortalidade auxiliar

`death_likelihood(age, sex)` é uma aproximação grosseira usada em simulações de parentes
ascendentes (que não passam pelo pipeline completo):

| Faixa | Probabilidade |
|---|---|
| < 5 anos | 0,008 |
| 5–39 | $0{,}002 + 0{,}0002 \cdot \text{idade}$ |
| 40–69 | $0{,}02 + 0{,}004 \cdot (\text{idade} - 40)$ |
| ≥ 70 | $0{,}12 + 0{,}03 \cdot (\text{idade} - 70)$ |

Homens recebem multiplicador 1,15 e o resultado é limitado a 0,99.

## Onde isso aparece no schema

`relacionamento`, `namoro`, `casamento`, `divorcio`, `uniao_estavel`, `filho`,
`guarda_compartilhada`, `pensao_alimenticia`, `familia`, `membro_familia`, `parentesco`,
`arvore_genealogica`.
