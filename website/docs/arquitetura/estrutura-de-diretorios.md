---
title: Estrutura de diretórios
sidebar_label: Estrutura de diretórios
sidebar_position: 5
description: Mapa do repositório, arquivo por arquivo.
---

# Estrutura de diretórios

```text
PersonaDB/
├── README.MD                      # visão geral e quick start
├── PERSONA.MD                     # especificação conceitual das ~256 entidades
├── TODO.MD                        # backlog detalhado por tarefa (TASK-xxx)
├── rewrite.MD                     # análise hipotética de performance (não implementada)
├── LICENSE                        # MIT
├── .github/workflows/
│   ├── ci.yml                     # pytest + ruff a cada push/PR
│   ├── jekyll-gh-pages.yml        # publicação legada (Jekyll)
│   └── docs.yml                   # build e deploy deste site
├── _coordination/                 # artefatos de coordenação multiagente
│   ├── AGENT_BRIEFS.md
│   ├── agent_status.json
│   ├── status.py
│   └── shared/FILESYNC.md
├── persona_db/                    # o pacote Python
│   ├── pyproject.toml             # metadados, deps, ruff e pytest
│   ├── Makefile                   # atalhos de setup/migrate/generate/load/export
│   ├── docker-compose.yml         # PostgreSQL 16 + pgAdmin
│   ├── .env.example               # DATABASE_URL, SEED, N_PESSOAS, PERSONADB_TODAY
│   ├── docs/
│   │   ├── SCHEMA.md              # dicionário de dados gerado por document_schema.py
│   │   └── MATH_MODELS.md         # formulação matemática dos motores
│   ├── engines/                   # 7 motores + constantes e bootstrap
│   ├── generators/                # gen_00_pessoa … gen_23_midia
│   ├── validators/                # 6 validadores + runner
│   ├── scripts/                   # CLIs
│   ├── seeds/                     # catálogos e tabelas de probabilidade
│   ├── sql/
│   │   ├── schema/                # 00_hub.sql … 99_functions.sql
│   │   └── tuning/postgresql.conf.recommended
│   └── tests/
│       ├── unit/                  # motores, validadores, exportação
│       ├── integration/           # pipeline completo, 25 domínios
│       └── statistical/           # distribuições com N grande
└── website/                       # este site (Docusaurus)
    ├── docs/                      # conteúdo escrito à mão + gerado
    ├── scripts/generate_reference.py
    ├── src/                       # página inicial, CSS, dados
    └── docusaurus.config.ts
```

## Pacote `persona_db`

| Diretório | Módulos | Papel |
|---|---|---|
| `engines/` | `rng`, `socio`, `genetics`, `health`, `family`, `geography`, `criminal`, `constants`, `root` | Modelos matemáticos puros, sem conhecimento do schema |
| `generators/` | `gen_00_pessoa` … `gen_23_midia` | Tradução dos modelos para linhas de tabela |
| `validators/` | `val_genealogia`, `val_temporal`, `val_financas`, `val_saude`, `val_juridico`, `val_social`, `run_validators` | Invariantes e relatório |
| `scripts/` | `generate`, `bulk_insert`, `export`, `benchmark`, `document_schema` | Interfaces de linha de comando |
| `seeds/` | `lookup_data`, `probability_tables` | Catálogos fechados e distribuições |
| `sql/schema/` | 29 arquivos `.sql` | DDL, índices, partições, funções, views |
| `tests/` | `unit/`, `integration/`, `statistical/` | Suíte executada na CI |

Dois módulos de `engines/` são infraestrutura, não modelos:

- **`constants.py`** — âncoras compartilhadas (`SOCIAL_CLASS_DIST`, `BLOOD_GROUP_PRIORS`,
  `DISEASE_TRANCHES`, `RISK_LOGLIT`). É o ponto único de calibração cruzada entre motores.
- **`root.py`** — bootstrap de `sys.path` e utilitários de hashing/status usados pela coordenação
  multiagente.

## Diretório `_coordination/`

O projeto foi construído por múltiplos agentes trabalhando em paralelo; `AGENT_BRIEFS.md`,
`agent_status.json` e `status.py` registram a divisão de responsabilidades (quem é dono de qual
arquivo) e o estado de conclusão. Isso explica as linhas "Ownership: Agent N" nas docstrings dos
motores: elas sinalizam o módulo responsável por aquela calibração.

## Arquivos de documentação na raiz

| Arquivo | Conteúdo | Status |
|---|---|---|
| `README.MD` | visão geral, quick start, consultas SQL de exemplo | atual |
| `PERSONA.MD` | especificação conceitual: todas as entidades e seus campos, domínio a domínio | referência de modelagem |
| `TODO.MD` | backlog por tarefa (`TASK-001` …), com critérios de aceite | histórico/planejamento |
| `rewrite.MD` | estudo de performance (GraalPy, PyPy, Cython, vetorização) | **não implementado** — ver [Desempenho](../guias/desempenho.md) |

## O que não é versionado

`.gitignore` exclui caches do Python (`__pycache__/`, `.pytest_cache/`, `.ruff_cache/`),
ambientes virtuais, artefatos de IDE e logs. Deste site, são ignorados `node_modules/`, `build/`,
`.docusaurus/` e as páginas geradas (`docs/referencia-api/`, `docs/schema/`,
`docs/geradores/catalogo.md`, `docs/validadores/regras.md`). Datasets gerados (`dataset.json`,
exportações) também ficam fora do controle de versão.
