---
title: Primeiro dataset
sidebar_label: Primeiro dataset
sidebar_position: 2
description: Gerar, validar, inspecionar e exportar um dataset sintético do zero.
---

# Gerando o primeiro dataset

## 1. Gerar

```bash
python3 -m persona_db.scripts.generate \
  --personas 200 \
  --seed 42 \
  --output dataset.json \
  --html-report report.html
```

O orquestrador:

1. cria 200 personas base com `gen_00_pessoa`;
2. executa os 23 geradores de domínio restantes na ordem topológica de `DOMAIN_PIPELINE`;
3. deriva as tabelas de junção N:N (domínio 25);
4. preenche metadados, auditoria e proveniência (domínios 24 e 26);
5. roda os validadores e grava `report.html`;
6. escreve `dataset.json` apenas se a validação passar.

Saída típica (resumida):

```json
{
  "personas": 200,
  "seed": 42,
  "elapsed_seconds": 11.87,
  "total_rows": 68342,
  "validation": {"passed": true, "violation_count": 0, "overall_consistency_pct": 100.0,
                 "domain_consistency": {"genealogia": 100.0, "temporal": 100.0, "financas": 100.0,
                                        "saude": 100.0, "juridico": 100.0, "social": 100.0}}
}
```

:::warning Código de saída
Se qualquer validador encontrar violações, o comando imprime uma amostra em `violations_sample`,
**não grava o JSON** e retorna `exit 1`. Isso torna o comando seguro em pipelines de CI.
:::

## 2. Conferir o determinismo

```bash
python3 -m persona_db.scripts.generate --personas 50 --seed 7 --output a.json
python3 -m persona_db.scripts.generate --personas 50 --seed 7 --output b.json
sha256sum a.json b.json   # hashes idênticos
```

Trocar a semente muda todo o dataset; manter a semente e aumentar `--personas` mantém as personas
anteriores estáveis apenas quando a ordem de forking não é afetada — veja
[Determinismo](../arquitetura/determinismo.md) para as garantias exatas.

## 3. Inspecionar o JSON

O arquivo é um objeto `{"nome_da_tabela": [linha, ...]}`:

```bash
python3 - <<'PY'
import json
ds = json.load(open("dataset.json"))
print(len(ds), "tabelas")
for t in sorted(ds, key=lambda t: -len(ds[t]))[:10]:
    print(f"{t:>28}: {len(ds[t]):>7} linhas")
print(json.dumps(ds["pessoa"][0], indent=2, ensure_ascii=False)[:600])
PY
```

## 4. Validar separadamente

```bash
python3 -m persona_db.validators.run_validators --personas 200 --seed 42 --html-out report.html
```

Esse CLI regenera o dataset com a mesma semente e aplica apenas a camada de validação — útil para
depurar regras sem gravar o dataset em disco (o único arquivo escrito é o relatório indicado por
`--html-out`). Veja [Validadores](../validadores/index.md).

## 5. Exportar

```bash
# um CSV por tabela, dentro de um tar.gz
python3 -m persona_db.scripts.export dataset.json --format csv --output dataset-csv.tar.gz

# um arquivo Parquet por tabela (requer o extra [parquet])
python3 -m persona_db.scripts.export dataset.json --format parquet --output dataset-parquet

# um JSON completo por pessoa (todas as linhas com aquele pessoa_id)
python3 -m persona_db.scripts.export dataset.json --format people --output pessoas/
```

Cada exportação grava também um *sidecar* `*.README.json` com data de criação, formato e contagem de
linhas por tabela. Detalhes em [export](../cli/export.md).

## 6. Carregar no PostgreSQL

```bash
docker compose -f persona_db/docker-compose.yml up -d
make -C persona_db migrate
python3 -m persona_db.scripts.bulk_insert dataset.json \
  --database-url postgresql://persona:persona@localhost:5432/personadb
```

Veja o passo a passo completo em [PostgreSQL](./postgresql.md) e as consultas de exemplo em
[Consultas SQL úteis](../guias/consultas-sql.md).

## Escolhendo o tamanho

| `--personas` | Linhas aproximadas | Uso típico |
|---|---|---|
| 25–100 | 8 mil – 35 mil | testes rápidos, depuração de regras |
| 200–1 000 | 70 mil – 350 mil | demonstrações, testes de integração |
| 10 000 | ~3,5 milhões | benchmark, carga realista (padrão do `Makefile`) |

Use `--domains` para gerar apenas parte do schema enquanto desenvolve:

```bash
python3 -m persona_db.scripts.generate --personas 100 --domains 02_genealogia,03_saude --dry-run
```
