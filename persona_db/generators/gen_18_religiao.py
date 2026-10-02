"""gen_18_religiao — domínio 18: crenças, instituições religiosas, rituais, conversões e dízimos.

Implementa a seção de Religião & Crenças de TASK-053 em TODO.MD:
- Distribuição religiosa brasileira calibrada: Católica (~45%), Evangélica (~31%),
  Sem religião (~14%), Espírita (~4%), Matriz Africana (~3%), Outras (~3%).
- Enriquece a persona com `religiao` e `religiosidade_alta` para consumo em
  relacionamentos (`gen_08_relacionamentos`) e comportamento eleitoral (`gen_12_eleitoral`).
"""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from typing import Any
from uuid import NAMESPACE_URL, uuid5

try:  # pragma: no cover
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today

# ---------------------------------------------------------------------------
# Distribuição religiosa brasileira calibrada (TASK-053)
# ---------------------------------------------------------------------------
_CRENCAS_CATALOGO = [
    ("Católica Apostólica Fictícia", 7.2, 0.45),
    ("Evangélica Pentecostal Simulada", 8.4, 0.31),
    ("Sem Religião / Secular", 2.0, 0.14),
    ("Espírita Kardecista Virtual", 7.0, 0.04),
    ("Religião de Matriz Africana Simulada", 7.8, 0.03),
    ("Outras Tradições Espirituais", 6.5, 0.03),
]

_INSTITUICOES = [
    "Paróquia Matriz de Alvorada Fictícia",
    "Comunidade Cristã Esperança Simulada",
    "Centro Espírita Luz do Caminho Virtual",
    "Templo Tradicional Raízes Inventadas",
]


def _birth(p: dict[str, Any]) -> date:
    return date.fromisoformat(p["data_nascimento"])


def _end_date(p: dict[str, Any], today: date) -> date:
    if p.get("data_obito"):
        return min(today, date.fromisoformat(p["data_obito"]))
    return today


def generate(
    personas: list[dict[str, Any]],
    seed: int = 7,
    today: date | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Gera todas as tabelas do domínio 18 (Religião & Crenças)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "crenca": [],
        "instituicao_religiosa": [],
        "participacao_religiosa": [],
        "ritual_ficticio": [],
        "conversao_religiosa": [],
        "dizimo_ficticio": [],
    }

    crencas: list[dict[str, Any]] = []
    weights: list[float] = []
    for nome, intens, w in _CRENCAS_CATALOGO:
        cid = str(uuid5(NAMESPACE_URL, f"crenca-{nome}"))
        rec = {"id": cid, "nome_ficticio": nome, "intensidade": intens}
        rows["crenca"].append(rec)
        crencas.append(rec)
        weights.append(w)

    instituicoes: list[dict[str, Any]] = []
    for nome in _INSTITUICOES:
        iid = str(uuid5(NAMESPACE_URL, f"instrel-{nome}"))
        rec = {"id": iid, "nome": nome, "endereco_id": None}
        rows["instituicao_religiosa"].append(rec)
        instituicoes.append(rec)

    for p in personas:
        rng = master.fork(p["id"], "gen18-religiao")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)

        chosen = rng.choice(crencas, weights=weights)
        p["religiao"] = chosen["nome_ficticio"]
        p["religiosidade_alta"] = float(chosen["intensidade"]) >= 7.5 and rng.bernoulli(0.55)

        if "Sem Religião" in chosen["nome_ficticio"]:
            continue

        inst = rng.choice(instituicoes)
        freq = str(rng.choice(["semanal", "mensal", "esporádica"], weights=[0.40, 0.35, 0.25]))
        rows["participacao_religiosa"].append({
            "id": str(uuid5(NAMESPACE_URL, f"partrel-{p['id']}")),
            "pessoa_id": p["id"],
            "instituicao_id": inst["id"],
            "frequencia": freq,
            "papel": "fiel" if not p["religiosidade_alta"] else "voluntário",
        })

        rit_dt = min(end, born + timedelta(days=365))
        rows["ritual_ficticio"].append({
            "id": str(uuid5(NAMESPACE_URL, f"ritual-{p['id']}")),
            "pessoa_id": p["id"],
            "nome": "Batismo / Apresentação Comunitária",
            "data": rit_dt.isoformat(),
        })

        if age >= 20 and rng.bernoulli(0.12):
            prev_crenca = crencas[0] if chosen["id"] != crencas[0]["id"] else crencas[1]
            conv_dt = min(end, born + timedelta(days=20 * 365))
            rows["conversao_religiosa"].append({
                "id": str(uuid5(NAMESPACE_URL, f"convrel-{p['id']}")),
                "pessoa_id": p["id"],
                "crenca_anterior_id": prev_crenca["id"],
                "crenca_nova_id": chosen["id"],
                "data": conv_dt.isoformat(),
            })

        if age >= 18 and freq == "semanal" and rng.bernoulli(0.45):
            sal = float(p.get("salario_mensal") or 1500.0)
            rows["dizimo_ficticio"].append({
                "id": str(uuid5(NAMESPACE_URL, f"dizimo-{p['id']}")),
                "pessoa_id": p["id"],
                "instituicao_id": inst["id"],
                "valor": round(max(30.0, sal * 0.08), 2),
                "periodicidade": "mensal",
            })

    return rows
