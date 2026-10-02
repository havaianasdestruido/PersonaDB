---
title: Instalação
sidebar_label: Instalação
sidebar_position: 1
description: Requisitos, instalação do pacote persona-db e extras opcionais.
---

# Instalação

## Requisitos

| Componente | Versão | Obrigatório? |
|---|---|---|
| Python | ≥ 3.10 (CI usa 3.12) | sim |
| PostgreSQL | 16 | apenas para carga no banco |
| Docker + Docker Compose | recente | opcional (sobe o PostgreSQL + pgAdmin) |
| `make` | GNU Make | opcional (atalhos do `Makefile`) |
| Node.js | ≥ 20 | apenas para construir este site |

## Clonar e instalar

```bash
git clone https://github.com/havaianasdestruido/PersonaDB.git
cd PersonaDB
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -e "persona_db[dev,parquet]"
```

O pacote é declarado em `persona_db/pyproject.toml` com `package-dir = {"" = ".."}`, ou seja, a
instalação editável expõe o pacote `persona_db` a partir da raiz do repositório. Depois da
instalação, todos os comandos funcionam via `python3 -m persona_db.<módulo>`.

### Grupos de dependências

| Grupo | Conteúdo | Quando instalar |
|---|---|---|
| (padrão) | `numpy`, `scipy`, `pandas`, `sqlalchemy`, `psycopg2-binary`, `pydantic`, `faker[pt_BR]`, `networkx`, `rich`, `tqdm`, `ijson` | sempre |
| `parquet` | `pyarrow` | para `--format parquet` no exportador |
| `dev` | `pytest`, `pytest-cov`, `ruff`, `black`, `mypy`, `snakeviz` | para desenvolver e rodar a suíte |

```bash
# instalação mínima (apenas gerar e exportar CSV/JSON)
python3 -m pip install -e persona_db

# instalação completa
python3 -m pip install -e "persona_db[dev,parquet]"
```

## Alternativa: `make setup`

```bash
make -C persona_db setup
```

O alvo `setup` executa exatamente `pip install -e '.[dev,parquet]'` com o `PYTHONPATH` ajustado para
a raiz do repositório. Veja todos os atalhos em [Makefile](../cli/makefile.md).

## Verificar a instalação

```bash
# 1. gerar 25 personas em memória sem persistir nada
python3 -m persona_db.scripts.generate --personas 25 --seed 42 --dry-run

# 2. rodar a suíte de testes
python3 -m pytest persona_db/tests -q

# 3. checar o lint usado na CI
python3 -m ruff check persona_db
```

A saída do passo 1 é um JSON com a contagem de linhas por tabela, o tempo decorrido e o resumo de
validação:

```json
{"personas": 25, "seed": 42, "elapsed_seconds": 1.42, "total_rows": 8421,
 "validation": {"passed": true, "violation_count": 0, "overall_consistency_pct": 100.0}}
```

:::tip Sem PostgreSQL
A geração, a validação e a exportação para CSV/JSON/Parquet funcionam **inteiramente em memória**.
O PostgreSQL só é necessário para a carga em lote (`bulk_insert`) e para consultas SQL.
:::

## Próximos passos

- [Gerar o primeiro dataset](./primeiro-dataset.md)
- [Subir o PostgreSQL com Docker Compose](./postgresql.md)
- [Variáveis de ambiente e configuração](./configuracao.md)
