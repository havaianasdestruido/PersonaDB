"""gen_22_comunicacao — domínio 22: telefones, e-mails únicos, correspondências e registros de comunicação.

Implementa a seção de Comunicação de TASK-053 em TODO.MD:
- Telefones fixos e celulares fictícios, endereços de e-mail únicos e registros
  de chamadas, mensagens e correspondências entre personas.
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

_PROVEDORES_EMAIL = ["correio.personadb.test", "mail.personadb.test", "inbox.personadb.test"]


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
    """Gera todas as tabelas do domínio 22 (Comunicação)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "telefone": [],
        "email": [],
        "correspondencia": [],
        "ligacao_registro": [],
        "mensagem_registro": [],
    }

    for idx, p in enumerate(personas):
        rng = master.fork(p["id"], "gen22-comunicacao")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)
        if age < 12:
            continue

        ddd = 11 + (p["idx"] % 78)
        num_cel = f"+55 ({ddd:02d}) 9{8000 + (p['idx'] % 1999):04d}-{1000 + (p['idx'] * 7 % 8999):04d}"
        rows["telefone"].append({
            "id": str(uuid5(NAMESPACE_URL, f"tel-cel-{p['id']}")),
            "pessoa_id": p["id"],
            "numero_ficticio": num_cel,
            "tipo": "celular",
        })

        if age >= 30 and rng.bernoulli(0.28):
            num_fixo = f"+55 ({ddd:02d}) 3{200 + (p['idx'] % 799):03d}-{1000 + (p['idx'] * 3 % 8999):04d}"
            rows["telefone"].append({
                "id": str(uuid5(NAMESPACE_URL, f"tel-fixo-{p['id']}")),
                "pessoa_id": p["id"],
                "numero_ficticio": num_fixo,
                "tipo": "fixo",
            })

        prov = str(rng.choice(_PROVEDORES_EMAIL))
        first_slug = "".join(c.lower() for c in p["nome_completo"].split()[0] if c.isalnum())
        email_addr = f"{first_slug}.{p['idx']}@{prov}"
        rows["email"].append({
            "id": str(uuid5(NAMESPACE_URL, f"email-{p['id']}")),
            "pessoa_id": p["id"],
            "endereco_ficticio": email_addr,
            "provedor": prov,
        })

        if len(personas) >= 2:
            other = personas[(idx + 1) % len(personas)]
            if other["id"] != p["id"]:
                dt_max = min(end, _end_date(other, today))
                dt_min = max(born + timedelta(days=12 * 365), _birth(other) + timedelta(days=12 * 365))
                if dt_min <= dt_max:
                    rows["ligacao_registro"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"lig-{p['id']}-{other['id']}")),
                        "pessoa_id_a": p["id"],
                        "pessoa_id_b": other["id"],
                        "data": f"{dt_max.isoformat()}T15:00:00+00:00",
                        "duracao": "00:04:30",
                    })
                    rows["mensagem_registro"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"msg-{p['id']}-{other['id']}")),
                        "pessoa_id_a": p["id"],
                        "pessoa_id_b": other["id"],
                        "plataforma": "Mensageiro Instantâneo Ficc.",
                        "data": f"{dt_max.isoformat()}T16:10:00+00:00",
                    })
                    if rng.bernoulli(0.25):
                        rows["correspondencia"].append({
                            "id": str(uuid5(NAMESPACE_URL, f"corresp-{p['id']}-{other['id']}")),
                            "pessoa_id_remetente": p["id"],
                            "pessoa_id_destinatario": other["id"],
                            "tipo": "carta registrada",
                            "data": dt_max.isoformat(),
                        })

    return rows
