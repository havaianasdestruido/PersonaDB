---
title: PostgreSQL com Docker Compose
sidebar_label: PostgreSQL
sidebar_position: 3
description: Subir o banco, aplicar as migrações DDL, carregar o dataset e ajustar o tuning.
---

# PostgreSQL com Docker Compose

## Subir o banco

O arquivo [`persona_db/docker-compose.yml`](https://github.com/havaianasdestruido/PersonaDB/blob/main/persona_db/docker-compose.yml)
define dois serviços:

| Serviço | Imagem | Porta | Credenciais |
|---|---|---|---|
| `db` | `postgres:16` | `5432` | usuário `persona`, senha `persona`, base `persona_db` |
| `pgadmin` | `dpage/pgadmin4` | `8080` | `admin@persona.local` / `admin` |

```bash
docker compose -f persona_db/docker-compose.yml up -d
docker compose -f persona_db/docker-compose.yml ps
```

:::caution Portas abertas em todas as interfaces
O compose publica `5432:5432` e `8080:80`, ou seja, expõe o banco (usuário/senha `persona`) e o
pgAdmin (`admin`/`admin`) em **todas** as interfaces da máquina. Em rede compartilhada, prefixe as
publicações com o loopback — `127.0.0.1:5432:5432` e `127.0.0.1:8080:80` — ou troque as
credenciais padrão.
:::

O diretório `persona_db/sql/schema` é montado em `/docker-entrypoint-initdb.d`, portanto **na
primeira inicialização do volume** o PostgreSQL já aplica todos os DDL em ordem alfabética
(`00_hub.sql` → `99_functions.sql`).

:::caution Nome da base
O `docker-compose.yml` cria a base `persona_db`, enquanto o `.env.example` e o `Makefile` apontam
para `postgresql://persona:persona@localhost:5432/personadb`. Ajuste `DATABASE_URL` (ou
`POSTGRES_DB`) para que os dois coincidam antes de rodar `migrate`/`load`.
:::

## Aplicar as migrações manualmente

Para um PostgreSQL já existente (sem Docker), aplique os arquivos em ordem:

```bash
make -C persona_db migrate DATABASE_URL=postgresql://persona:persona@localhost:5432/personadb
```

O alvo roda, para cada arquivo de `sql/schema/*.sql` em ordem alfabética:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$file"
```

Os DDL são **idempotentes** (`CREATE TABLE IF NOT EXISTS`, `CREATE OR REPLACE FUNCTION`), então
reaplicá-los é seguro.

| Arquivo | Conteúdo |
|---|---|
| `00_hub.sql` … `26_metadata.sql` | 257 tabelas, tipos ENUM e comentários |
| `98_indexes.sql` | partições de `transacao` (por ano) e `exame_resultado` (por hash), índices compostos, índice GIN trigram em nomes, `SET STATISTICS` |
| `99_functions.sql` | `calcular_idade()`, `validar_tipo_sanguineo_filho()`, triggers de auditoria/reputação e as views `v_pessoa_completa`, `v_perfil_criminal`, `v_arvore_familiar`, `mv_estatisticas_populacao` |

Consulte o catálogo completo em [Schema SQL](../schema/index.md).

## Carregar o dataset

```bash
python3 -m persona_db.scripts.bulk_insert dataset.json \
  --database-url postgresql://persona:persona@localhost:5432/personadb \
  --page-size 2000
```

O carregador usa **ijson** para percorrer o JSON em streaming (sem carregar o arquivo inteiro na
memória) e `psycopg2.extras.execute_values` em lotes. A tabela `pessoa` é sempre inserida primeiro,
para que as chaves estrangeiras das satélites sejam satisfeitas. Veja [bulk_insert](../cli/bulk-insert.md).

## Fluxo completo com `make`

```bash
cp persona_db/.env.example .env
docker compose -f persona_db/docker-compose.yml up -d
make -C persona_db migrate
make -C persona_db generate N_PESSOAS=1000 SEED=42
make -C persona_db load
make -C persona_db validate
make -C persona_db export-csv
make -C persona_db export-parquet
```

Para recomeçar do zero:

```bash
make -C persona_db reset   # DROP SCHEMA public CASCADE; CREATE SCHEMA public;
make -C persona_db migrate
```

## Tuning recomendado

O arquivo `persona_db/sql/tuning/postgresql.conf.recommended` traz uma linha de base para uma
instância pequena e dedicada:

```ini
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
```

Para cargas grandes (≥ 1 milhão de linhas), vale ainda:

- aplicar **antes** da carga a parte de `98_indexes.sql` que cria as **partições** de `transacao`
  (intervalos anuais + `DEFAULT`) e de `exame_resultado` (4 partições por hash) — sem elas o
  `INSERT` nessas tabelas particionadas falha; só os **índices opcionais** (BTREE/GIN) valem a pena
  criar depois da carga, para acelerar os `INSERT`s;
- executar `ANALYZE` ao final da carga;
- aumentar `maintenance_work_mem` temporariamente durante a criação dos índices.
