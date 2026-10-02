---
title: "run_validators — validação de consistência"
sidebar_label: run_validators
sidebar_position: 2
description: CLI que regenera um dataset e aplica todos os validadores.
---

# `validators.run_validators`

```bash
python3 -m persona_db.validators.run_validators [opções]
```

Regenera um dataset com a semente informada e aplica as 10 verificações
([4 estruturais + 6 de domínio](../validadores/index.md)).

## Flags

| Flag | Padrão | Descrição |
|---|---|---|
| `--personas` | `100` | Número de personas a gerar para validação |
| `--seed` | `7` | Semente determinística |
| `--html-out` | — | Caminho opcional para o relatório HTML |

## Exemplo

```bash
python3 -m persona_db.validators.run_validators --personas 500 --seed 42 --html-out report.html
```

```json
{"passed": true, "violation_count": 0, "overall_consistency_pct": 100.0,
 "domain_consistency": {"genealogia": 100.0, "temporal": 100.0, "financas": 100.0,
                        "saude": 100.0, "juridico": 100.0, "social": 100.0},
 "tables_count": 257, "total_rows": 171034}
```

Retorna `0` quando `passed` é verdadeiro e `1` caso contrário — pronto para ser um passo de CI.

:::note Ele regenera, não lê arquivo
Este CLI **não** aceita um `dataset.json` de entrada: ele chama `generate_all(n, seed)` internamente.
Para validar um JSON existente, use a API:

```python
import json
from persona_db.validators import validate_dataset

dataset = json.load(open("dataset.json"))
report = validate_dataset(dataset)
print(report["passed"], report["violations_by_rule"])
```
:::

## Funções exportadas

```python
from persona_db.validators import (
    validate_dataset,            # relatório consolidado
    build_validation_table_rows, # linhas de validacao_consistencia
    render_html_report,          # relatório HTML
    validate_genealogia, validate_temporal, validate_financas,
    validate_saude, validate_juridico, validate_social,
)
```

Detalhes do formato em [Relatório de validação](../validadores/relatorio.md) e a lista completa de
regras em [Catálogo de regras](../validadores/regras.md).

## Via Makefile

```bash
make -C persona_db validate N_PESSOAS=200 SEED=42
```
