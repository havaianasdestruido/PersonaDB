---
title: Contratos de dados
sidebar_label: Contratos de dados
sidebar_position: 4
description: O dicionário da persona, o formato do dataset e o relatório de validação.
---

# Contratos de dados

Três estruturas circulam por todo o sistema. Elas são dicionários Python simples — sem ORM, sem
classes — o que mantém o pipeline barato e serializável.

## 1. O dicionário da persona

Produzido por `gen_00_pessoa.build_persona()` e enriquecido pelos demais geradores.

| Campo | Tipo | Origem |
|---|---|---|
| `id` | `str` (UUID5) | determinístico a partir do índice e da semente |
| `idx` | `int` | posição na geração |
| `nome_completo`, `nome_social`, `ultimo_sobrenome` | `str`/`None` | catálogos `MALE_FIRST_NAMES`, `FEMALE_FIRST_NAMES`, `SURNAMES` |
| `data_nascimento` | `str` ISO | pirâmide etária fictícia + âncora temporal |
| `sexo` | `"masculino" \| "feminino"` | Bernoulli(0,5) |
| `nacionalidade` | `str` | catálogo |
| `cidade_nascimento`, `uf_nascimento`, `cidade_residencia` | `str` | `GeographyEngine` |
| `classe_social` | `"A" \| "B1" \| "B2" \| "C1" \| "C2" \| "D_E"` | `SocioeconomicEngine.sample_class` |
| `estado_civil` | `str` | perfil por faixa etária |
| `esta_vivo` | `bool` | tábua de mortalidade |
| `data_obito` | `str` ISO \| `None` | só quando `esta_vivo` é falso |
| `education` | `"fundamental" \| "medio" \| "superior" \| "pos"` | logit ordinal |
| `setor_empregado` | `str` | catálogo de setores |
| `ancestry`, `ancestry_pcts` | `str`, `dict[str, float]` | priors de ancestralidade (Dirichlet) |
| `cor_olhos`, `cor_cabelo`, `pele`, `mao_dominante` | `str` | `GeneticEngine` |
| `tipo_sanguineo`, `fator_rh` | `str` | Punnett ABO/Rh |
| `altura`, `peso` | `float` | mid-parent de Galton + IMC log-normal |
| `criminal` | `dict` | `CriminalEngine.criminal_process_series()` |

Campos acrescentados em tempo de execução por geradores posteriores (exemplos):
`pai_id`, `mae_id`, `geracao`, `tem_doenca_grave`, `impactos_saude`, `tem_antecedente_criminal`.

:::tip Projeção para a tabela `pessoa`
`as_pessoa_row(persona)` recorta apenas as colunas que existem no DDL do hub. Campos auxiliares
(como `criminal` ou `ancestry_pcts`) **nunca** chegam ao banco — eles existem só para coordenar os
geradores.
:::

## 2. O dataset em memória

```python
Dataset = dict[str, list[dict[str, Any]]]
```

Um mapa `nome_da_tabela → lista de linhas`, onde cada linha é um dicionário cujas chaves são nomes
de coluna do DDL. Regras do contrato:

- as chaves de tabela **devem** existir no schema PostgreSQL (`sql/schema/*.sql`);
- valores são tipos JSON-serializáveis; datas são `str` em ISO-8601;
- `None` representa `NULL`;
- `dict`/`list` aninhados são serializados como JSON pelo exportador e pelo carregador;
- toda tabela satélite carrega `pessoa_id` apontando para `pessoa.id`.

```python
{
  "pessoa": [{"id": "…", "nome_completo": "…", "data_nascimento": "1988-04-12", …}],
  "doenca_pessoa": [{"id": "…", "pessoa_id": "…", "doenca_id": "…", "data_diagnostico": "2019-07-02"}],
  …
}
```

## 3. O contrato do gerador

Todo módulo `gen_XX_*.py` expõe:

```python
def generate(
    personas: list[dict],
    seed: int = 7,
    today: date | None = None,
    # apenas 07_residencia, 11_juridico, 13_viagens e 16_timeline:
    existing_tables: dict[str, list[dict]] | None = None,
) -> dict[str, list[dict]]:
    ...
```

Detalhes e checklist em [Contrato dos geradores](../geradores/contrato.md).

## 4. O relatório de validação

Devolvido por `validate_dataset(dataset, today=None)`:

| Chave | Tipo | Significado |
|---|---|---|
| `passed` | `bool` | nenhuma violação encontrada |
| `violation_count` / `critical_violations` | `int` | total de violações (deduplicadas) |
| `violations` | `list[dict]` | cada item tem `domain`, `rule` e, quando aplicável, `person_id`, `table`, `value` |
| `violations_by_rule` | `dict[str, int]` | contagem por regra |
| `domain_consistency` | `dict[str, float]` | percentual de consistência por domínio validado |
| `overall_consistency_pct` | `float` | média dos percentuais por domínio |
| `row_counts` | `dict[str, int]` | linhas por tabela |

```json
{
  "passed": false,
  "violation_count": 2,
  "violations": [
    {"domain": "genealogia", "rule": "parent_at_least_14", "person_id": "…", "parent_id": "…"},
    {"domain": "temporal", "rule": "end_before_start", "table": "contrato_trabalho", "start": "2021-03-01", "end": "2020-12-01"}
  ],
  "domain_consistency": {"genealogia": 99.5, "temporal": 99.5, "financas": 100.0,
                         "saude": 100.0, "juridico": 100.0, "social": 100.0},
  "overall_consistency_pct": 99.83
}
```

## 5. Convenções de identificadores

| Convenção | Exemplo |
|---|---|
| UUID de linha derivado de chave estável | `uuid5(NAMESPACE_URL, f"doenca-pessoa-{pessoa_id}-{i}")` |
| Catálogos compartilhados têm ID próprio e sem `pessoa_id` | `hospital`, `empresa`, `banco`, `partido` |
| Tabelas de junção usam PK composta | `pessoa_habilidade(pessoa_id, habilidade_id)` |
| Datas sempre como `str` ISO | `"2026-01-01"` |
| Valores monetários em `float` BRL | `4231.57` |
