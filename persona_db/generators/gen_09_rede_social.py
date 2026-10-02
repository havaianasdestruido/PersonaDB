"""gen_09_rede_social — domínio 09: amizades simétricas, grupos sociais, eventos e clubes.

Gera as tabelas de rede social interpessoal (`grupo_social`, `evento_social`,
`clube`, `amizade`, `membro_grupo_social`, `participacao_evento_social`,
`contato_pessoal`, `inimizade_ficticia`), garantindo simetria estrita na
tabela `amizade` (se A é amigo de B, B é amigo de A) conforme TASK-075.
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

_GRUPOS = [
    ("Associação de Moradores do Bairro", "comunitário"),
    ("Grupo de Estudos e Leitura Fictício", "acadêmico"),
    ("Confraria Gastronômica Simulada", "lazer"),
    ("Coletivo Cultural Virtual", "cultural"),
]

_EVENTOS = [
    "Encontro Anual da Comunidade Fictícia",
    "Feira de Inovação e Cultura Simulada",
    "Festival de Música e Gastronomia Virtual",
]

_CLUBES = [
    ("Clube Recreativo Alvorada", "recreativo"),
    ("Sociedade Literária Fictícia", "cultural"),
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
    """Gera todas as tabelas do domínio 09 (Rede Social)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "grupo_social": [],
        "evento_social": [],
        "clube": [],
        "amizade": [],
        "membro_grupo_social": [],
        "participacao_evento_social": [],
        "contato_pessoal": [],
        "inimizade_ficticia": [],
    }

    grupos: list[dict[str, Any]] = []
    for nome, tipo in _GRUPOS:
        gid = str(uuid5(NAMESPACE_URL, f"grupo-{nome}"))
        rec = {"id": gid, "nome": nome, "tipo": tipo, "data_criacao": "2015-01-15"}
        rows["grupo_social"].append(rec)
        grupos.append(rec)

    eventos: list[dict[str, Any]] = []
    for idx, nome in enumerate(_EVENTOS):
        eid = str(uuid5(NAMESPACE_URL, f"evsoc-{nome}"))
        ev_dt = today - timedelta(days=90 * (idx + 1))
        rec = {
            "id": eid,
            "nome": nome,
            "data": f"{ev_dt.isoformat()}T20:00:00+00:00",
            "local_endereco_id": None,
        }
        rows["evento_social"].append(rec)
        eventos.append(rec)

    for nome, cat in _CLUBES:
        rows["clube"].append({
            "id": str(uuid5(NAMESPACE_URL, f"clube-{nome}")),
            "nome": nome,
            "categoria": cat,
        })

    if len(personas) < 2:
        return rows

    seen_friend_pairs: set[frozenset[str]] = set()
    for idx, p in enumerate(personas):
        rng = master.fork(p["id"], "gen09-social")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)
        if age < 7:
            continue

        # Amizade simétrica (A <-> B)
        friend = personas[(idx + 1 + rng.integer(0, max(0, len(personas) - 2))) % len(personas)]
        if friend["id"] != p["id"]:
            pair = frozenset((p["id"], friend["id"]))
            dt_ini = max(_birth(p), _birth(friend)) + timedelta(days=7 * 365)
            dt_max = min(_end_date(p, today), _end_date(friend, today))
            if pair not in seen_friend_pairs and dt_ini <= dt_max:
                seen_friend_pairs.add(pair)
                ctx = str(rng.choice(["escola", "trabalho", "vizinhança", "família"]))
                rows["amizade"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"amiz-{p['id']}-{friend['id']}")),
                    "pessoa_id_a": p["id"],
                    "pessoa_id_b": friend["id"],
                    "data_inicio": dt_ini.isoformat(),
                    "contexto_conhecimento": ctx,
                })
                rows["amizade"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"amiz-{friend['id']}-{p['id']}")),
                    "pessoa_id_a": friend["id"],
                    "pessoa_id_b": p["id"],
                    "data_inicio": dt_ini.isoformat(),
                    "contexto_conhecimento": ctx,
                })
                rows["contato_pessoal"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"contpess-{p['id']}-{friend['id']}")),
                    "pessoa_id": p["id"],
                    "pessoa_id_contato": friend["id"],
                    "frequencia_contato": str(rng.choice(["semanal", "mensal", "diária"])),
                    "tipo_vinculo": "amigo",
                })

        # Participação em grupos e eventos
        if rng.bernoulli(0.45):
            grp = rng.choice(grupos)
            g_dt = max(born + timedelta(days=12 * 365), date(2016, 1, 1))
            if g_dt <= end:
                rows["membro_grupo_social"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"memgrp-{p['id']}-{grp['id']}")),
                    "pessoa_id": p["id"],
                    "grupo_id": grp["id"],
                    "data_entrada": g_dt.isoformat(),
                    "papel": "membro",
                })

        if rng.bernoulli(0.35):
            ev = rng.choice(eventos)
            rows["participacao_evento_social"].append({
                "id": str(uuid5(NAMESPACE_URL, f"partev-{p['id']}-{ev['id']}")),
                "pessoa_id": p["id"],
                "evento_id": ev["id"],
                "papel": str(rng.choice(["convidado", "organizador", "palestrante"], weights=[0.85, 0.10, 0.05])),
            })

        # Inimizade ocasional sem auto-referência
        if age >= 18 and rng.bernoulli(0.06):
            rival = personas[(idx + 2) % len(personas)]
            if rival["id"] != p["id"]:
                dt_riv = max(_birth(p), _birth(rival)) + timedelta(days=18 * 365)
                dt_max_r = min(_end_date(p, today), _end_date(rival, today))
                if dt_riv <= dt_max_r:
                    rows["inimizade_ficticia"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"inim-{p['id']}-{rival['id']}")),
                        "pessoa_id_a": p["id"],
                        "pessoa_id_b": rival["id"],
                        "motivo": "desentendimento comercial ou condominial",
                        "data_inicio": dt_riv.isoformat(),
                    })

    return rows
