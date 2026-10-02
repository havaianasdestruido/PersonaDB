---
title: "bulk_insert — carga no PostgreSQL"
sidebar_label: bulk_insert
sidebar_position: 4
description: Carga em streaming do dataset JSON para o PostgreSQL com lotes controlados.
---

# `scripts.bulk_insert`

```bash
python3 -m persona_db.scripts.bulk_insert <dataset.json> --database-url <url> [--page-size N]
```

Carrega o dataset no PostgreSQL **sem** materializar o arquivo inteiro na memória.

## Flags

| Flag | Padrão | Descrição |
|---|---|---|
| `input` (posicional) | — | Caminho do JSON gerado por `scripts.generate` |
| `--database-url` | `$DATABASE_URL` | URL de conexão `postgresql://user:senha@host:porta/base` |
| `--page-size` | `1000` | Linhas por `execute_values` |

```bash
python3 -m persona_db.scripts.bulk_insert dataset.json \
  --database-url postgresql://persona:persona@localhost:5432/personadb \
  --page-size 2000
# Inserted 342118 rows
```

## Como funciona

1. **ijson** lê apenas as chaves de primeiro nível para descobrir os nomes das tabelas;
2. a lista é ordenada com `pessoa` **sempre primeiro**, garantindo que as FKs das satélites
   encontrem o hub já populado;
3. para cada tabela, as colunas são descobertas pela união das chaves das linhas;
4. as linhas são transmitidas em streaming e inseridas em lotes com
   `psycopg2.extras.execute_values`;
5. valores `dict`/`list` são serializados como JSON antes do `INSERT`.

```mermaid
flowchart LR
    A[dataset.json] -->|ijson.parse| B[nomes das tabelas]
    B --> C{pessoa primeiro}
    C --> D[descoberta de colunas]
    D --> E[ijson.items streaming]
    E --> F["execute_values (lotes de page_size)"]
    F --> G[(PostgreSQL)]
```

## Proteções

- Nomes de tabela e de coluna precisam casar com `^[a-z_][a-z0-9_]*$`; qualquer identificador fora
  do padrão levanta `ValueError` **antes** de qualquer SQL ser montado.
- Identificadores são sempre citados com aspas duplas no `INSERT`.
- Tabelas cujo nome começa com `_` são ignoradas (convenção para chaves auxiliares).
- Linhas que não sejam objetos JSON levantam `TypeError`.

## Pré-requisitos

```bash
make -C persona_db migrate        # aplica os DDL antes da carga
```

Se o schema não existir, o `INSERT` falha com `relation does not exist`. Para recarregar do zero:

```bash
make -C persona_db reset && make -C persona_db migrate
```

## API em Python

```python
from pathlib import Path
from persona_db.scripts.bulk_insert import load_dataset

total = load_dataset(
    "postgresql://persona:persona@localhost:5432/personadb",
    Path("dataset.json"),
    page_size=2000,
)
print(total, "linhas inseridas")
```

## Desempenho

| Ajuste | Efeito |
|---|---|
| `--page-size 2000–5000` | menos *round-trips*; cuidado com o uso de memória do servidor |
| Aplicar `98_indexes.sql` **depois** da carga | evita manter índices durante os `INSERT`s |
| `ANALYZE` ao final | estatísticas atualizadas para o planejador |
| Tuning de `sql/tuning/postgresql.conf.recommended` | linha de base para instâncias pequenas |
