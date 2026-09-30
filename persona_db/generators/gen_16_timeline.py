"""gen_16_timeline — domínio 16: consolidação da linha do tempo, marcos pessoais e luto.

Implementa TASK-054 de TODO.MD (roda por último entre os geradores de domínio):
- Consolida todos os eventos relevantes da vida da persona (`nascimento`,
  `formatura`, `primeiro_emprego`, `casamento`, `divorcio`, `nascimento_filho`,
  `diagnostico_doenca`, `processo_criminal`, `compra_imovel`, `obito`) em
  `evento_vida`.
- Ordena cronologicamente em `linha_do_tempo` e atribui importância 1-10 em
  `marco_historico_pessoal`.
- Cruza com falecimentos de parentes para preencher `luto_ficticio`.
- Registra a semente determinística de cada persona em `semente_aleatoria`.
"""
from __future__ import annotations

import os
import sys
from datetime import date
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

_IMPORTANCIA_EVENTO: dict[str, int] = {
    "nascimento": 10,
    "nascimento_filho": 10,
    "casamento": 9,
    "divorcio": 8,
    "morte_parente": 9,
    "formatura": 8,
    "primeiro_emprego": 8,
    "compra_imovel": 8,
    "diagnostico_doenca": 7,
    "processo_criminal": 7,
    "obito": 10,
}


def _birth(p: dict[str, Any]) -> date:
    return date.fromisoformat(p["data_nascimento"])


def generate(
    personas: list[dict[str, Any]],
    seed: int = 7,
    today: date | None = None,
    existing_tables: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Gera todas as tabelas do domínio 16 (Timeline & Eventos) e `semente_aleatoria`."""
    today = today or simulation_today()
    master = new_rng(seed)
    tables = existing_tables or {}

    rows: dict[str, list[dict[str, Any]]] = {
        "evento_vida": [],
        "marco_historico_pessoal": [],
        "linha_do_tempo": [],
        "aniversario": [],
        "comemoracao": [],
        "luto_ficticio": [],
        "semente_aleatoria": [],
    }

    by_id = {p["id"]: p for p in personas}

    # Índices rápidos por pessoa nas tabelas já geradas
    first_job_by_person: dict[str, str] = {}
    for c in tables.get("contrato_trabalho", []):
        pid = c.get("pessoa_id")
        dt = c.get("data_inicio")
        if pid and dt and (pid not in first_job_by_person or dt < first_job_by_person[pid]):
            first_job_by_person[pid] = dt

    diag_by_person: dict[str, str] = {}
    for dp in tables.get("doenca_pessoa", []):
        pid = dp.get("pessoa_id")
        dt = dp.get("data_diagnostico")
        if pid and dt and (pid not in diag_by_person or dt < diag_by_person[pid]):
            diag_by_person[pid] = dt

    children_births_by_parent: dict[str, list[str]] = {}
    for ch in personas:
        for pk in ("pai_id", "mae_id"):
            par_id = ch.get(pk)
            if par_id:
                children_births_by_parent.setdefault(par_id, []).append(ch["data_nascimento"])

    for p in personas:
        rng = master.fork(p["id"], "gen16-timeline")
        pid = p["id"]
        born_str = p["data_nascimento"]

        # Semente aleatória determinística (Domínio 24 / TASK-002 / TASK-040)
        rows["semente_aleatoria"].append({
            "id": str(uuid5(NAMESPACE_URL, f"seed-{pid}")),
            "pessoa_id": pid,
            "seed_valor": f"seed={seed}|persona={pid}",
        })

        # Aniversários comemorativos
        rows["aniversario"].append({
            "id": str(uuid5(NAMESPACE_URL, f"aniv-nasc-{pid}")),
            "pessoa_id": pid,
            "tipo": "nascimento",
            "data": born_str,
        })
        if p.get("data_casamento"):
            rows["aniversario"].append({
                "id": str(uuid5(NAMESPACE_URL, f"aniv-cas-{pid}")),
                "pessoa_id": pid,
                "tipo": "casamento",
                "data": p["data_casamento"],
            })
        if first_job_by_person.get(pid):
            rows["aniversario"].append({
                "id": str(uuid5(NAMESPACE_URL, f"aniv-emp-{pid}")),
                "pessoa_id": pid,
                "tipo": "emprego",
                "data": first_job_by_person[pid],
            })
        if p.get("ensino_superior_concluido_em"):
            rows["aniversario"].append({
                "id": str(uuid5(NAMESPACE_URL, f"aniv-form-{pid}")),
                "pessoa_id": pid,
                "tipo": "formatura",
                "data": p["ensino_superior_concluido_em"],
            })

        # Coleta eventos de vida da persona
        raw_events: list[tuple[str, str, str]] = [
            (born_str, "nascimento", f"Nascimento em {p.get('cidade_nascimento', 'Brasil')}"),
        ]
        if p.get("ensino_medio_concluido_em"):
            raw_events.append((p["ensino_medio_concluido_em"], "formatura", "Conclusão do Ensino Médio"))
        if p.get("ensino_superior_concluido_em"):
            raw_events.append((p["ensino_superior_concluido_em"], "formatura", "Conclusão do Ensino Superior"))
        if first_job_by_person.get(pid):
            raw_events.append((first_job_by_person[pid], "primeiro_emprego", "Início do primeiro vínculo de trabalho"))
        if p.get("data_casamento"):
            raw_events.append((p["data_casamento"], "casamento", "Celebração de casamento civil"))
        if p.get("data_divorcio"):
            raw_events.append((p["data_divorcio"], "divorcio", "Averbação de divórcio"))
        for idx_ch, ch_dt in enumerate(sorted(children_births_by_parent.get(pid, []))):
            raw_events.append((ch_dt, "nascimento_filho", f"Nascimento do(a) {idx_ch + 1}º filho(a)"))
        if diag_by_person.get(pid):
            raw_events.append((diag_by_person[pid], "diagnostico_doenca", "Diagnóstico médico relevante"))

        # Luto por falecimento de pai ou mãe
        for rel_label, par_key in (("pai", "pai_id"), ("mae", "mae_id")):
            par_id = p.get(par_key)
            par = by_id.get(par_id) if par_id else None
            if par and not par.get("esta_vivo") and par.get("data_obito"):
                ob_str = par["data_obito"]
                if ob_str >= born_str and (not p.get("data_obito") or ob_str <= p["data_obito"]):
                    rows["luto_ficticio"].append({
                        "id": str(uuid5(NAMESPACE_URL, f"luto-{pid}-{par_id}")),
                        "pessoa_id": pid,
                        "pessoa_id_falecido": par_id,
                        "data": ob_str,
                        "relacao": rel_label,
                    })
                    raw_events.append((ob_str, "morte_parente", f"Falecimento de {rel_label}"))

        if p.get("data_obito"):
            raw_events.append((p["data_obito"], "obito", "Registro de óbito"))

        # Ordena cronologicamente e insere em evento_vida, linha_do_tempo e marco_historico_pessoal
        raw_events.sort(key=lambda item: (item[0], item[1]))
        for order_idx, (ev_dt, ev_tipo, ev_desc) in enumerate(raw_events, start=1):
            ev_id = str(uuid5(NAMESPACE_URL, f"evvida-{pid}-{order_idx}-{ev_tipo}"))
            rows["evento_vida"].append({
                "id": ev_id,
                "pessoa_id": pid,
                "data": ev_dt,
                "tipo_evento": ev_tipo,
                "descricao": ev_desc,
            })
            rows["linha_do_tempo"].append({
                "id": str(uuid5(NAMESPACE_URL, f"ldt-{ev_id}")),
                "pessoa_id": pid,
                "evento_vida_id": ev_id,
                "ordem_cronologica": order_idx,
            })
            imp = _IMPORTANCIA_EVENTO.get(ev_tipo, 6)
            rows["marco_historico_pessoal"].append({
                "id": str(uuid5(NAMESPACE_URL, f"marco-{ev_id}")),
                "pessoa_id": pid,
                "evento_vida_id": ev_id,
                "importancia": imp,
            })
            if ev_tipo in ("casamento", "formatura") and rng.bernoulli(0.65):
                rows["comemoracao"].append({
                    "id": str(uuid5(NAMESPACE_URL, f"comem-{ev_id}")),
                    "pessoa_id": pid,
                    "evento_vida_id": ev_id,
                    "local_endereco_id": p.get("endereco_atual_id"),
                    "convidados_ficticios": rng.integer(15, 120),
                })

    return rows
