---
title: "Motor de saúde (health.py)"
sidebar_label: health — saúde e mortalidade
sidebar_position: 4
description: Gompertz–Makeham, hazard por doença, diagnósticos, risco mental e impacto crônico.
---

# `HealthEngine` — sobrevivência e morbidade

Arquivo: [`persona_db/engines/health.py`](../referencia-api/engines/health.md)

## 1. Hazard por doença

`lifetime_hazard(age, sex, disease)` devolve a taxa anual de incidência:

| Doença | Modelo | Parâmetros |
|---|---|---|
| `cancer` | Gompertz | $\lambda(t) = a\,e^{bt}$, com $a = 3\times10^{-4}$, $b = 0{,}085$ |
| `diabetes` | degrau etário | $0{,}007$ a partir dos 40 anos |
| `hipertension` | degrau etário | $0{,}015$ a partir dos 35 anos |
| `depression` | janela etária | $0{,}021$ entre 25 e 44; $0{,}008$ acima de 44; 0 antes dos 25 |

Doenças fora de `DISEASE_TRANCHES` têm hazard zero — acrescentar uma nova condição é só adicionar
uma entrada no dicionário de constantes.

## 2. Sobrevivência (Gompertz–Makeham)

A força total de mortalidade soma um risco basal por sexo e todos os hazards de doença:

$$h(t) = h_0(\text{sexo}) + \sum_d \lambda_d(t,\text{sexo}),
\qquad S(t) = \exp\!\left(-\int_0^t h(u)\,du\right)$$

com $h_0 = 0{,}020$ (masculino) e $0{,}018$ (feminino). A integral é aproximada por **regra do
trapézio em passos anuais**, com tratamento explícito da fração final de ano, e o resultado é
limitado a $(10^{-12},\,1]$.

```python
HealthEngine.survival(age=0,  sex="masculino")   # 1.0
HealthEngine.survival(age=40, sex="feminino")    # decresce monotonicamente
HealthEngine.survival(age=90, sex="masculino")   # valor pequeno, nunca zero exato
```

:::note Simplificação consciente
O modelo é um *proxy* didático: trata o hazard de doença como aditivo à mortalidade e usa
parâmetros fixos por sexo. Ele não reproduz a tábua de vida do IBGE. A tábua de mortalidade usada
nas decisões de óbito do hub é a de `seeds.probability_tables.mortality_qx`.
:::

## 3. Simulação de diagnósticos

`simulate_diagnoses(...)` percorre as doenças de `DISEASE_TRANCHES`, acumula o hazard até a idade
atual (`_cumulative_hazard`), aplica o multiplicador hereditário e sorteia ocorrência e data de
diagnóstico. Quem tem predisposição familiar registrada carrega:

$$\text{risco} = 1{,}9 \times \text{risco basal}$$

## 4. Saúde mental

```python
score = HealthEngine.mental_risk_score({"desemprego": 1, "divorcio": 1, "doenca_cronica": 0})
HealthEngine.mental_disorder(rng, score)
```

`mental_risk_score` agrega fatores de risco em um escore e `mental_disorder` o converte em evento
binário — base da tabela `saude_mental_registro` e das terapias do domínio 03.

## 5. Impacto crônico

```python
HealthEngine.chronic_impact(rng, has_chronic=True)
# {"salary_factor": …, "absence_days": …, "dropout_prob": …}
```

Doenças crônicas propagam efeitos para outros domínios: redução esperada de salário, aumento de
licenças médicas em `licenca_trabalho` e maior probabilidade de evasão escolar em `reprovacao` /
`matricula`. É um dos pontos em que o motor de saúde "realimenta" o motor socioeconômico via
geradores.

## Níveis de severidade

`SEVERITY_LEVELS = ["leve", "moderado", "grave"]` e
`CHRONIC_DISEASES = ("diabetes", "hipertension", "depression")` padronizam os rótulos gravados nas
tabelas `doenca_pessoa`, `condicao_cronica` e `tratamento`.

## Onde isso aparece no schema

| Tabela | Conteúdo derivado |
|---|---|
| `doenca_pessoa`, `tratamento`, `sintoma_ocorrencia` | diagnósticos sorteados pelo hazard |
| `condicao_cronica` | doenças de `CHRONIC_DISEASES` que persistem |
| `internacao`, `cirurgia`, `alta_hospitalar` | eventos graves derivados da severidade |
| `saude_mental_registro`, `terapia`, `sessao_terapia` | escore de risco mental |
| `pessoa.esta_vivo`, `pessoa.data_obito` | tábua de mortalidade + sobrevivência |
