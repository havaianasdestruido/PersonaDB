"""gen_11_juridico — domínio 11: processos judiciais, ocorrências, sentenças e antecedentes.

Implementa TASK-047 de TODO.MD:
- Calcula envolvimento criminal via `CriminalEngine` incorporando preditores
  familiares (`pai_criminal`, `mae_criminal`, `irmao_criminal`), desemprego,
  abandono escolar, saúde mental, escolaridade e renda.
- Garante imputabilidade penal (idade >= 18 anos na data do processo/julgamento).
- Registra cadeia completa: `processo` -> `processo_advogado` -> `julgamento`
  -> `sentenca` -> `pena` -> `antecedente_criminal`.
- Aplica impactos retroativos nos contratos de trabalho para garantir que
  nenhuma pessoa presa mantenha contrato de trabalho ativo durante o período
  de cumprimento de pena de prisão.
- Gera ocorrências policiais, boletins de ocorrência, processos cíveis, multas
  e contratos jurídicos privados.
"""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from typing import Any
from uuid import NAMESPACE_URL, uuid5

try:  # pragma: no cover
    from persona_db.engines.criminal import CriminalEngine
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.criminal import CriminalEngine
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today

# ---------------------------------------------------------------------------
# Constantes nomeadas (TASK-047)
# ---------------------------------------------------------------------------
CIVIL_LABOR_SUIT_PROB = 0.08
CIVIL_DIVORCE_SUIT_FACTOR = 0.15
CIVIL_CONSUMER_SUIT_PROB = 0.04

_TRIBUNAIS = [
    ("Tribunal de Justiça Fictício do Sudeste", "estadual"),
    ("Tribunal Regional Federal Simulado 1ª Região", "federal"),
    ("Tribunal Regional do Trabalho Virtual", "trabalhista"),
    ("Juizado Especial Cível e Criminal Inventado", "estadual"),
    ("Vara de Família e Sucessões Fictícia", "estadual"),
]

_ADVOGADOS = [
    (f"Dr(a). Defensor Simulado {i:02d}", f"OAB-FIC-{10000 + i:05d}")
    for i in range(1, 21)
]

_DELEGACIAS = [
    "1ª Delegacia Distrital Fictícia",
    "Delegacia Central de Polícia Simulada",
    "Delegacia de Crimes Cibernéticos Virtual",
    "Delegacia de Proteção ao Cidadão Inventada",
]


def _birth(p: dict[str, Any]) -> date:
    return date.fromisoformat(p["data_nascimento"])


def _end_date(p: dict[str, Any], today: date) -> date:
    if p.get("data_obito"):
        return min(today, date.fromisoformat(p["data_obito"]))
    return today


def _build_catalogs(
    rows: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tribunais: list[dict[str, Any]] = []
    for nome, jur in _TRIBUNAIS:
        tid = str(uuid5(NAMESPACE_URL, f"tribunal-{nome}"))
        rec = {"id": tid, "nome_ficticio": nome, "jurisdicao": jur}
        rows["tribunal"].append(rec)
        tribunais.append(rec)

    advogados: list[dict[str, Any]] = []
    for nome, oab in _ADVOGADOS:
        aid = str(uuid5(NAMESPACE_URL, f"advogado-{oab}"))
        rec = {"id": aid, "nome": nome, "oab_ficticia": oab}
        rows["advogado"].append(rec)
        advogados.append(rec)

    return tribunais, advogados


def _terminate_overlapping_contracts(
    person_id: str,
    prison_start: date,
    prison_end: date,
    existing_tables: dict[str, list[dict[str, Any]]] | None,
    *,
    persona: dict[str, Any] | None = None,
    today: date | None = None,
) -> None:
    """Encerra contratos sobrepostos e ajusta seus registros dependentes."""
    if not existing_tables or "contrato_trabalho" not in existing_tables:
        return
    today = today or simulation_today()
    kept_contracts: list[dict[str, Any]] = []
    dropped: set[str] = set()
    shortened: dict[str, str] = {}
    open_ended: set[str] = set()
    for c in existing_tables["contrato_trabalho"]:
        if c.get("pessoa_id") != person_id:
            kept_contracts.append(c)
            continue
        c_ini = date.fromisoformat(c["data_inicio"])
        c_fim = date.fromisoformat(c["data_fim"]) if c.get("data_fim") else None
        overlaps = c_ini <= prison_end and (c_fim is None or c_fim >= prison_start)
        if not overlaps:
            kept_contracts.append(c)
            continue
        new_end = prison_start - timedelta(days=1)
        if new_end > c_ini:
            if c_fim is None:
                open_ended.add(c["id"])
            c["data_fim"] = new_end.isoformat()
            shortened[c["id"]] = c["data_fim"]
            kept_contracts.append(c)
        else:
            dropped.add(c["id"])
    existing_tables["contrato_trabalho"] = kept_contracts

    # Estas tabelas usam IDs derivados do contrato, sem uma coluna contrato_id.
    derived_prefixes = {
        "historico_emprego": "histemp", "avaliacao_desempenho": "aval",
        "promocao": "promo", "licenca_trabalho": "lic",
    }
    for table, entries in existing_tables.items():
        derived_ids = {
            str(uuid5(NAMESPACE_URL, f"{derived_prefixes[table]}-{cid}")): cid
            for cid in dropped | shortened.keys()
        } if table in derived_prefixes else {}
        kept_rows = []
        for row in entries:
            cid = row.get("contrato_id") or derived_ids.get(row.get("id"))
            if cid in dropped:
                continue
            if cid in shortened:
                end = shortened[cid]
                for field in ("data_inicio", "data_fim", "inicio", "fim",
                              "data", "data_vigencia", "mes_referencia"):
                    if row.get(field) and row[field] > end:
                        row[field] = end
                if table == "holerite":
                    row["mes_referencia"] = row["mes_referencia"][:8] + "01"
                if table == "ferias":
                    row["dias"] = (date.fromisoformat(row["data_fim"])
                                   - date.fromisoformat(row["data_inicio"])).days
                if table in ("demissao", "historico_emprego"):
                    row["motivo" if table == "demissao" else "motivo_saida"] = "prisão"
            kept_rows.append(row)
        existing_tables[table] = kept_rows

    dismissals = existing_tables.setdefault("demissao", [])
    dismissed = {row["contrato_id"] for row in dismissals}
    for cid in sorted(open_ended - dismissed):
        dismissals.append({
            "id": str(uuid5(NAMESPACE_URL, f"dem-{cid}")),
            "contrato_id": cid,
            "data": shortened[cid],
            "motivo": "prisão",
            "tipo": "justa_causa",
        })

    if persona is None:
        persona = next((p for p in existing_tables.get("pessoa", [])
                        if p.get("id") == person_id), None)
    if persona is not None:
        active = [c for c in kept_contracts if c.get("pessoa_id") == person_id
                  and c["data_inicio"] <= today.isoformat()
                  and (not c.get("data_fim") or c["data_fim"] >= today.isoformat())]
        current = max(active, key=lambda c: c["data_inicio"], default=None)
        salaries = [s for s in existing_tables.get("salario", [])
                    if current and s.get("contrato_id") == current["id"]
                    and s["data_vigencia"] <= today.isoformat()]
        salary = max(salaries, key=lambda s: s["data_vigencia"], default={})
        persona["salario_mensal"] = float(salary.get("valor", 0.0))
        persona["renda_anual"] = round(persona["salario_mensal"] * 13.3, 2)
        persona["empresa_atual_id"] = current["empresa_id"] if current else None
        persona["desempregado"] = current is None


def generate(
    personas: list[dict[str, Any]],
    seed: int = 7,
    today: date | None = None,
    existing_tables: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Gera todas as tabelas do domínio 11 (Jurídico & Criminal)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "tribunal": [],
        "processo": [],
        "pessoa_processo": [],
        "advogado": [],
        "processo_advogado": [],
        "ocorrencia_policial": [],
        "boletim_ocorrencia": [],
        "julgamento": [],
        "sentenca": [],
        "pena": [],
        "antecedente_criminal": [],
        "multa": [],
        "contrato_juridico": [],
    }

    tribunais, advogados = _build_catalogs(rows)
    by_id = {p["id"]: p for p in personas}
    ordered = sorted(personas, key=lambda p: (p.get("geracao", 0), p["idx"]))
    proc_seq = 0
    bo_seq = 0

    for p in ordered:
        rng = master.fork(p["id"], "gen11-juridico")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)

        p["tem_antecedente_criminal"] = False
        p["foi_preso"] = False
        p["prisao_periodo"] = None

        # 1. Ocorrência policial e Boletim de Ocorrência (inclusive como vítima)
        p_bo = 0.22 if p["classe_social"] in ("C2", "D_E") else 0.14
        if age >= 16 and rng.bernoulli(p_bo):
            bo_seq += 1
            oc_dt = born + timedelta(days=16 * 365 + rng.integer(1, max(2, (end - (born + timedelta(days=16 * 365))).days)))
            oc_dt = min(oc_dt, end)
            oc_id = str(uuid5(NAMESPACE_URL, f"ocorrencia-{p['id']}-{bo_seq}"))
            rows["ocorrencia_policial"].append({
                "id": oc_id,
                "pessoa_id": p["id"],
                "tipo": str(rng.choice(["furto", "extravio de documento", "acidente de trânsito", "perturbação do sossego"])),
                "data": f"{oc_dt.isoformat()}T14:30:00+00:00",
                "local_endereco_id": None,
            })
            rows["boletim_ocorrencia"].append({
                "id": str(uuid5(NAMESPACE_URL, f"bo-{oc_id}")),
                "ocorrencia_id": oc_id,
                "numero_ficticio": f"BO-{oc_dt.year}-{p['idx']:05d}-{bo_seq:04d}",
                "delegacia": str(rng.choice(_DELEGACIAS)),
            })

        # Imputabilidade penal somente para maiores de 18 anos
        adult_start = born + timedelta(days=18 * 365 + 30)
        if age < 19 or adult_start >= end - timedelta(days=30):
            continue

        pai = by_id.get(p.get("pai_id")) if p.get("pai_id") else None
        mae = by_id.get(p.get("mae_id")) if p.get("mae_id") else None
        pai_crim = bool(pai and pai.get("tem_antecedente_criminal"))
        mae_crim = bool(mae and mae.get("tem_antecedente_criminal"))

        features = {
            "sex": p["sexo"],
            "age": age,
            "class_label": p["classe_social"],
            "pai_criminal": pai_crim,
            "mae_criminal": mae_crim,
            "irmao_criminal": False,
            "desemprego": bool(p.get("desempregado")),
            "abandono_escolar": bool(p.get("abandono_escolar")),
            "transtorno_mental": bool(p.get("tem_transtorno_mental")),
            "education": p.get("education", "medio"),
            "income_annual": float(p.get("renda_anual") or 0.0),
            "sector": p.get("setor_empregado") or "",
            "formal_employment": not bool(p.get("desempregado")),
            "family_support": bool(p.get("pai_id") or p.get("mae_id")),
        }

        crim_engine = CriminalEngine(rng)
        series = crim_engine.criminal_process_series(features)
        p["criminal"] = series

        # 2. Processo criminal (se cometeu crime)
        if series["did_crime"]:
            proc_seq += 1
            proc_id = str(uuid5(NAMESPACE_URL, f"proc-crim-{p['id']}-{proc_seq}"))
            span_days = max(10, (end - adult_start).days - 60)
            proc_dt = adult_start + timedelta(days=rng.integer(0, max(1, span_days)))
            if proc_dt > end:
                proc_dt = adult_start

            status_proc = "julgado" if series["convicted"] or series["was_arrested"] else "arquivado"
            rows["processo"].append({
                "id": proc_id,
                "numero_ficticio": f"00{proc_seq:05d}-88.{proc_dt.year}.8.26.0000",
                "tipo": f"criminal:{series['crime_type']}",
                "tribunal_id": tribunais[0]["id"],
                "status": status_proc,
            })
            rows["pessoa_processo"].append({
                "id": str(uuid5(NAMESPACE_URL, f"pproc-{proc_id}-{p['id']}")),
                "pessoa_id": p["id"],
                "processo_id": proc_id,
                "papel": "reu",
            })
            adv = rng.choice(advogados)
            rows["processo_advogado"].append({
                "id": str(uuid5(NAMESPACE_URL, f"padv-{proc_id}")),
                "processo_id": proc_id,
                "advogado_id": adv["id"],
                "parte_representada": "reu",
            })

            julg_id = str(uuid5(NAMESPACE_URL, f"julg-{proc_id}"))
            julg_dt = min(end, proc_dt + timedelta(days=rng.integer(15, 180)))
            resultado_julg = "condenado" if series["convicted"] else "absolvido"
            rows["julgamento"].append({
                "id": julg_id,
                "processo_id": proc_id,
                "data": julg_dt.isoformat(),
                "resultado": resultado_julg,
            })

            if series["convicted"]:
                p["tem_antecedente_criminal"] = True
                sent_id = str(uuid5(NAMESPACE_URL, f"sent-{julg_id}"))
                rows["sentenca"].append({
                    "id": sent_id,
                    "julgamento_id": julg_id,
                    "tipo": "condenatória",
                    "descricao": f"Sentença condenatória por {series['crime_type']}",
                })
                months = max(6, int(series["months_sentence"] or 12))
                if series["was_arrested"] and months >= 24:
                    tipo_pena = "prisao"
                    dur_str = f"{months} meses"
                    p["foi_preso"] = True
                    prisao_fim = min(end, julg_dt + timedelta(days=months * 30))
                    p["prisao_periodo"] = (julg_dt.isoformat(), prisao_fim.isoformat())
                    _terminate_overlapping_contracts(
                        p["id"], julg_dt, prisao_fim, existing_tables, persona=p, today=today
                    )
                else:
                    tipo_pena = str(rng.choice(["prestacao_servico", "restritiva", "multa"]))
                    dur_str = f"{months} meses de restrição/serviço"
                rows["pena"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"pena-{sent_id}")),
                    "sentenca_id": sent_id,
                    "tipo": tipo_pena,
                    "duracao_ou_valor": dur_str,
                })
                rows["antecedente_criminal"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"antec-{proc_id}")),
                    "pessoa_id": p["id"],
                    "processo_id": proc_id,
                    "status": "ativo" if p["foi_preso"] else "sancionado",
                })

        # 3. Processos cíveis / trabalhistas / consumidor
        p_civel = CIVIL_LABOR_SUIT_PROB + CIVIL_CONSUMER_SUIT_PROB
        if p.get("estado_civil") == "divorciado":
            p_civel += CIVIL_DIVORCE_SUIT_FACTOR
        if rng.bernoulli(p_civel):
            proc_seq += 1
            cproc_id = str(uuid5(NAMESPACE_URL, f"proc-civ-{p['id']}-{proc_seq}"))
            c_dt = adult_start + timedelta(days=rng.integer(0, max(1, (end - adult_start).days)))
            tipo_civ = (
                "familia:divorcio"
                if p.get("estado_civil") == "divorciado"
                else str(rng.choice(["trabalhista", "civel:consumidor"]))
            )
            trib_idx = 2 if tipo_civ == "trabalhista" else (4 if "familia" in tipo_civ else 3)
            rows["processo"].append({
                "id": cproc_id,
                "numero_ficticio": f"01{proc_seq:05d}-12.{c_dt.year}.5.02.0000",
                "tipo": tipo_civ,
                "tribunal_id": tribunais[trib_idx]["id"],
                "status": str(rng.choice(["em_andamento", "julgado", "arquivado"])),
            })
            rows["pessoa_processo"].append({
                "id": str(uuid5(NAMESPACE_URL, f"pproc-{cproc_id}-{p['id']}")),
                "pessoa_id": p["id"],
                "processo_id": cproc_id,
                "papel": "autor",
            })
            adv = rng.choice(advogados)
            rows["processo_advogado"].append({
                "id": str(uuid5(NAMESPACE_URL, f"padv-{cproc_id}")),
                "processo_id": cproc_id,
                "advogado_id": adv["id"],
                "parte_representada": "autor",
            })

        # 4. Multas administrativas / trânsito
        if rng.bernoulli(0.24):
            m_dt = adult_start + timedelta(days=rng.integer(0, max(1, (end - adult_start).days)))
            rows["multa"].append({
                "id": str(uuid5(NAMESPACE_URL, f"multa-{p['id']}")),
                "pessoa_id": p["id"],
                "tipo": str(rng.choice(["trânsito", "ambiental", "fiscal"])),
                "valor": round(rng.uniform(130.16, 1467.35), 2),
                "data": m_dt.isoformat(),
                "status_pagamento": str(rng.choice(["paga", "pendente", "recurso"])),
            })

    # 5. Contratos jurídicos entre personas adultas
    adults = [p for p in personas if ( _end_date(p, today) - _birth(p) ).days // 365 >= 21]
    for idx in range(0, min(len(adults) - 1, 20), 2):
        pa, pb = adults[idx], adults[idx + 1]
        if pa["id"] == pb["id"]:
            continue
        dt_min = max(_birth(pa), _birth(pb)) + timedelta(days=21 * 365)
        dt_max = min(_end_date(pa, today), _end_date(pb, today))
        if dt_min < dt_max:
            rows["contrato_juridico"].append({
                "id": str(uuid5(NAMESPACE_URL, f"contjur-{pa['id']}-{pb['id']}")),
                "pessoa_id_a": pa["id"],
                "pessoa_id_b": pb["id"],
                "tipo": "prestação de serviços privados",
                "data": dt_min.isoformat(),
                "objeto": "Contrato particular fictício de prestação de serviços",
            })

    return rows
