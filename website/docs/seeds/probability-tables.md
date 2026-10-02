---
title: "Tabelas de probabilidade (probability_tables.py)"
sidebar_label: probability_tables
sidebar_position: 2
description: Mobilidade, mortalidade, doenças, crimes, emprego, renda e ancestralidade.
---

# `probability_tables.py` — distribuições calibradas

Arquivo: [`persona_db/seeds/probability_tables.py`](../referencia-api/seeds/probability_tables.md)

## Classes e faixas etárias

```python
SOCIAL_CLASSES = ["A", "B1", "B2", "C1", "C2", "D_E"]
AGE_BANDS = [(0, 4), (5, 9), …]
```

## Mobilidade social

`SOCIAL_MOBILITY_MATRIX` é a matriz 6×6 pais → filhos, **renormalizada defensivamente** na
importação para que toda linha some exatamente 1. É a mesma estrutura usada por
[`SocioeconomicEngine`](../motores/socio.md) — mantê-las coerentes é responsabilidade de quem
recalibra.

## Mortalidade

```python
def mortality_qx(age: int, sex: str) -> float: ...
```

Tábua de vida fictícia construída a partir de $q_x$ no primeiro ano (0,055 masculino / 0,047
feminino), com idade máxima 110. `MORTALITY_TABLE` guarda o vetor por sexo; `gen_00_pessoa` acumula
$\sum q_x$ para decidir `esta_vivo` e sortear a data de óbito.

## Incidência de doenças

```python
DISEASE_BY_AGE_SEX: dict[str, dict[str, dict[str, float]]]
def disease_incidence(disease: str, age: int, sex: str) -> float: ...
```

Complementa o hazard paramétrico de [`HealthEngine`](../motores/health.md) com uma tabela empírica
por faixa etária e sexo.

## Criminalidade

```python
CRIME_BY_PROFILE: dict[str, dict[str, dict[str, float]]]
def crime_rate(crime: str, sexo: str, idade: int) -> float: ...
```

Faixas usadas: `15-19`, `20-29`, `30-44`, `45+`. Serve de taxa base por tipo de crime, enquanto o
[`CriminalEngine`](../motores/criminal.md) aplica o modelo logístico individual.

## Emprego

```python
EMPLOYMENT_RATES: dict[str, dict[str, dict[str, float]]]
def employment_rate(sector: str, education: str, age: int) -> float: ...
```

Combina uma base por setor (`_SECTOR_EMPLOYMENT_BASE`), um bônus por escolaridade (`_EDU_BOOST`) e
um fator etário (`_AGE_EMPLOYMENT_FACTOR`). Setores: aberto, agro, comércio, construção, educação,
saúde, indústria, tecnologia, financeiro e público.

## Distribuição de renda (curva de Lorenz)

```python
_GINI = 0.52
INCOME_DIST = _lorenz_curve(_GINI, 100)
def income_share_percentile(p: float) -> float: ...
```

A curva é derivada analiticamente do coeficiente de Gini alvo (0,52) e discretizada em 100 pontos.
`income_share_percentile(p)` devolve a fração da renda total acumulada até o percentil $p$ — usada
para posicionar patrimônio e consumo de forma desigual, como no Brasil real.

## Ancestralidade → traços

```python
ANCESTRY_TO_TRAITS: dict[str, dict[str, dict[str, float]]]
def trait_probs(ancestry: str, trait: str) -> dict[str, float]: ...
```

Mapeia a ancestralidade fictícia da persona (europeia, africana, indígena, asiática, mista) em
distribuições de probabilidade para traços fenotípicos como cor de pele, olhos e cabelos. O
`GeneticEngine` usa essas distribuições apenas como **prior**: quando há pais conhecidos, a
herança mendeliana prevalece.

:::caution Simplificação consciente
Ancestralidade não determina fenótipo de forma determinística, e as categorias usadas aqui são
rótulos ficcionais grosseiros, escolhidos para produzir variabilidade plausível no dataset. Não
tome esses números como afirmações biológicas ou demográficas.
:::

## Recalibrando

1. Altere a constante ou a função geradora da tabela.
2. Rode `python3 -m pytest persona_db/tests/statistical -q` — os testes de distribuição comparam
   agregados com faixas esperadas em $N = 1000$.
3. Atualize [`MATH_MODELS.md`](https://github.com/havaianasdestruido/PersonaDB/blob/main/persona_db/docs/MATH_MODELS.md)
   e a página do motor correspondente nesta documentação.
4. Lembre-se: a mudança **invalida datasets anteriores** gerados com a mesma semente.
