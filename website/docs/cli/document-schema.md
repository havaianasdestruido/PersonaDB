---
title: "document_schema — dicionário de dados"
sidebar_label: document_schema
sidebar_position: 6
description: Gerar docs/SCHEMA.md a partir dos DDL ou de um banco PostgreSQL ativo.
---

# `scripts.document_schema`

```bash
python3 -m persona_db.scripts.document_schema [--database-url URL] [--schema-dir DIR] [--output ARQ]
```

Gera o dicionário de dados do PersonaDB em Markdown.

| Flag | Padrão | Descrição |
|---|---|---|
| `--database-url` | `$DATABASE_URL` | Se presente, lê o catálogo **vivo** (`information_schema`) |
| `--schema-dir` | `persona_db/sql/schema` | Diretório dos arquivos DDL |
| `--output` | `persona_db/docs/SCHEMA.md` | Arquivo de saída |

## Dois modos

```bash
# a) a partir dos arquivos DDL (não precisa de banco)
python3 -m persona_db.scripts.document_schema

# b) a partir de um banco já migrado
python3 -m persona_db.scripts.document_schema \
  --database-url postgresql://persona:persona@localhost:5432/personadb \
  --output docs/SCHEMA_LIVE.md
```

| Modo | Fonte | Requer |
|---|---|---|
| DDL (padrão) | regex sobre `sql/schema/*.sql` | nada além do Python |
| Catálogo vivo | `information_schema.columns` + constraints | `psycopg2-binary` e um banco migrado |

## O que o modo DDL extrai

- tabelas (ignorando partições concretas como `transacao_2019` e `*_default`);
- colunas com tipo, nulidade, `DEFAULT`, `CHECK` e chave primária;
- chaves estrangeiras declaradas inline (`REFERENCES`) e via `ALTER TABLE … ADD CONSTRAINT`;
- comentários de tabela (`COMMENT ON TABLE … IS '…'`);
- um diagrama Mermaid `erDiagram` por domínio.

## API em Python

```python
from pathlib import Path
from persona_db.scripts.document_schema import render_from_sql_dir, render

markdown = render_from_sql_dir(Path("persona_db/sql/schema"))
Path("SCHEMA.md").write_text(markdown, encoding="utf-8")

markdown_vivo = render("postgresql://persona:persona@localhost:5432/personadb")
```

## Relação com este site

A seção [Schema SQL](../schema/index.md) **não** consome `SCHEMA.md`: ela é produzida por
`website/scripts/generate_reference.py`, que faz o próprio parsing dos DDL e acrescenta informações
que o `SCHEMA.md` não tem — índice alfabético de tabelas, ligação tabela → gerador responsável,
tipos ENUM, objetos de banco e índices declarados.

| Artefato | Gerado por | Quando atualizar |
|---|---|---|
| `persona_db/docs/SCHEMA.md` | `scripts.document_schema` | ao alterar qualquer DDL (é versionado) |
| Seção **Schema SQL** deste site | `npm run gen:docs` | automaticamente a cada build |

## Via Makefile

```bash
make -C persona_db docs-schema
```
