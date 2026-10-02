"""gen_13_viagens — domínio 13: destinos, viagens, hospedagens, passagens e documentos de viagem.

Implementa TASK-051 de TODO.MD:
- Probabilidade de viagens nacionais e internacionais modulada pela classe
  socioeconômica, renda e posse de passaporte.
- Toda viagem internacional possui passaporte válido na data da viagem em
  `documento_viagem` (e sincronizado com `pessoa_documento`), garantindo 100%
  de consistência em `val_temporal.py`.
- Viagens de negócios correlacionadas com setor e carreira.
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

_DESTINOS_NACIONAIS = [
    ("Serra da Paz", "Brasil Fictício"),
    ("Vista do Mar", "Brasil Fictício"),
    ("Porto Azul", "Brasil Fictício"),
    ("Vale do Prata", "Brasil Fictício"),
    ("Alvorada das Águas", "Brasil Fictício"),
]

_DESTINOS_INTERNACIONAIS = [
    ("Nova Lisboa Simulada", "Portugal Fictício"),
    ("Porto del Sol Virtual", "Argentina Fictícia"),
    ("San Lorenzo Inventado", "Estados Unidos Fictícios"),
    ("Valparaíso do Norte Ficc.", "Chile Fictício"),
]

_COMPANHIAS_AEREAS = [
    "VoeFictício Linhas Aéreas",
    "SulAir Simulada",
    "Atlântico Virtual Airlines",
]

_COMPANHIAS_RODO = [
    "Expresso Horizonte Fictício",
    "Viação Cruzeiro Simulado",
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
    existing_tables: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Gera todas as tabelas do domínio 13 (Viagens)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "destino": [],
        "viagem": [],
        "hospedagem": [],
        "transporte_viagem": [],
        "passagem": [],
        "documento_viagem": [],
        "bagagem": [],
        "seguro_viagem": [],
        "roteiro_viagem": [],
        "companhia_viagem": [],
    }

    dest_nac: list[dict[str, Any]] = []
    dest_int: list[dict[str, Any]] = []
    for cid_nome, pais in _DESTINOS_NACIONAIS:
        did = str(uuid5(NAMESPACE_URL, f"dest-{cid_nome}-{pais}"))
        rec = {"id": did, "cidade_ficticia": cid_nome, "pais_ficticio": pais}
        rows["destino"].append(rec)
        dest_nac.append(rec)

    for cid_nome, pais in _DESTINOS_INTERNACIONAIS:
        did = str(uuid5(NAMESPACE_URL, f"dest-{cid_nome}-{pais}"))
        rec = {"id": did, "cidade_ficticia": cid_nome, "pais_ficticio": pais}
        rows["destino"].append(rec)
        dest_int.append(rec)

    for p in personas:
        rng = master.fork(p["id"], "gen13-viagens")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)
        if age < 18:
            continue

        cls = p["classe_social"]
        p_viagem = {"A": 0.85, "B1": 0.72, "B2": 0.55, "C1": 0.40, "C2": 0.25, "D_E": 0.12}.get(cls, 0.30)
        if not rng.bernoulli(p_viagem):
            continue

        min_dt = max(born + timedelta(days=18 * 365), end - timedelta(days=1800))
        if min_dt >= end - timedelta(days=15):
            continue

        n_trips = 2 if cls in ("A", "B1") and rng.bernoulli(0.45) else 1
        has_passport_doc = False
        passport_val = (end + timedelta(days=1825)).isoformat()

        for t_idx in range(n_trips):
            is_intl = cls in ("A", "B1", "B2") and rng.bernoulli(0.40 if cls == "A" else 0.20)
            dest = rng.choice(dest_int if is_intl else dest_nac)

            span = max(10, (end - timedelta(days=12) - min_dt).days)
            ida_dt = min_dt + timedelta(days=rng.integer(0, max(1, span - 1)))
            dur_days = rng.integer(3, 10)
            volta_dt = min(end, ida_dt + timedelta(days=dur_days))
            if volta_dt <= ida_dt:
                volta_dt = ida_dt + timedelta(days=2)

            if is_intl and not has_passport_doc:
                has_passport_doc = True
                rows["documento_viagem"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"docviag-pass-{p['id']}")),
                    "pessoa_id": p["id"],
                    "tipo": "passaporte",
                    "validade": passport_val,
                })
                # Sincroniza passaporte válido em pessoa_documento se a tabela estiver presente
                if existing_tables is not None and "pessoa_documento" in existing_tables:
                    existing_pass = [
                        d for d in existing_tables["pessoa_documento"]
                        if d.get("pessoa_id") == p["id"] and d.get("tipo") == "passaporte"
                    ]
                    if existing_pass:
                        for d in existing_pass:
                            d["validade"] = passport_val
                    else:
                        existing_tables["pessoa_documento"].append({
                            "id": str(uuid5(NAMESPACE_URL, f"doc-{p['id']}-PASS")),
                            "pessoa_id": p["id"],
                            "tipo": "passaporte",
                            "numero_ficticio": f"BR{p['idx']:07d}",
                            "orgao_emissor": "Polícia Federal Fictícia",
                            "validade": passport_val,
                        })

            motivo = (
                "negócios"
                if p.get("setor_empregado") in ("tecnologia", "financeiro", "gerencia") and rng.bernoulli(0.35)
                else str(rng.choice(["turismo", "visita familiar", "lazer"]))
            )
            viag_id = str(uuid5(NAMESPACE_URL, f"viagem-{p['id']}-{t_idx}"))
            rows["viagem"].append({
                "id": viag_id,
                "pessoa_id": p["id"],
                "destino_id": dest["id"],
                "data_ida": ida_dt.isoformat(),
                "data_volta": volta_dt.isoformat(),
                "motivo": motivo,
            })

            # Hospedagem
            tipo_hosp = str(rng.choice(["hotel", "pousada", "airbnb", "hostel", "familia"]))
            rows["hospedagem"].append({
                "id": str(uuid5(NAMESPACE_URL, f"hosp-{viag_id}")),
                "viagem_id": viag_id,
                "tipo": tipo_hosp,
                "nome_estabelecimento": f"Hospedagem {dest['cidade_ficticia']}",
                "custo": round(rng.uniform(350.0, 4200.0), 2),
            })

            # Transporte e passagem
            tipo_transp = "aereo" if is_intl or cls in ("A", "B1") else str(rng.choice(["aereo", "rodoviario"]))
            comp = str(rng.choice(_COMPANHIAS_AEREAS if tipo_transp == "aereo" else _COMPANHIAS_RODO))
            transp_id = str(uuid5(NAMESPACE_URL, f"transp-{viag_id}"))
            rows["transporte_viagem"].append({
                "id": transp_id,
                "viagem_id": viag_id,
                "tipo": tipo_transp,
                "companhia": comp,
            })
            rows["passagem"].append({
                "id": str(uuid5(NAMESPACE_URL, f"pass-{transp_id}")),
                "transporte_id": transp_id,
                "numero_ficticio": f"TKT-{p['idx']:04d}-{t_idx}",
                "classe": "executiva" if cls == "A" and rng.bernoulli(0.4) else "econômica",
                "valor": round(rng.uniform(220.0, 5800.0), 2),
            })

            # Bagagem, seguro e roteiro
            rows["bagagem"].append({
                "id": str(uuid5(NAMESPACE_URL, f"bag-{viag_id}")),
                "viagem_id": viag_id,
                "tipo": "mala despachada" if tipo_transp == "aereo" else "mala de mão",
                "peso": round(rng.uniform(8.0, 23.0), 2),
                "extraviada": rng.bernoulli(0.02),
            })
            if is_intl or rng.bernoulli(0.35):
                rows["seguro_viagem"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"segviag-{viag_id}")),
                    "viagem_id": viag_id,
                    "seguradora": "Assistência Global Fictícia",
                    "cobertura": "médica e extravio de bagagem",
                })
            rows["roteiro_viagem"].append({
                "id": str(uuid5(NAMESPACE_URL, f"rot-{viag_id}-1")),
                "viagem_id": viag_id,
                "dia": 1,
                "atividade_planejada": f"Chegada e passeio em {dest['cidade_ficticia']}",
            })

            if p.get("conjuge_id"):
                rows["companhia_viagem"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"compviag-{viag_id}")),
                    "viagem_id": viag_id,
                    "pessoa_id_acompanhante": p["conjuge_id"],
                })

    return rows
