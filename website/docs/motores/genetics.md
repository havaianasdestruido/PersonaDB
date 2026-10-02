---
title: "Motor genético (genetics.py)"
sidebar_label: genetics — herança
sidebar_position: 3
description: Punnett ABO e Rh, cor de olhos e cabelos, estatura mid-parent, lateralidade e PRS.
---

# `GeneticEngine` — herança de traços

Arquivo: [`persona_db/engines/genetics.py`](../referencia-api/engines/genetics.md)

Este motor garante que filhos sejam **geneticamente compatíveis** com os pais — a restrição mais
visível de coerência do PersonaDB, verificada também pelo validador de genealogia e por uma função
PL/pgSQL (`validar_tipo_sanguineo_filho`).

## 1. Sistema ABO e fator Rh

Alelos $\{I^A, I^B, i\}$, com $I^A$ e $I^B$ codominantes e $i$ recessivo:

| Fenótipo | Genótipos |
|---|---|
| A | $(I^A, I^A)$, $(I^A, i)$ |
| B | $(I^B, I^B)$, $(I^B, i)$ |
| AB | $(I^A, I^B)$ |
| O | $(i, i)$ |

Priors populacionais usados quando não há pais conhecidos: **O 47%, A 41%, B 9%, AB 3%**;
**Rh+ 87%, Rh− 13%**.

```python
GeneticEngine.punnett_abo("A", "B")   # {"A": .25, "B": .25, "AB": .25, "O": .25} (heterozigotos)
GeneticEngine.rh_punnett("-", "-")    # {"-": 1.0}
GeneticEngine.validate_child_blood("O", "O", "+", "-", "A")   # False
```

Regra dura: **dois pais Rh− só podem ter filhos Rh−**, e `validate_child_blood` rejeita qualquer
combinação impossível.

## 2. Cor dos olhos (poligênico simplificado OCA2/HERC2)

Dois loci equivalentes com alelos $\{B, G, g, b\}$ — castanho dominante, verde intermediário,
avelã e azul recessivo. O quadro de Punnett de olhos (`eye_color_chart`) cruza os genótipos dos
pais; pais homozigotos $(b,b) \times (b,b)$ **nunca** geram filhos castanhos.

Há ainda um mecanismo de **variante rara** (`_rare_variant`) que introduz, com baixa probabilidade,
um alelo não presente nos pais, simulando mutações e ancestralidade não registrada.

## 3. Cor do cabelo

`hair_color()` combina a herança parental com os priors de ancestralidade de
`seeds.probability_tables.ANCESTRY_TO_TRAITS`, mantendo coerência com `pele` e `cor_olhos`.

## 4. Lateralidade (modelo logístico familiar)

$$\text{logit}\big(\mathbb{P}(\text{canhoto})\big) = -2{,}10 + 0{,}69 \cdot \mathbb{I}(\text{pai canhoto}) + 0{,}55 \cdot \mathbb{I}(\text{mãe canhota})$$

| Pais | P(canhoto) |
|---|---|
| nenhum canhoto | ≈ 10,9% |
| só o pai | ≈ 19,6% |
| só a mãe | ≈ 17,4% |
| ambos | ≈ 30,0% |

## 5. Estatura adulta (mid-parent de Galton)

$$\mu_{\text{alt}} = \begin{cases}
\dfrac{H_{\text{pai}} + 1{,}08\,H_{\text{mãe}}}{2}, & \text{masculino} \\[8pt]
\dfrac{0{,}923\,H_{\text{pai}} + H_{\text{mãe}}}{2}, & \text{feminino}
\end{cases}
\qquad H_{\text{filho}} \sim \mathcal{N}(\mu_{\text{alt}},\, 6{,}5^2)$$

O fator $1{,}08$ (e seu inverso $0{,}923$) representa o dimorfismo sexual de ±8%, e o desvio-padrão
de 6,5 cm produz a regressão à média característica do modelo de Galton.

## 6. Peso a partir da estatura

```python
GeneticEngine.peso_from_height(altura_cm=172, sex="masculino", disease_chronic=True)
```

O IMC é sorteado de uma log-normal e ajustado para cima na presença de doença crônica; o peso
final é $W = \text{IMC} \cdot (H/100)^2$.

## 7. Escore poligênico de risco (PRS)

```python
prs = engine.prs_risk("diabetes", family_effects={"pai": True}, genotypes=None)
engine.has_hereditary_disease(prs, threshold=0.5)
```

`prs_risk` combina efeitos familiares e genótipos em um escore em $[0, 1]$, consumido por
`gen_02_genealogia` (tabela `predisposicao_genetica`) e por `HealthEngine.hereditary_multiplier`,
que multiplica por **1,9** o risco basal de quem tem predisposição registrada.

## Invariantes testadas

- `tests/unit/test_genetics.py` — tabelas de Punnett, pais Rh− ⇒ filhos Rh−, olhos azuis recessivos.
- `tests/unit/test_genetics_family_geo.py` — mid-parent, dimorfismo, faixas de IMC.
- `validators/val_genealogia.py` — percorre o dataset conferindo compatibilidade pai/mãe/filho.
- `sql/schema/99_functions.sql` — `validar_tipo_sanguineo_filho()` replica a regra no banco.
