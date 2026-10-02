---
title: Dados de referência (seeds)
sidebar_label: Visão geral
sidebar_position: 0
description: Catálogos determinísticos e tabelas de probabilidade usados pelos geradores.
---

# Dados de referência

O pacote [`persona_db/seeds/`](/docs/referencia-api/seeds) concentra tudo o que é **fixo** no
PersonaDB: catálogos de nomes, lugares e instituições fictícias, e as distribuições de
probabilidade calibradas.

| Módulo | Conteúdo |
|---|---|
| [`lookup_data.py`](./lookup-data.md) | nomes, cidades, bairros, bancos, empresas, universidades, hospitais, profissões, doenças, medicamentos, cursos, raças de pet, partidos, salário mínimo histórico, IPCA |
| [`probability_tables.py`](./probability-tables.md) | mobilidade social, mortalidade, incidência de doenças, criminalidade, emprego, renda (Lorenz), ancestralidade → traços |

## Por que separar seeds de engines

- **Motores** descrevem *mecanismos* (como a renda se forma).
- **Seeds** descrevem *o mundo* (quais empresas existem, quanto era o salário mínimo em 2015).

Essa separação permite trocar o universo fictício — por exemplo, gerar personas de outro país —
sem alterar uma linha dos modelos probabilísticos.

## Determinismo dos catálogos

Vários catálogos são **construídos em tempo de importação** por funções puras:

```python
BAIRROS: list[dict] = _build_bairros()
PROFISSOES: list[dict] = _build_profissoes()
DOENCAS = _fill_doencas()
IPCA_MENSAL: list[dict] = _build_ipca()
INCOME_DIST: list[float] = _lorenz_curve(_GINI, 100)
```

Como não há aleatoriedade nessas funções, o conteúdo é idêntico em qualquer máquina e execução.

## Dados fictícios com formato válido

Alguns campos precisam **parecer** reais para exercitar validações de sistemas consumidores sem
jamais corresponder a registros verdadeiros:

```python
def _valid_cnpj(digits14: str) -> bool: ...
def _make_cnpj(seed_str: str) -> str: ...
```

Os CNPJs das empresas fictícias passam no cálculo dos dígitos verificadores, mas pertencem a
empresas inventadas. O mesmo vale para documentos gerados em `gen_01_identidade`.

:::danger Nunca use para fins reais
Formatos válidos não transformam dados fictícios em dados legítimos. Não use esses identificadores
em cadastros, testes de produção com terceiros ou qualquer contexto em que possam ser confundidos
com documentos reais.
:::
