---
title: "Catálogos (lookup_data.py)"
sidebar_label: lookup_data
sidebar_position: 1
description: Nomes, lugares, instituições, profissões e séries econômicas fictícias.
---

# `lookup_data.py` — catálogos fictícios

Arquivo: [`persona_db/seeds/lookup_data.py`](../referencia-api/seeds/lookup_data.md)

## Inventário

| Constante | Tipo | Conteúdo |
|---|---|---|
| `MALE_FIRST_NAMES`, `FEMALE_FIRST_NAMES` | `list[str]` | prenomes usados por `gen_00_pessoa` |
| `SURNAMES` | `list[str]` | sobrenomes; personas recebem 1 ou 2 (78% recebem 2) |
| `CIDADES` | `list[dict]` | municípios fictícios com UF, região e população |
| `BAIRROS` | `list[dict]` | derivado de `CIDADES` por `_build_bairros()` |
| `BANCOS` | `list[dict]` | instituições financeiras fictícias |
| `EMPRESAS` | `list[dict]` | empregadores com CNPJ fictício válido e setor |
| `UNIVERSIDADES` | `list[dict]` | instituições de ensino superior |
| `HOSPITAIS` | `list[dict]` | rede hospitalar fictícia |
| `PROFISSOES` | `list[dict]` | ocupações com setor e faixa salarial (`_build_profissoes()`) |
| `DOENCAS` | `list[dict]` | catálogo clínico (`_fill_doencas()`) |
| `MEDICAMENTOS` | `list[dict]` | princípios ativos fictícios |
| `CURSOS` | `list[dict]` | cursos de graduação e técnicos |
| `RACAS_PET` | `list[dict]` | raças de cães, gatos e outros |
| `PARTIDOS` | `list[dict]` | legendas fictícias para o domínio eleitoral |
| `MIN_WAGE_HISTORY` | `list[dict]` | salário mínimo por ano |
| `IPCA_MENSAL` | `list[dict]` | série mensal de inflação (`_build_ipca()`) |

## Séries econômicas

`MIN_WAGE_HISTORY` é a referência usada por `gen_05_carreira.min_wage_for_year(year)` e pelo
validador financeiro: **nenhum salário registrado pode ficar abaixo do piso do ano de
contratação**. `IPCA_MENSAL` corrige valores monetários ao longo do tempo (faturas, aluguéis,
preços de produtos).

```python
from persona_db.seeds.lookup_data import MIN_WAGE_HISTORY
from persona_db.generators.gen_05_carreira import min_wage_for_year

min_wage_for_year(2015), min_wage_for_year(2024)
```

## Geografia: `CIDADES` vs. `GeographyEngine.CITY_SET`

Existem **duas** fontes de territórios fictícios:

| Fonte | Papel |
|---|---|
| `seeds.lookup_data.CIDADES` / `BAIRROS` | catálogo tabular usado por geradores que precisam de endereços |
| `engines.geography.CITY_SET` / `NEIGHBORHOODS` | território procedural (50 cidades, ~500 bairros) usado na alocação por classe e na migração |

As duas são determinísticas; ao criar um domínio novo, prefira o motor geográfico quando a escolha
depender de classe social e o catálogo quando for apenas um rótulo de endereço.

## Empresas e CNPJ

```python
def _make_cnpj(seed_str: str) -> str: ...
def _valid_cnpj(digits14: str) -> bool: ...
```

Cada empresa fictícia tem CNPJ formalmente válido (dígitos verificadores corretos) derivado do
nome — estável entre execuções e nunca correspondente a uma empresa real.

## Estendendo um catálogo

1. Acrescente entradas **ao final** da lista (inserir no meio desloca índices e muda sorteios
   ponderados por posição).
2. Mantenha as mesmas chaves dos dicionários existentes.
3. Rode `python3 -m pytest persona_db/tests -q` — a suíte estatística detecta mudanças grosseiras
   de distribuição.
4. Lembre-se de que **qualquer alteração aqui muda os datasets gerados** com a mesma semente.
