---
title: "generate — orquestrador de geração"
sidebar_label: generate
sidebar_position: 1
description: Flags, saída, códigos de retorno e uso programático do orquestrador.
---

# `scripts.generate`

```bash
python3 -m persona_db.scripts.generate [opções]
```

Executa o [pipeline completo](../arquitetura/pipeline.md): personas base → 23 geradores de domínio
→ junções N:N → metadados → validação → JSON.

## Flags

| Flag | Padrão | Descrição |
|---|---|---|
| `--personas` / `--people` | `100` | Número de personas a gerar |
| `--seed` | `7` | Semente mestre |
| `--batch-size` | `100` | Tamanho de lote informado no resumo (não altera o resultado) |
| `--domains` | todos | Lista separada por vírgulas de prefixos de domínio (`02_genealogia,03_saude`) |
| `--dry-run` | desligado | Não grava o **dataset JSON** (`--json-out`); o resumo e o relatório de `--html-report` continuam sendo produzidos |
| `--validate` / `--no-validate` | validação **ligada** | Roda (ou não) os validadores |
| `--json-out` / `--output` | — | Caminho do JSON de saída |
| `--html-report` | — | Caminho do relatório HTML de validação |

## Exemplos

```bash
# dataset completo com relatório
python3 -m persona_db.scripts.generate --personas 1000 --seed 42 \
  --output dataset.json --html-report report.html

# iteração rápida em um domínio, sem escrever nada
python3 -m persona_db.scripts.generate --personas 50 --domains 03_saude --dry-run

# geração sem validação (mais rápida; use com cuidado)
python3 -m persona_db.scripts.generate --personas 5000 --seed 7 --no-validate --output big.json

# âncora temporal diferente
PERSONADB_TODAY=2032-01-01 python3 -m persona_db.scripts.generate --personas 100 --dry-run
```

## Saída

Uma única linha JSON em `stdout`:

```json
{
  "personas": 1000,
  "seed": 42,
  "batch_size": 100,
  "elapsed_seconds": 58.21,
  "tables": {"pessoa": 1000, "doenca_pessoa": 2431, "...": 0},
  "total_rows": 342118,
  "validation": {
    "passed": true,
    "violation_count": 0,
    "overall_consistency_pct": 100.0,
    "domain_consistency": {"genealogia": 100.0, "temporal": 100.0, "financas": 100.0,
                           "saude": 100.0, "juridico": 100.0, "social": 100.0}
  }
}
```

Quando a validação falha, o objeto ganha `violations_sample` (as 10 primeiras violações), o JSON
**não** é gravado e o processo retorna `1`.

```bash
python3 -m persona_db.scripts.generate --personas 200 --seed 42 --output dataset.json | jq .validation
```

## Códigos de retorno

| Código | Situação |
|---|---|
| `0` | Geração concluída e validação aprovada (ou `--no-validate`) |
| `1` | Pelo menos uma violação de consistência |

## API em Python

```python
from datetime import date
from persona_db.scripts.generate import generate_all, generate_dataset, DOMAIN_PIPELINE

dataset = generate_all(n=250, seed=42, today=date(2026, 1, 1))
dataset = generate_dataset(250, 42)              # alias

parcial = generate_all(n=50, seed=7, domains={"02_genealogia", "03_saude"})

print([nome for nome, _ in DOMAIN_PIPELINE])     # ordem topológica
```

`generate_all` devolve o dataset em memória **sem** gravar arquivos e **sem** validar — a validação
é responsabilidade do CLI (ou sua, chamando `validate_dataset`).

## Dicas de desempenho

- A validação custa tempo proporcional ao número de linhas; para lotes grandes, gere com
  `--no-validate` e valide uma amostra em separado.
- `--domains` é a forma mais rápida de iterar enquanto se escreve um gerador.
- O consumo de memória cresce linearmente com `--personas`: todo o dataset fica em dicionários
  Python até a serialização. Veja [Desempenho](../guias/desempenho.md).
