---
title: Makefile
sidebar_label: Makefile
sidebar_position: 7
description: Todos os atalhos de automação do projeto.
---

# Makefile

O arquivo [`persona_db/Makefile`](https://github.com/havaianasdestruido/PersonaDB/blob/main/persona_db/Makefile)
embrulha os comandos mais usados. Rode-os a partir da raiz do repositório com `-C persona_db`.

## Variáveis

| Variável | Padrão | Uso |
|---|---|---|
| `PYTHON` | `python3` | Interpretador |
| `PYTHONPATH` | `..` | Torna `persona_db` importável sem instalar |
| `DATABASE_URL` | `postgresql://persona:persona@localhost:5432/personadb` | Conexão |
| `SCHEMA` | `sql/schema/*.sql` ordenados | Arquivos aplicados pelo `migrate` |
| `N_PESSOAS` | `10000` (`100` em `validate`) | Tamanho da população |
| `SEED` | `7` | Semente |

```bash
make -C persona_db generate N_PESSOAS=500 SEED=42
make -C persona_db migrate DATABASE_URL=postgresql://u:p@host:5432/base
```

## Alvos

| Alvo | O que faz |
|---|---|
| `setup` | `pip install -e '.[dev,parquet]'` |
| `migrate` | Aplica cada `sql/schema/*.sql` com `psql -v ON_ERROR_STOP=1` |
| `generate` | `scripts.generate --people $N_PESSOAS --seed $SEED --output dataset.json` |
| `validate` | `validators.run_validators --personas $N_PESSOAS --seed $SEED` |
| `benchmark` | `scripts.benchmark --people $N_PESSOAS --seed $SEED` |
| `load` | `scripts.bulk_insert dataset.json --database-url $DATABASE_URL` |
| `export-csv` | Exporta `dataset-csv.tar.gz` |
| `export-parquet` | Exporta o diretório `dataset-parquet` |
| `docs-schema` | Regenera `docs/SCHEMA.md` |
| `reset` | `DROP SCHEMA public CASCADE; CREATE SCHEMA public;` |
| `test` | `python -m pytest` |

## Receita completa

```bash
cp persona_db/.env.example .env
docker compose -f persona_db/docker-compose.yml up -d

# O compose cria a base persona_db; o padrão do Makefile aponta para personadb.
export DATABASE_URL=postgresql://persona:persona@localhost:5432/persona_db

make -C persona_db setup
make -C persona_db migrate DATABASE_URL="$DATABASE_URL"
make -C persona_db generate N_PESSOAS=1000 SEED=42
make -C persona_db validate N_PESSOAS=1000 SEED=42
make -C persona_db load DATABASE_URL="$DATABASE_URL"
make -C persona_db export-csv
make -C persona_db export-parquet
```

:::caution Nome da base
Use o mesmo nome nos dois lados: ou exporte `DATABASE_URL` com `persona_db` (como acima), ou mude
`POSTGRES_DB` no `docker-compose.yml` para `personadb`. Veja
[PostgreSQL com Docker Compose](../comecando/postgresql.md).
:::

:::danger `make reset` apaga tudo
O alvo derruba o schema `public` inteiro do banco apontado por `DATABASE_URL`. Confirme a URL antes
de rodar.
:::

:::note Sem instalar o pacote
Todos os alvos exportam `PYTHONPATH=..`, então funcionam em um clone recém-baixado, desde que as
dependências (`numpy`, `scipy`, `pandas`, …) estejam disponíveis no ambiente.
:::
