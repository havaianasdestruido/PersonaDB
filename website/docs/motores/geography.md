---
title: "Motor geográfico (geography.py)"
sidebar_label: geography — território
sidebar_position: 6
description: Cidades fictícias, bairros estratificados, modelo gravitacional e migração interna.
---

# `GeographyEngine` — território fictício

Arquivo: [`persona_db/engines/geography.py`](../referencia-api/engines/geography.md)

## 1. O conjunto de cidades

`CITY_SET` é construído **deterministicamente** na importação do módulo (`_build_city_set()`),
distribuindo 50 cidades fictícias pelas cinco macrorregiões:

| Região | Cidades | Peso demográfico de referência |
|---|---|---|
| Sudeste (SE) | 22 | 43% |
| Nordeste (NE) | 13 | 27% |
| Sul (S) | 8 | 15% |
| Norte (N) | 4 | 8% |
| Centro-Oeste (CO) | 3 | 7% |

Cada cidade carrega:

```python
{
  "city_id": "CID-001", "name": "…", "uf": "SP", "region": "SE",
  "population": 1_200_000, "base_class_dist": {"A": .03, "B1": .07, …},
  "cost_of_living": 1.36, "crime_index": 44, "university_count": 3,
}
```

Os nomes vêm da combinação de radicais (`_CITY_ROOT`), modificadores (`_CITY_MOD`) e, no Sul, um
sobrenome (`_SURNAMES_CITY`) — garantindo topônimos plausíveis e inexistentes.

## 2. Bairros e segregação residencial

`_build_neighborhoods()` cria de 8 a 11 bairros por cidade (≈ 500 no total), cada um com perfil de
classe, nível de criminalidade, qualidade de escola e de saúde:

```python
{"neighborhood_id": "BAI-0001", "city_id": "CID-001", "name": "Jardim 1",
 "class_profiles": ["C1"], "crime_level": 22, "school_quality": 9, "health_quality": 7}
```

A escolha do bairro filtra candidatos compatíveis com a classe da persona — é assim que a
segregação intraurbana emerge:

```python
cidade = engine.city_for_class("B1")
bairro = engine.neighborhood_for(cidade["city_id"], "B1")
```

## 3. Alocação urbana ponderada

A cidade é sorteada com peso proporcional a **população × adequação de classe**:

$$w_c = \text{pop}_c \cdot \max\big(0{,}01,\; \text{dist}_c(\text{classe})\big)$$

Isso reproduz, de forma aproximada, a lei de Zipf urbana (cidades grandes concentram pessoas) sem
ignorar o perfil socioeconômico local.

## 4. Modelo gravitacional de fluxo

$$F_{ij} = k \cdot \frac{\text{pop}_i \cdot \text{pop}_j}{d_{ij}^2}, \qquad k = 10^{-3}$$

```python
GeographyEngine.gravity_model(pop_i=1_200_000, pop_j=540_000, distance_km=380)
```

A distância é limitada inferiormente a 0,5 km para evitar divisão por zero.

## 5. Probabilidade de migração

```python
engine.migration_prob(age=27, class_label="B1", job_opportunity_ratio=1.2)
```

| Componente | Efeito |
|---|---|
| base | 0,03 |
| idade entre 18 e 35 | +0,05 |
| classe A ou B1 | +0,02 |
| classe C2 ou D_E | −0,01 |
| razão de oportunidades de emprego | multiplicador ≥ 0,5 |

Resultado limitado a $[0{,}01;\ 0{,}50]$.

## 6. Resumo do território

```python
from persona_db.engines.geography import city_summary
city_summary()
# {"n_cidades": 50, "n_bairros": …, "regioes": ["CO", "N", "NE", "S", "SE"], "ufs": [...]}
```

## Onde isso aparece no schema

`endereco`, `residencia`, `historico_residencia`, `condominio`, `vizinho`,
`pessoa.cidade_nascimento`, `pessoa.uf_nascimento`, além de servir de base para hospitais, escolas,
empresas e lojas, que herdam cidade e bairro das personas que atendem.

:::info Nomes fictícios por construção
Nenhuma cidade, bairro, UF-cidade ou CEP corresponde a um lugar real. As UFs são siglas
verdadeiras apenas para manter o formato de duas letras; os municípios associados são inventados.
:::
