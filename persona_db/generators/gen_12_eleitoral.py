"""gen_12_eleitoral — domínio 12: partidos, eleições, candidaturas, filiações e votos.

Implementa TASK-050 de TODO.MD:
- Modelo logístico de comportamento eleitoral (`esquerda`, `centro`, `direita`,
  `abstencao`) em função de classe socioeconômica, sindicalização, serviço
  militar e religiosidade.
- Votos estritamente restritos a cidadãos com idade >= 16 anos na data do
  pleito (`TASK-019`, `TASK-074`).
- Todo candidato registrado em `candidato` possui filiação partidária ativa
  no partido representado (`filiacao_partidaria`, `TASK-074`).
"""
from __future__ import annotations

import math
import os
import sys
from datetime import date, timedelta
from typing import Any
from uuid import NAMESPACE_URL, uuid5

try:  # pragma: no cover
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
    from persona_db.seeds.lookup_data import PARTIDOS
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
    from persona_db.seeds.lookup_data import PARTIDOS

_ELEICOES = [
    (2020, "municipal", "Alvorada Leste"),
    (2022, "federal", "Nacional Fictício"),
    (2024, "municipal", "Nova Serena"),
]


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


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
    """Gera todas as tabelas do domínio 12 (Eleitoral & Política)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "eleicao": [],
        "partido": [],
        "candidato": [],
        "voto": [],
        "filiacao_partidaria": [],
        "cargo_publico": [],
        "doacao_campanha_ficticia": [],
        "comparecimento_eleitoral": [],
    }

    partidos_by_spec: dict[str, list[dict[str, Any]]] = {"esquerda": [], "centro": [], "direita": []}
    all_partidos: list[dict[str, Any]] = []
    for pt in PARTIDOS:
        pid = str(uuid5(NAMESPACE_URL, f"partido-{pt['sigla']}"))
        rec = {"id": pid, "nome_ficticio": pt["nome"], "sigla_ficticia": pt["sigla"], "_espectro": pt["espectro"]}
        rows["partido"].append({"id": pid, "nome_ficticio": pt["nome"], "sigla_ficticia": pt["sigla"]})
        partidos_by_spec.setdefault(pt["espectro"], []).append(rec)
        all_partidos.append(rec)

    eleicoes: list[dict[str, Any]] = []
    for ano, tipo, mun in _ELEICOES:
        if date(ano, 10, 2) > today:
            continue
        eid = str(uuid5(NAMESPACE_URL, f"eleicao-{ano}-{tipo}"))
        erec = {"id": eid, "ano": ano, "tipo": tipo, "municipio_ficticio": mun}
        rows["eleicao"].append(erec)
        eleicoes.append(erec)

    if not eleicoes:
        return rows

    # 1. Seleciona candidatos e registra filiação partidária obrigatória
    affiliated_pairs: set[tuple[str, str]] = set()
    candidatos_by_eleicao: dict[str, list[dict[str, Any]]] = {e["id"]: [] for e in eleicoes}

    eligible_candidates = [
        p for p in personas
        if (_end_date(p, today) - _birth(p)).days >= 24 * 365
    ]

    for e in eleicoes:
        el_dt = date(e["ano"], 10, 2)
        pool = [
            p for p in eligible_candidates
            if _birth(p) + timedelta(days=21 * 365) <= el_dt <= _end_date(p, today)
        ]
        for idx, cand_p in enumerate(pool[: min(6, len(pool))]):
            rng = master.fork(cand_p["id"], f"gen12-cand-{e['ano']}")
            pt = all_partidos[(idx + cand_p["idx"]) % len(all_partidos)]
            pair = (cand_p["id"], pt["id"])
            if pair not in affiliated_pairs:
                affiliated_pairs.add(pair)
                fil_dt = max(_birth(cand_p) + timedelta(days=18 * 365), date(e["ano"] - 2, 3, 15))
                if fil_dt >= el_dt:
                    fil_dt = el_dt - timedelta(days=180)
                rows["filiacao_partidaria"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"fil-{cand_p['id']}-{pt['id']}")),
                    "pessoa_id": cand_p["id"],
                    "partido_id": pt["id"],
                    "data_filiacao": fil_dt.isoformat(),
                    "data_desfiliacao": None,
                })

            cargo = "Vereador Fictício" if e["tipo"] == "municipal" else "Deputado Federal Simulado"
            cid = str(uuid5(NAMESPACE_URL, f"cand-{e['id']}-{cand_p['id']}"))
            crec = {
                "id": cid,
                "pessoa_id": cand_p["id"],
                "eleicao_id": e["id"],
                "partido_id": pt["id"],
                "cargo_pretendido": cargo,
                "_espectro": pt["_espectro"],
            }
            rows["candidato"].append({
                "id": cid,
                "pessoa_id": cand_p["id"],
                "eleicao_id": e["id"],
                "partido_id": pt["id"],
                "cargo_pretendido": cargo,
            })
            candidatos_by_eleicao[e["id"]].append(crec)

            # Alguns candidatos assumem cargo público
            if idx == 0 and ( _end_date(cand_p, today) - el_dt ).days >= 120:
                cp_ini = date(e["ano"] + 1, 1, 1)
                cp_fim = min(_end_date(cand_p, today), date(e["ano"] + 4, 12, 31))
                if cp_fim > cp_ini:
                    cand_p["tem_cargo_publico"] = True
                    rows["cargo_publico"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"cargopub-{cid}")),
                        "pessoa_id": cand_p["id"],
                        "nome_cargo": cargo,
                        "orgao": f"Câmara {e['municipio_ficticio']}",
                        "data_inicio": cp_ini.isoformat(),
                        "data_fim": cp_fim.isoformat(),
                    })

    # 2. Votos, comparecimento eleitoral e doações de campanha (somente >= 16 anos na data da eleição)
    for p in personas:
        rng = master.fork(p["id"], "gen12-voto")
        born = _birth(p)
        end = _end_date(p, today)
        cls = p["classe_social"]

        # Propensão ideológica logística (TASK-050)
        low_cls = 1.0 if cls in ("C2", "D_E") else 0.0
        high_cls = 1.0 if cls in ("A", "B1") else 0.0
        union = 1.0 if p.get("sindicato") else 0.0
        relig = 1.0 if p.get("religiosidade_alta") else 0.0
        w_esq = _sigmoid(-0.4 + 0.7 * low_cls + 0.9 * union - 0.3 * relig)
        w_dir = _sigmoid(-0.4 + 0.8 * high_cls + 0.5 * relig)
        w_cen = 0.35

        for e in eleicoes:
            el_dt = date(e["ano"], 10, 2)
            # Verifica se a pessoa tinha pelo menos 16 anos completos e estava viva
            age_at_election = (el_dt - born).days / 365.25
            if age_at_election < 16.0 or el_dt > end:
                continue

            p_abst = 0.18 + (0.15 if p.get("foi_preso") else 0.0) + (0.05 if cls == "D_E" else 0.0)
            compareceu = not rng.bernoulli(min(0.60, p_abst))
            rows["comparecimento_eleitoral"].append({
                "id": str(uuid5(NAMESPACE_URL, f"comp-{e['id']}-{p['id']}")),
                "pessoa_id": p["id"],
                "eleicao_id": e["id"],
                "compareceu": compareceu,
                "justificativa_ausencia": None if compareceu else "viagem ou motivo de saúde",
            })

            if not compareceu:
                continue

            cands = candidatos_by_eleicao.get(e["id"], [])
            if not cands or rng.bernoulli(0.08):
                tipo_voto = str(rng.choice(["branco", "nulo"]))
                cand_escolhido = None
            else:
                tipo_voto = "candidato"
                spec = str(rng.choice(["esquerda", "centro", "direita"], weights=[w_esq, w_cen, w_dir]))
                spec_cands = [c for c in cands if c["_espectro"] == spec] or cands
                cand_escolhido = rng.choice(spec_cands)["id"]

            rows["voto"].append({
                "id": str(uuid5(NAMESPACE_URL, f"voto-{e['id']}-{p['id']}")),
                "pessoa_id": p["id"],
                "eleicao_id": e["id"],
                "candidato_id_escolhido": cand_escolhido,
                "tipo": tipo_voto,
            })

            # Doação de campanha para eleitores de alta renda
            if cand_escolhido and cls in ("A", "B1") and age_at_election >= 18.0 and rng.bernoulli(0.18):
                rows["doacao_campanha_ficticia"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"doacamp-{e['id']}-{p['id']}")),
                    "pessoa_id_doador": p["id"],
                    "candidato_id": cand_escolhido,
                    "valor": round(rng.uniform(250.0, 5000.0), 2),
                    "data": (el_dt - timedelta(days=rng.integer(10, 45))).isoformat(),
                })

    return rows
