---
title: Adicionar um novo domínio
sidebar_label: Novo domínio
sidebar_position: 1
description: Passo a passo completo, do DDL ao teste, para criar um domínio do zero.
---

# Adicionar um novo domínio

Vamos criar um domínio fictício `42_voluntariado` com duas tabelas, do DDL até o teste.

## 1. Escrever o DDL

`persona_db/sql/schema/42_voluntariado.sql`:

```sql
-- ============================================================================
-- PersonaDB - 42_voluntariado.sql (Trabalho voluntário fictício)
-- ============================================================================

CREATE TABLE IF NOT EXISTS organizacao_voluntaria (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome          TEXT NOT NULL,
    causa         TEXT NOT NULL,
    cidade        TEXT
);
COMMENT ON TABLE organizacao_voluntaria IS
    'Catálogo de ONGs fictícias que recebem trabalho voluntário.';

CREATE TABLE IF NOT EXISTS participacao_voluntaria (
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id      UUID NOT NULL REFERENCES pessoa(id) ON DELETE CASCADE,
    organizacao_id UUID NOT NULL REFERENCES organizacao_voluntaria(id),
    data_inicio    DATE NOT NULL,
    data_fim       DATE,
    horas_mensais  INTEGER CHECK (horas_mensais BETWEEN 1 AND 200)
);
COMMENT ON TABLE participacao_voluntaria IS
    'Vínculo de uma persona com uma organização voluntária fictícia.';
```

Regras a seguir:

- `CREATE TABLE IF NOT EXISTS` (os DDL precisam ser idempotentes);
- `COMMENT ON TABLE` — o comentário aparece automaticamente na
  [documentação do schema](../schema/index.md);
- `pessoa_id` com `REFERENCES pessoa(id)` em toda tabela satélite;
- numeração do arquivo define a ordem de aplicação.

## 2. Escrever o gerador

`persona_db/generators/gen_42_voluntariado.py`:

```python
"""gen_42_voluntariado — domínio 42: trabalho voluntário fictício.

generate(personas, seed, today) -> dict[str, list[dict]]

Tabelas: organizacao_voluntaria (catálogo), participacao_voluntaria.
Enriquecimento: p["faz_voluntariado"] (bool).
"""
from __future__ import annotations

from datetime import date, timedelta
from uuid import NAMESPACE_URL, uuid5

from persona_db.engines.rng import SeededRNG, new_rng
from persona_db.generators.gen_00_pessoa import simulation_today

_ORGS = [
    ("Instituto Horizonte Fictício", "educação"),
    ("Associação Raiz Inventada", "meio ambiente"),
    ("Casa Solidária Imaginária", "assistência social"),
]


def _build_catalog(rows: dict[str, list[dict]]) -> list[str]:
    ids = []
    for nome, causa in _ORGS:
        oid = str(uuid5(NAMESPACE_URL, f"org-voluntaria-{nome}"))
        rows["organizacao_voluntaria"].append(
            {"id": oid, "nome": nome, "causa": causa, "cidade": None}
        )
        ids.append(oid)
    return ids


def _aniversario(nascimento: date, anos: int) -> date:
    """Aniversário calendárico; 29/02 cai em 28/02 nos anos não bissextos."""
    try:
        return nascimento.replace(year=nascimento.year + anos)
    except ValueError:
        return nascimento.replace(year=nascimento.year + anos, month=2, day=28)


def _probabilidade(p: dict) -> float:
    base = 0.12
    if p.get("education") in ("superior", "pos"):
        base += 0.10
    if p.get("classe_social") in ("A", "B1"):
        base += 0.05
    return min(0.5, base)


def generate(personas: list[dict], seed: int = 7, today: date | None = None) -> dict[str, list[dict]]:
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict]] = {"organizacao_voluntaria": [], "participacao_voluntaria": []}
    org_ids = _build_catalog(rows)

    for p in personas:
        rng: SeededRNG = master.fork(p["id"], "gen42-voluntariado")
        nascimento = date.fromisoformat(p["data_nascimento"])
        fim_vida = date.fromisoformat(p["data_obito"]) if p.get("data_obito") else today

        maioridade = _aniversario(nascimento, 16)   # data-limite única, reusada no validador
        p["faz_voluntariado"] = False
        if maioridade >= fim_vida or not rng.bernoulli(_probabilidade(p)):
            continue

        janela = max(1, (fim_vida - maioridade).days)
        inicio = maioridade + timedelta(days=rng.integer(0, janela))
        duracao = rng.integer(90, 1800)
        fim = min(fim_vida, inicio + timedelta(days=duracao))

        p["faz_voluntariado"] = True
        rows["participacao_voluntaria"].append({
            "id": str(uuid5(NAMESPACE_URL, f"voluntariado-{p['id']}")),
            "pessoa_id": p["id"],
            "organizacao_id": org_ids[rng.integer(0, len(org_ids) - 1)],
            "data_inicio": inicio.isoformat(),
            "data_fim": fim.isoformat() if rng.bernoulli(0.6) else None,
            "horas_mensais": rng.integer(2, 40),
        })

    return rows
```

Revise o [contrato dos geradores](../geradores/contrato.md) antes de prosseguir.

## 3. Registrar no pipeline

Em `persona_db/generators/__init__.py`, acrescente ao `__all__`. Em
`persona_db/scripts/generate.py`, importe o módulo e insira a entrada **depois** das dependências:

```diff
 from persona_db.generators import (
     gen_00_pessoa,
+    gen_42_voluntariado,
 )

 DOMAIN_PIPELINE = (
     …
     ("23_midia", gen_23_midia),
+    ("42_voluntariado", gen_42_voluntariado),
     ("16_timeline", gen_16_timeline),
 )
```

:::tip Posição importa
`gen_16_timeline` consolida eventos de todos os domínios — qualquer domínio novo deve vir **antes**
dele se quiser aparecer na linha do tempo.
:::

## 4. Acrescentar invariantes

Se o domínio tem regras próprias, estenda um validador existente ou crie
`persona_db/validators/val_voluntariado.py` seguindo a assinatura padrão e registre-o em
`run_validators.CHECKS` e `DOMAIN_VALIDATORS`.

```python
def validate_voluntariado(dataset, today=None):
    today = today or simulation_today()
    violations = []
    nascimentos = {p["id"]: date.fromisoformat(p["data_nascimento"]) for p in dataset.get("pessoa", [])}
    for row in dataset.get("participacao_voluntaria", []):
        nasc = nascimentos.get(row["pessoa_id"])
        if nasc and date.fromisoformat(row["data_inicio"]) < _aniversario(nasc, 16):
            violations.append({"domain": "voluntariado", "rule": "volunteer_min_age_16",
                               "person_id": row["pessoa_id"]})
    return violations
```

As verificações genéricas (`data_inicio <= data_fim`, datas não futuras) já são aplicadas
automaticamente a **todas** as tabelas.

## 5. Testar

`persona_db/tests/unit/test_voluntariado.py`:

```python
from persona_db.generators import gen_42_voluntariado
from persona_db.generators.gen_00_pessoa import generate_personas


def test_voluntariado_deterministico():
    personas = generate_personas(30, seed=7)
    a = gen_42_voluntariado.generate(personas, seed=7)
    b = gen_42_voluntariado.generate(personas, seed=7)
    assert a == b          # todos os valores e IDs, não só as contagens


def test_voluntariado_respeita_idade_minima():
    personas = generate_personas(50, seed=7)
    rows = gen_42_voluntariado.generate(personas, seed=7)
    nascimentos = {p["id"]: date.fromisoformat(p["data_nascimento"]) for p in personas}
    for row in rows["participacao_voluntaria"]:
        # mesmo corte usado pelo gerador e pelo validador
        assert date.fromisoformat(row["data_inicio"]) >= _aniversario(nascimentos[row["pessoa_id"]], 16)
```

## 6. Verificar de ponta a ponta

```bash
python3 -m persona_db.scripts.generate --personas 100 --seed 7 --dry-run
python3 -m pytest persona_db/tests -q
python3 -m ruff check persona_db
python3 -m persona_db.scripts.document_schema      # atualiza SCHEMA.md
cd website && npm run gen:docs                     # atualiza este site
```

O novo domínio aparece automaticamente no [catálogo de geradores](../geradores/catalogo.md) e na
seção [Schema SQL](../schema/index.md) — nenhuma edição manual de documentação é necessária.
