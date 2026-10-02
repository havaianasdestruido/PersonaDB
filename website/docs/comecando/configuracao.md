---
title: Configuração
sidebar_label: Configuração
sidebar_position: 4
description: Variáveis de ambiente, âncora temporal e parâmetros do Makefile.
---

# Configuração

O PersonaDB tem pouquíssima configuração global — por desenho, quase tudo é parâmetro explícito de
função ou flag de CLI. O que existe está em [`persona_db/.env.example`](https://github.com/havaianasdestruido/PersonaDB/blob/main/persona_db/.env.example):

```ini
DATABASE_URL=postgresql://persona:persona@localhost:5432/personadb
SEED=7
N_PESSOAS=10000
PERSONADB_TODAY=2026-01-01
```

## Variáveis de ambiente

| Variável | Lida por | Padrão | Efeito |
|---|---|---|---|
| `DATABASE_URL` | `bulk_insert`, `document_schema`, `Makefile` | — | Conexão PostgreSQL usada na carga, no `migrate` e na documentação a partir do catálogo vivo |
| `PERSONADB_TODAY` | `persona_db.generators.gen_00_pessoa.simulation_today()` | `2026-01-01` | **Âncora temporal** de toda a simulação |
| `SEED` | `Makefile` | `7` | Semente mestre repassada aos alvos `generate`, `validate` e `benchmark` |
| `N_PESSOAS` | `Makefile` | `10000` (`100` em `validate`) | Quantidade de personas dos alvos do `Makefile` |
| `PYTHONPATH` | `Makefile` | `..` | Garante que `persona_db` seja importável sem instalação |

## A âncora temporal

```python
DEFAULT_TODAY = date(2026, 1, 1)

def simulation_today() -> date:
    raw = os.environ.get("PERSONADB_TODAY")
    if raw:
        return date.fromisoformat(raw)
    return DEFAULT_TODAY
```

Nenhum gerador chama `date.today()`. Todas as idades, validades de documentos, datas de contrato,
diagnósticos e óbitos são calculadas em relação a essa âncora. Consequências práticas:

- O dataset gerado hoje e daqui a um ano são **idênticos** para a mesma semente.
- Mudar `PERSONADB_TODAY` reposiciona toda a linha do tempo (as pessoas "envelhecem").
- Os validadores usam a mesma âncora, então regras do tipo "data não pode estar no futuro" são
  estáveis.

```bash
PERSONADB_TODAY=2030-06-30 python3 -m persona_db.scripts.generate --personas 50 --seed 7 --dry-run
```

:::tip Use ISO-8601
O valor é lido com `date.fromisoformat`, portanto precisa estar no formato `AAAA-MM-DD`. Um valor
inválido levanta `ValueError` logo no início da geração.
:::

## Parâmetros por linha de comando

Qualquer parâmetro relevante também existe como flag, e a flag **vence** sobre o ambiente:

| Parâmetro | Flag | CLIs |
|---|---|---|
| Nº de personas | `--personas` / `--people` | `generate` (os dois nomes) |
| Nº de personas | `--personas` | `run_validators` |
| Nº de personas | `--people` | `benchmark` |
| Semente | `--seed` | `generate`, `run_validators`, `benchmark` |
| Subconjunto de domínios | `--domains` | `generate` |
| Saída JSON | `--json-out` / `--output` | `generate` (os dois nomes) |
| Relatório HTML | `--html-report` | `generate` |
| Relatório HTML | `--html-out` | `run_validators` |
| Conexão | `--database-url` | `bulk_insert`, `document_schema` |
| Tamanho do lote de `INSERT` | `--page-size` | `bulk_insert` |

## Arquivos gerados em disco

| Caminho | Origem | Versionado? |
|---|---|---|
| `dataset.json` | `scripts.generate --output` | não |
| `report.html` | `--html-report` | não |
| `persona_db/data/rng_log.jsonl` | `engines.rng.register_seed()` | não (criado sob demanda, falhas de escrita são ignoradas) |
| `persona_db/docs/SCHEMA.md` | `scripts.document_schema` | sim |
| `website/docs/referencia-api/`, `website/docs/schema/` | `npm run gen:docs` | não (derivado do código) |
