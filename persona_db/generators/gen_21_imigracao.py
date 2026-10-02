"""gen_21_imigracao — domínio 21: vistos, naturalizações, residências permanentes e travessias.

Implementa a seção de Imigração & Documentos de TASK-053 em TODO.MD:
- Emissão de vistos e travessias de fronteira correlacionadas com nacionalidade,
  classe socioeconômica e histórico de viagens.
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

_PAISES = [
    "Portugal Fictício",
    "Argentina Fictícia",
    "Estados Unidos Fictícios",
    "Espanha Simulada",
    "Itália Virtual",
]

_FRONTEIRAS = [
    "Aeroporto Internacional de Alvorada Leste",
    "Fronteira Terrestre Sul Simulada",
    "Porto Marítimo de Porto Azul",
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
    """Gera todas as tabelas do domínio 21 (Imigração & Documentos)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "documento_identidade": [],
        "visto_ficticio": [],
        "naturalizacao_ficticia": [],
        "residencia_permanente_ficticia": [],
        "deportacao_ficticia": [],
        "fronteira_travessia_ficticia": [],
    }

    for p in personas:
        rng = master.fork(p["id"], "gen21-imigracao")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)
        if age < 18:
            continue

        nac = p.get("nacionalidade", "brasileira")
        cls = p["classe_social"]
        ev_dt = max(born + timedelta(days=18 * 365), end - timedelta(days=rng.integer(90, 1800)))
        ev_dt = min(ev_dt, end)

        if nac in ("estrangeiro", "naturalizado"):
            pais_orig = str(rng.choice(_PAISES))
            rows["documento_identidade"].append({
                "id": str(uuid5(NAMESPACE_URL, f"docid-ext-{p['id']}")),
                "pessoa_id": p["id"],
                "tipo": "RNM / Cédula Estrangeira Fictícia",
                "pais_emissor_ficticio": pais_orig,
                "validade": (end + timedelta(days=1825)).isoformat(),
            })
            if nac == "naturalizado":
                rows["naturalizacao_ficticia"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"nat-{p['id']}")),
                    "pessoa_id": p["id"],
                    "pais_origem": pais_orig,
                    "pais_destino": "Brasil Fictício",
                    "data": ev_dt.isoformat(),
                })
            else:
                rows["residencia_permanente_ficticia"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"resperm-{p['id']}")),
                    "pessoa_id": p["id"],
                    "pais": "Brasil Fictício",
                    "data_concessao": ev_dt.isoformat(),
                })

        if cls in ("A", "B1", "B2") and rng.bernoulli(0.32):
            pais_dest = str(rng.choice(_PAISES))
            rows["visto_ficticio"].append({
                "id": str(uuid5(NAMESPACE_URL, f"visto-{p['id']}")),
                "pessoa_id": p["id"],
                "pais_destino_ficticio": pais_dest,
                "tipo": str(rng.choice(["turismo", "trabalho", "estudo"], weights=[0.70, 0.20, 0.10])),
                "validade": (end + timedelta(days=1825)).isoformat(),
            })
            rows["fronteira_travessia_ficticia"].append({
                "id": str(uuid5(NAMESPACE_URL, f"front-{p['id']}")),
                "pessoa_id": p["id"],
                "ponto_fronteira": str(rng.choice(_FRONTEIRAS)),
                "data": ev_dt.isoformat(),
                "direcao": "saida",
            })

        if rng.bernoulli(0.01):
            rows["deportacao_ficticia"].append({
                "id": str(uuid5(NAMESPACE_URL, f"deport-{p['id']}")),
                "pessoa_id": p["id"],
                "pais": str(rng.choice(_PAISES)),
                "data": ev_dt.isoformat(),
                "motivo": "expiração de prazo de permanência turística",
            })

    return rows
