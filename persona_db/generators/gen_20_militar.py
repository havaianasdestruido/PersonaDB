"""gen_20_militar — domínio 20: alistamento militar obrigatório, incorporação, patentes e baixas.

Implementa a seção Militar de TASK-053 em TODO.MD:
- Alistamento obrigatório exclusivamente para homens que atingiram 18 anos.
- Probabilidade de incorporação `P(incorporado | homem_18_anos) = 0.12`.
- Geração de `servico_militar`, `patente`, `baixa_militar` e `condecoracao_ficticia`.
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
# Constante de incorporação militar (TASK-053)
# ---------------------------------------------------------------------------
INCORPORATION_PROB_MALE_18 = 0.12

_UNIDADES = [
    ("1º Batalhão de Infantaria Fictício", "Alvorada Leste"),
    ("2º Grupo de Artilharia Simulado", "Porto Azul"),
    ("Base Aérea Regional Virtual", "Nova Serena"),
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
    """Gera todas as tabelas do domínio 20 (Militar & Serviço)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "unidade_militar": [],
        "servico_militar": [],
        "patente": [],
        "convocacao": [],
        "baixa_militar": [],
        "condecoracao_ficticia": [],
    }

    for nome, loc in _UNIDADES:
        rows["unidade_militar"].append({
            "id": str(uuid5(NAMESPACE_URL, f"unidmil-{nome}")),
            "nome": nome,
            "localizacao_ficticia": loc,
        })

    for p in personas:
        p["serviu_forca_armada"] = False
        if p["sexo"] != "masculino":
            continue
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)
        if age < 18:
            continue

        rng = master.fork(p["id"], "gen20-militar")
        conv_dt = born + timedelta(days=18 * 365 + 30)
        conv_dt = min(conv_dt, end)

        incorporado = rng.bernoulli(INCORPORATION_PROB_MALE_18) and (end - conv_dt).days >= 365
        resultado = "incorporado" if incorporado else "dispensado"
        rows["convocacao"].append({
            "id": str(uuid5(NAMESPACE_URL, f"convoc-{p['id']}")),
            "pessoa_id": p["id"],
            "data": conv_dt.isoformat(),
            "motivo": "alistamento militar obrigatório",
            "resultado": resultado,
        })

        if not incorporado:
            continue

        p["serviu_forca_armada"] = True
        srv_ini = conv_dt + timedelta(days=15)
        srv_fim = min(end, srv_ini + timedelta(days=350))
        if srv_fim <= srv_ini:
            srv_fim = srv_ini + timedelta(days=30)

        srv_id = str(uuid5(NAMESPACE_URL, f"srvmil-{p['id']}"))
        ramo = str(rng.choice(["Exército Fictício", "Marinha Simulada", "Aeronáutica Virtual"], weights=[0.70, 0.15, 0.15]))
        rows["servico_militar"].append({
            "id": srv_id,
            "pessoa_id": p["id"],
            "data_inicio": srv_ini.isoformat(),
            "data_fim": srv_fim.isoformat(),
            "ramo": ramo,
        })
        rows["patente"].append({
            "id": str(uuid5(NAMESPACE_URL, f"patente-{srv_id}")),
            "servico_militar_id": srv_id,
            "nome_patente": str(rng.choice(["Soldado", "Cabo", "3º Sargento"], weights=[0.75, 0.18, 0.07])),
            "data_promocao": srv_ini.isoformat(),
        })
        rows["baixa_militar"].append({
            "id": str(uuid5(NAMESPACE_URL, f"baixa-{srv_id}")),
            "servico_militar_id": srv_id,
            "data": srv_fim.isoformat(),
            "motivo": "conclusão do tempo de serviço obrigatório",
        })
        if rng.bernoulli(0.25):
            rows["condecoracao_ficticia"].append({
                "id": str(uuid5(NAMESPACE_URL, f"condec-{p['id']}")),
                "pessoa_id": p["id"],
                "nome": "Honra ao Mérito Militar Fictício",
                "data": srv_fim.isoformat(),
            })

    return rows
