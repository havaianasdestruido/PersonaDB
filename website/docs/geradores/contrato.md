---
title: Contrato dos geradores
sidebar_label: Contrato
sidebar_position: 2
description: Assinatura obrigatória, convenções de ID, cronologia e checklist de revisão.
---

# Contrato dos geradores

## Assinatura

```python
from datetime import date

def generate(
    personas: list[dict],
    seed: int = 7,
    today: date | None = None,
) -> dict[str, list[dict]]:
    """Gera todas as tabelas do domínio XX."""
```

Quatro geradores recebem um parâmetro extra com o dataset parcial já construído:

```python
def generate(
    personas: list[dict],
    seed: int = 7,
    today: date | None = None,
    existing_tables: dict[str, list[dict]] | None = None,
) -> dict[str, list[dict]]:
```

| Gerador | Por que precisa do dataset parcial |
|---|---|
| `gen_07_residencia` | reaproveita endereços e imóveis já criados em finanças |
| `gen_11_juridico` | associa processos a contratos, imóveis e veículos existentes |
| `gen_13_viagens` | monta companhias de viagem a partir de vínculos sociais |
| `gen_16_timeline` | consolida eventos de **todos** os domínios anteriores |

## Esqueleto mínimo

```python
"""gen_42_exemplo — domínio 42: descrição curta do domínio.

generate(personas, seed, today) -> dict[str, list[dict]]

Tabelas: exemplo_evento, exemplo_item.
"""
from __future__ import annotations

from datetime import date, timedelta
from uuid import NAMESPACE_URL, uuid5

from persona_db.engines.rng import new_rng
from persona_db.generators.gen_00_pessoa import simulation_today


def generate(personas: list[dict], seed: int = 7, today: date | None = None) -> dict[str, list[dict]]:
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict]] = {"exemplo_evento": [], "exemplo_item": []}

    for p in personas:
        rng = master.fork(p["id"], "gen42-exemplo")
        nascimento = date.fromisoformat(p["data_nascimento"])
        fim = date.fromisoformat(p["data_obito"]) if p.get("data_obito") else today

        if not rng.bernoulli(0.35):
            continue

        dias = max(1, (fim - nascimento).days)
        quando = nascimento + timedelta(days=rng.integer(1, dias))

        rows["exemplo_evento"].append({
            "id": str(uuid5(NAMESPACE_URL, f"exemplo-evento-{p['id']}")),
            "pessoa_id": p["id"],
            "data": quando.isoformat(),
            "tipo": str(rng.choice(["alfa", "beta"], weights=[0.7, 0.3])),
        })

    return rows
```

## Convenções obrigatórias

### Identificadores

```python
str(uuid5(NAMESPACE_URL, f"<prefixo>-{pessoa_id}-{indice}"))
```

A chave precisa ser **estável e única**: incluir o `pessoa_id` e um discriminador (índice,
ano, nome do catálogo). Nunca use `uuid4()`.

### Datas

- Sempre `str` em ISO-8601 (`date.isoformat()`).
- O intervalo válido de qualquer evento é `[data_nascimento, min(data_obito, today)]`.
- Datas de início e fim: `data_inicio <= data_fim` (o validador temporal checa os pares
  `data_inicio`/`data_fim` e `data_entrada`/`data_saida` em **todas** as tabelas).

### Aleatoriedade

- Um `fork` por persona e por domínio; use `salt` para subprocessos (`"gen03-impact"`).
- Nunca compartilhe o mesmo `rng` entre personas.
- Nunca reordene chamadas existentes ao RNG sem assumir que o dataset mudará.

### Colunas

As chaves de cada linha devem existir no DDL do domínio. Chaves desconhecidas quebram
`bulk_insert` (que monta o `INSERT` a partir da união das chaves) e passam despercebidas na
validação em memória.

## Enriquecimento da persona

```python
p["tem_doenca_grave"] = has_grave
p["impactos_saude"] = HealthEngine.chronic_impact(impact_rng, has_chronic)
```

Documente na docstring do módulo quais campos você acrescenta — é o que permite ao próximo
gerador depender deles com segurança.

## Checklist de revisão

- [ ] Docstring do módulo lista o domínio, as tabelas e os campos de enriquecimento.
- [ ] `today = today or simulation_today()` na primeira linha.
- [ ] Nenhum uso de `random`, `np.random`, `uuid4` ou `date.today()`.
- [ ] Todos os `pessoa_id` referenciam personas existentes.
- [ ] Nenhum evento fora de `[nascimento, óbito/hoje]`.
- [ ] Pessoas falecidas não recebem eventos posteriores ao óbito.
- [ ] Linhas usam apenas colunas presentes no DDL.
- [ ] O gerador foi registrado em `DOMAIN_PIPELINE` **depois** de suas dependências.
- [ ] Há testes em `persona_db/tests/` cobrindo o novo domínio.
- [ ] `python3 -m persona_db.scripts.generate --personas 100 --seed 7` continua passando.

## Erros comuns

| Sintoma | Causa provável |
|---|---|
| `end_before_start` na validação temporal | `data_fim` calculada sem garantir `>= data_inicio` |
| `event_after_death` | laço não respeita `data_obito` |
| Violação de FK no `bulk_insert` | catálogo referenciado não foi incluído no `rows` retornado |
| Dataset muda entre execuções | `uuid4()`, `date.today()` ou ordenação por `set` |
| Tabela some do dataset | o gerador devolveu a chave com lista vazia e outro gerador a sobrescreveu — use nomes de tabela exclusivos por domínio |
