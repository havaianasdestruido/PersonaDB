"""gen_08_relacionamentos — domínio 08: relacionamentos afetivos, casamentos, divórcios e filhos.

Implementa TASK-049 de TODO.MD:
- Linha do tempo afetiva utilizando `FamilyEngine` (`engines/family.py`).
- Casamentos civis apenas para maiores de 18 anos (respeitando idade mínima
  legal >= 16 anos), sem casamentos simultâneos ativos e sem auto-referência.
- Divórcios modulados pelos fatores de risco de `FamilyEngine.divorce`
  (doença mental do cônjuge, antecedente criminal, diferença de classe,
  desemprego prolongado, filhos pequenos e religiosidade).
- Registros de `filho`, `guarda_compartilhada` e `pensao_alimenticia`
  estritamente consistentes com os vínculos parentais biológicos.
"""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from typing import Any
from uuid import NAMESPACE_URL, uuid5

try:  # pragma: no cover
    from persona_db.engines.family import FamilyEngine
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.family import FamilyEngine
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today

_REGIMES_BENS: dict[str, str] = {
    "A": "separação total de bens",
    "B1": "comunhão parcial de bens",
    "B2": "comunhão parcial de bens",
    "C1": "comunhão parcial de bens",
    "C2": "comunhão parcial de bens",
    "D_E": "comunhão parcial de bens",
}

_MOTIVOS_TERMINO = [
    "incompatibilidade de objetivos",
    "mudança de cidade",
    "desgaste natural do relacionamento",
    "divergências familiares",
]

_MOTIVOS_DIVORCIO = [
    "incompatibilidade de gênios",
    "crise financeira familiar",
    "desgaste conjugal prolongado",
    "mudança de projetos de vida",
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
    """Gera todas as tabelas do domínio 08 (Relacionamentos & Família Nuclear)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "relacionamento": [],
        "namoro": [],
        "casamento": [],
        "divorcio": [],
        "uniao_estavel": [],
        "filho": [],
        "guarda_compartilhada": [],
        "pensao_alimenticia": [],
        "adocao_ficticia": [],
        "padrinho_madrinha": [],
    }

    by_id = {p["id"]: p for p in personas}
    adults = [
        p for p in personas
        if (_end_date(p, today) - _birth(p)).days >= 18 * 365 + 180
    ]

    # 1. Pareamento de casamentos (cada pessoa no máximo em 1 casamento para evitar bigamia)
    married_ids: set[str] = set()
    males = [p for p in adults if p["sexo"] == "masculino"]
    females = [p for p in adults if p["sexo"] == "feminino"]

    for m in males:
        if m["id"] in married_ids:
            continue
        rng = master.fork(m["id"], "gen08-casamento")
        fam_eng = FamilyEngine(rng)
        m_age_marriage = fam_eng.first_marriage_age("M")
        if m_age_marriage is None:
            continue

        # Procura parceira elegível próxima em idade e não parente direta
        m_birth = _birth(m)
        m_end = _end_date(m, today)
        candidates = [
            f for f in females
            if f["id"] not in married_ids
            and f["id"] != m["id"]
            and m["id"] not in (f.get("pai_id"), f.get("mae_id"))
            and f["id"] not in (m.get("pai_id"), m.get("mae_id"))
            and not (
                {m.get("pai_id"), m.get("mae_id")} - {None}
            ).intersection({f.get("pai_id"), f.get("mae_id")} - {None})
            and abs((_birth(f) - m_birth).days) <= 12 * 365
        ]
        if not candidates:
            continue
        partner = rng.choice(candidates)
        f_birth = _birth(partner)
        f_end = _end_date(partner, today)

        min_marriage_dt = max(
            m_birth + timedelta(days=int(max(18.5, m_age_marriage) * 365.25)),
            f_birth + timedelta(days=int(18.5 * 365.25)),
        )
        max_marriage_dt = min(m_end, f_end) - timedelta(days=60)
        if min_marriage_dt >= max_marriage_dt:
            continue

        cas_dt = min_marriage_dt
        cas_id = str(uuid5(NAMESPACE_URL, f"cas-{m['id']}-{partner['id']}"))
        regime = _REGIMES_BENS.get(m["classe_social"], "comunhão parcial de bens")
        rows["casamento"].append({
            "id": cas_id,
            "pessoa_id_a": m["id"],
            "pessoa_id_b": partner["id"],
            "data": cas_dt.isoformat(),
            "regime_bens": regime,
        })
        married_ids.add(m["id"])
        married_ids.add(partner["id"])
        m["conjuge_id"] = partner["id"]
        partner["conjuge_id"] = m["id"]
        m["data_casamento"] = cas_dt.isoformat()
        partner["data_casamento"] = cas_dt.isoformat()

        # Relacionamento correspondente ao casamento
        rel_id = str(uuid5(NAMESPACE_URL, f"rel-cas-{cas_id}"))
        risk_factors = {
            "doenca_mental_conjuge": 1.0 if (m.get("tem_transtorno_mental") or partner.get("tem_transtorno_mental")) else 0.0,
            "antecedente_criminal_conjuge": 1.0 if (m.get("tem_antecedente_criminal") or partner.get("tem_antecedente_criminal")) else 0.0,
            "diferenca_classe": 1.0 if m["classe_social"] != partner["classe_social"] else 0.0,
            "desemprego_prolongado": 1.0 if (m.get("desempregado") or partner.get("desempregado")) else 0.0,
            "filhos_pequenos": 0.0,
            "religiosidade_alta": 1.0 if m.get("religiosidade_alta") else 0.0,
        }
        did_divorce = fam_eng.divorce(risk_factors) and (max_marriage_dt - cas_dt).days >= 180
        if did_divorce:
            div_dt = cas_dt + timedelta(days=rng.integer(180, (max_marriage_dt - cas_dt).days))
            rows["divorcio"].append({
                "id": str(uuid5(NAMESPACE_URL, f"div-{cas_id}")),
                "casamento_id": cas_id,
                "data": div_dt.isoformat(),
                "motivo_ficticio": str(rng.choice(_MOTIVOS_DIVORCIO)),
            })
            m["estado_civil"] = "divorciado"
            partner["estado_civil"] = "divorciado"
            m["data_divorcio"] = div_dt.isoformat()
            partner["data_divorcio"] = div_dt.isoformat()
            rows["relacionamento"].append({
                "id": rel_id,
                "pessoa_id_a": m["id"],
                "pessoa_id_b": partner["id"],
                "tipo": "casamento",
                "data_inicio": cas_dt.isoformat(),
                "data_fim": div_dt.isoformat(),
                "status": "encerrado",
            })
        else:
            m["estado_civil"] = "casado"
            partner["estado_civil"] = "casado"
            rows["relacionamento"].append({
                "id": rel_id,
                "pessoa_id_a": m["id"],
                "pessoa_id_b": partner["id"],
                "tipo": "casamento",
                "data_inicio": cas_dt.isoformat(),
                "data_fim": None,
                "status": "ativo",
            })

    # 2. Namoros e uniões estáveis para adultos não casados
    unmarried = [p for p in adults if p["id"] not in married_ids]
    for idx in range(0, len(unmarried) - 1, 2):
        pa, pb = unmarried[idx], unmarried[idx + 1]
        if pa["id"] == pb["id"]:
            continue
        rng = master.fork(pa["id"], "gen08-namoro")
        dt_min = max(_birth(pa) + timedelta(days=17 * 365), _birth(pb) + timedelta(days=17 * 365))
        dt_max = min(_end_date(pa, today), _end_date(pb, today)) - timedelta(days=30)
        if dt_min >= dt_max:
            continue

        ini_dt = dt_min + timedelta(days=rng.integer(0, max(1, (dt_max - dt_min).days // 2)))
        fim_dt = ini_dt + timedelta(days=rng.integer(60, max(61, (dt_max - ini_dt).days)))
        if fim_dt <= ini_dt:
            fim_dt = ini_dt + timedelta(days=30)

        rel_id = str(uuid5(NAMESPACE_URL, f"rel-nam-{pa['id']}-{pb['id']}"))
        encerrado = rng.bernoulli(0.55)
        rows["relacionamento"].append({
            "id": rel_id,
            "pessoa_id_a": pa["id"],
            "pessoa_id_b": pb["id"],
            "tipo": "namoro",
            "data_inicio": ini_dt.isoformat(),
            "data_fim": fim_dt.isoformat() if encerrado else None,
            "status": "encerrado" if encerrado else "ativo",
        })
        rows["namoro"].append({
            "id": str(uuid5(NAMESPACE_URL, f"nam-{rel_id}")),
            "relacionamento_id": rel_id,
            "motivo_termino": str(rng.choice(_MOTIVOS_TERMINO)) if encerrado else None,
        })
        if not encerrado and rng.bernoulli(0.35):
            rows["uniao_estavel"].append({
                "id": str(uuid5(NAMESPACE_URL, f"uniao-{pa['id']}-{pb['id']}")),
                "pessoa_id_a": pa["id"],
                "pessoa_id_b": pb["id"],
                "data_inicio": ini_dt.isoformat(),
                "data_reconhecimento": fim_dt.isoformat(),
            })

    # 3. Filhos, guarda compartilhada e pensão alimentícia (baseados nos pais biológicos)
    for child in personas:
        pai_id = child.get("pai_id")
        mae_id = child.get("mae_id")
        if not pai_id or not mae_id or pai_id == mae_id:
            continue
        pai = by_id.get(pai_id)
        mae = by_id.get(mae_id)
        if not pai or not mae:
            continue
        nasc_c = _birth(child)
        age_pai = (nasc_c - _birth(pai)).days / 365.25
        age_mae = (nasc_c - _birth(mae)).days / 365.25
        if not (14.0 <= age_mae <= 50.0 and 14.0 <= age_pai <= 70.0):
            continue

        filho_id = str(uuid5(NAMESPACE_URL, f"filho-{child['id']}"))
        rows["filho"].append({
            "id": filho_id,
            "pessoa_id_pai": pai_id,
            "pessoa_id_mae": mae_id,
            "pessoa_id_filho": child["id"],
            "data_nascimento": child["data_nascimento"],
        })

        rng = master.fork(child["id"], "gen08-guarda")
        if pai.get("estado_civil") == "divorciado" or mae.get("estado_civil") == "divorciado" or rng.bernoulli(0.30):
            resp_id = mae_id if pai.get("tem_antecedente_criminal") else (pai_id if rng.bernoulli(0.4) else mae_id)
            rows["guarda_compartilhada"].append({
                "id": str(uuid5(NAMESPACE_URL, f"guarda-{filho_id}")),
                "filho_id": filho_id,
                "responsavel_pessoa_id": resp_id,
                "percentual_tempo": 50.0 if not pai.get("tem_antecedente_criminal") else 80.0,
            })
            pagador_id = pai_id if resp_id == mae_id else mae_id
            pagador = by_id[pagador_id]
            sal = float(pagador.get("salario_mensal") or 1800.0)
            pensao_dt = min(_end_date(child, today), nasc_c + timedelta(days=365))
            rows["pensao_alimenticia"].append({
                "id": str(uuid5(NAMESPACE_URL, f"pensao-{filho_id}")),
                "pessoa_id_pagador": pagador_id,
                "pessoa_id_beneficiario": child["id"],
                "valor_mensal": round(max(250.0, sal * 0.22), 2),
                "data_inicio": pensao_dt.isoformat(),
            })

    # 4. Adoção fictícia e padrinhos/madrinhas
    if len(adults) >= 2:
        for idx, p in enumerate(personas[: min(15, len(personas))]):
            godparent = adults[idx % len(adults)]
            if godparent["id"] != p["id"]:
                rows["padrinho_madrinha"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"padr-{p['id']}-{godparent['id']}")),
                    "pessoa_id_afilhado": p["id"],
                    "pessoa_id_padrinho": godparent["id"],
                    "tipo": "batismo",
                })

        adopter = adults[0]
        adopted_candidates = [
            c for c in personas
            if c["id"] != adopter["id"]
            and (_birth(c) - _birth(adopter)).days >= 18 * 365
        ]
        if adopted_candidates:
            adotado = adopted_candidates[0]
            dt_adoc = min(_end_date(adotado, today), _birth(adotado) + timedelta(days=365))
            rows["adocao_ficticia"].append({
                "id": str(uuid5(NAMESPACE_URL, f"adoc-{adopter['id']}-{adotado['id']}")),
                "pessoa_id_adotante": adopter["id"],
                "pessoa_id_adotado": adotado["id"],
                "data": dt_adoc.isoformat(),
            })

    return rows
