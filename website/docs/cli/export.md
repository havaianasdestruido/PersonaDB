---
title: "export — exportação de datasets"
sidebar_label: export
sidebar_position: 3
description: Exportar para CSV em tar.gz, Parquet por tabela ou um JSON por pessoa.
---

# `scripts.export`

```bash
python3 -m persona_db.scripts.export <dataset.json> --format {csv,people,parquet} --output <destino>
```

Converte o JSON produzido por [`generate`](./generate.md) em formatos portáteis.

## Formatos

| Formato | Saída | Observações |
|---|---|---|
| `csv` | um `.tar.gz` com um CSV por tabela | colunas ordenadas alfabeticamente; valores `dict`/`list` viram JSON |
| `parquet` | um diretório com um `.parquet` por tabela não vazia | requer o extra `[parquet]` (`pyarrow`) |
| `people` | um diretório com um `.json` por pessoa | agrupa todas as linhas com aquele `pessoa_id` |

```bash
python3 -m persona_db.scripts.export dataset.json --format csv     --output export/dataset.tar.gz
python3 -m persona_db.scripts.export dataset.json --format parquet --output export/parquet
python3 -m persona_db.scripts.export dataset.json --format people  --output export/pessoas
```

## Arquivo por pessoa

```json
{
  "pessoa": {"id": "…", "nome_completo": "…", "data_nascimento": "1988-04-12"},
  "doenca_pessoa": [{"id": "…", "pessoa_id": "…"}],
  "contrato_trabalho": [{"id": "…", "pessoa_id": "…"}]
}
```

Tabelas de catálogo (sem `pessoa_id`) **não** entram nesses arquivos — apenas o que pertence
àquela pessoa. É o formato ideal para alimentar APIs de perfil ou fixtures de teste.

## Sidecar de proveniência

Toda exportação grava um arquivo irmão `*.README.json`:

```json
{
  "created_at": "2026-01-01T12:00:00+00:00",
  "format": "csv",
  "row_counts": {"pessoa": 200, "doenca_pessoa": 486},
  "total_rows": 68342
}
```

## Segurança de caminho

As exportações `people` e `parquet` validam cada nome de arquivo com
`^[A-Za-z0-9][A-Za-z0-9_.-]*$` e confirmam que o caminho resolvido permanece **dentro** do
diretório de destino, impedindo *path traversal* a partir de nomes de tabela ou UUIDs manipulados.
Arquivos antigos (`*.json` / `*.parquet`) no destino são removidos antes da nova escrita, para que
o diretório reflita exatamente o dataset atual.

## API em Python

```python
import json
from pathlib import Path
from persona_db.scripts.export import export_csv, export_people, export_parquet

dataset = json.loads(Path("dataset.json").read_text(encoding="utf-8"))
export_csv(dataset, Path("export/dataset.tar.gz"))
export_people(dataset, Path("export/pessoas"))
export_parquet(dataset, Path("export/parquet"))
```

## Via Makefile

```bash
make -C persona_db export-csv
make -C persona_db export-parquet
```
