"""gen_19_esporte — domínio 19: esportes praticados, clubes esportivos, competições e hobbies.

Implementa a seção de Esporte & Lazer de TASK-053 em TODO.MD:
- Prática de esportes, filiação a clubes esportivos, participação em
  competições, aquisição de equipamentos esportivos, hobbies e coleções.
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

_CLUBES_ESPORTIVOS = [
    ("Esporte Clube Alvorada Fictício", "futebol"),
    ("Associação Atlética Natação Simulada", "natação"),
    ("Clube de Corrida e Atletismo Virtual", "atletismo"),
]

_COMPETICOES = [
    ("Meia Maratona de Alvorada", "atletismo"),
    ("Torneio Interclubes de Futebol Amador", "futebol"),
    ("Copa Regional de Natação Simulada", "natação"),
]

_ESPORTES = ["futebol", "corrida de rua", "natação", "ciclismo", "musculação", "vôlei"]
_HOBBIES = ["leitura", "jardinagem", "jogos de tabuleiro", "culinária", "fotografia", "música"]
_COLECOES = ["moedas comemorativas", "discos de vinil", "livros raros", "camisas de futebol"]


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
    """Gera todas as tabelas do domínio 19 (Esporte & Lazer)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "clube_esportivo": [],
        "competicao": [],
        "esporte_praticado": [],
        "membro_clube_esportivo": [],
        "resultado_competicao": [],
        "equipamento_esportivo": [],
        "hobby": [],
        "colecao_ficticia": [],
    }

    clubes: list[dict[str, Any]] = []
    for nome, mod in _CLUBES_ESPORTIVOS:
        cid = str(uuid5(NAMESPACE_URL, f"clubeesp-{nome}"))
        rec = {"id": cid, "nome": nome, "modalidade": mod}
        rows["clube_esportivo"].append(rec)
        clubes.append(rec)

    competicoes: list[dict[str, Any]] = []
    for idx, (nome, mod) in enumerate(_COMPETICOES):
        comp_id = str(uuid5(NAMESPACE_URL, f"compesp-{nome}"))
        comp_dt = today - timedelta(days=120 * (idx + 1))
        rec = {"id": comp_id, "nome": nome, "modalidade": mod, "data": comp_dt.isoformat()}
        rows["competicao"].append(rec)
        competicoes.append(rec)

    for p in personas:
        rng = master.fork(p["id"], "gen19-esporte")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)
        if age < 6:
            continue

        # Hobby universal
        rows["hobby"].append({
            "id": str(uuid5(NAMESPACE_URL, f"hobby-{p['id']}")),
            "pessoa_id": p["id"],
            "nome": str(rng.choice(_HOBBIES)),
            "frequencia": str(rng.choice(["semanal", "diária", "quinzenal"])),
        })

        if rng.bernoulli(0.22):
            rows["colecao_ficticia"].append({
                "id": str(uuid5(NAMESPACE_URL, f"colecao-{p['id']}")),
                "pessoa_id": p["id"],
                "tema": str(rng.choice(_COLECOES)),
                "quantidade_itens": rng.integer(5, 180),
            })

        if not rng.bernoulli(0.58):
            continue

        esp = str(rng.choice(_ESPORTES))
        rows["esporte_praticado"].append({
            "id": str(uuid5(NAMESPACE_URL, f"espprat-{p['id']}")),
            "pessoa_id": p["id"],
            "nome_esporte": esp,
            "nivel": str(rng.choice(["iniciante", "amador", "avançado"])),
            "frequencia": str(rng.choice(["2x/semana", "3x/semana", "fins de semana"])),
        })

        eq_dt = max(born + timedelta(days=6 * 365), end - timedelta(days=rng.integer(30, 720)))
        eq_dt = min(eq_dt, end)
        rows["equipamento_esportivo"].append({
            "id": str(uuid5(NAMESPACE_URL, f"eqesp-{p['id']}")),
            "pessoa_id": p["id"],
            "tipo": f"kit para {esp}",
            "marca_ficticia": "AtletaPro Fictícia",
            "data_aquisicao": eq_dt.isoformat(),
        })

        if rng.bernoulli(0.30):
            clb = rng.choice(clubes)
            rows["membro_clube_esportivo"].append({
                "id": str(uuid5(NAMESPACE_URL, f"memclbesp-{p['id']}")),
                "pessoa_id": p["id"],
                "clube_id": clb["id"],
                "data_entrada": eq_dt.isoformat(),
            })

        if age >= 16 and rng.bernoulli(0.20):
            comp = rng.choice(competicoes)
            rows["resultado_competicao"].append({
                "id": str(uuid5(NAMESPACE_URL, f"rescomp-{p['id']}-{comp['id']}")),
                "pessoa_id": p["id"],
                "competicao_id": comp["id"],
                "colocacao": rng.integer(1, 50),
            })

    return rows
