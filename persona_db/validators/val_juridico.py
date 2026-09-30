"""val_juridico — validador de consistência jurídica, penal e eleitoral (TASK-074).

Regras verificadas:
- Votos (`voto`) emitidos apenas por cidadãos maiores de 16 anos na data da eleição.
- Candidatos (`candidato`) filiados (`filiacao_partidaria`) ao partido que representam.
- Sentenças (`sentenca`) referenciando julgamentos existentes (`julgamento`).
- Penas (`pena`) referenciando sentenças existentes (`sentenca`).
- Antecedentes criminais (`antecedente_criminal`) referenciando processos existentes (`processo`).
- Pessoas em cumprimento de pena de prisão não possuem contrato de trabalho (`contrato_trabalho`)
  ativo sobreposto ao período de reclusão.
- Todo processo (`processo`) possui pelo menos um advogado constituído (`processo_advogado`).
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

Violation = dict[str, Any]


def _date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])


def validate_juridico(
    dataset: dict[str, list[dict[str, Any]]],
    today: date | None = None,
) -> list[Violation]:
    """Executa todas as verificações de consistência jurídico-eleitoral."""
    violations: list[Violation] = []
    people = {p["id"]: p for p in dataset.get("pessoa", []) if "id" in p}
    eleicoes = {e["id"]: e for e in dataset.get("eleicao", []) if "id" in e}
    processos = {pr["id"]: pr for pr in dataset.get("processo", []) if "id" in pr}
    julgamentos = {j["id"]: j for j in dataset.get("julgamento", []) if "id" in j}
    sentencas = {s["id"]: s for s in dataset.get("sentenca", []) if "id" in s}

    # 1. Votos apenas para maiores de 16 anos na data da eleição
    for v in dataset.get("voto", []):
        p = people.get(v.get("pessoa_id"))
        el = eleicoes.get(v.get("eleicao_id"))
        if p and el:
            b = _date(p.get("data_nascimento"))
            ed = _date(el.get("data"))
            if b and ed and (ed - b).days < 16 * 365:
                violations.append({
                    "domain": "juridico",
                    "rule": "voter_under_16",
                    "person_id": p["id"],
                    "eleicao_id": el["id"],
                })

    # 2. Candidatos filiados ao partido representado
    filiacoes_pairs = {
        (f.get("pessoa_id"), f.get("partido_id"))
        for f in dataset.get("filiacao_partidaria", [])
    }
    for cand in dataset.get("candidato", []):
        pair = (cand.get("pessoa_id"), cand.get("partido_id"))
        if pair not in filiacoes_pairs:
            violations.append({
                "domain": "juridico",
                "rule": "candidate_without_party_affiliation",
                "candidato_id": cand.get("id"),
                "person_id": cand.get("pessoa_id"),
                "partido_id": cand.get("partido_id"),
            })

    # 3. Cadeia referencial sentença -> julgamento, pena -> sentença, antecedente -> processo
    for s in dataset.get("sentenca", []):
        if s.get("julgamento_id") not in julgamentos:
            violations.append({
                "domain": "juridico",
                "rule": "sentence_without_judgment",
                "sentenca_id": s.get("id"),
            })

    for pn in dataset.get("pena", []):
        if pn.get("sentenca_id") not in sentencas:
            violations.append({
                "domain": "juridico",
                "rule": "penalty_without_sentence",
                "pena_id": pn.get("id"),
            })

    for ant in dataset.get("antecedente_criminal", []):
        if ant.get("processo_id") not in processos:
            violations.append({
                "domain": "juridico",
                "rule": "criminal_record_without_process",
                "antecedente_id": ant.get("id"),
            })

    # 4. Todo processo deve ter pelo menos um advogado registrado
    procs_with_lawyer = {
        pa.get("processo_id")
        for pa in dataset.get("processo_advogado", [])
        if pa.get("processo_id")
    }
    for proc_id in processos:
        if proc_id not in procs_with_lawyer:
            violations.append({
                "domain": "juridico",
                "rule": "process_without_lawyer",
                "processo_id": proc_id,
            })

    # 5. Pessoas em prisão não têm contrato de trabalho sobreposto ao período de prisão
    contratos_by_person: dict[str, list[dict[str, Any]]] = {}
    for ct in dataset.get("contrato_trabalho", []):
        pid = ct.get("pessoa_id")
        if pid:
            contratos_by_person.setdefault(pid, []).append(ct)

    for pn in dataset.get("pena", []):
        if pn.get("tipo") != "prisao":
            continue
        sent = sentencas.get(pn.get("sentenca_id"))
        julg = julgamentos.get(sent.get("julgamento_id")) if sent else None
        proc = processos.get(julg.get("processo_id")) if julg else None
        if not (julg and proc):
            continue
        reu_id = proc.get("pessoa_id_reu")
        p_start = _date(julg.get("data"))
        dur_days = int(pn.get("duracao_dias") or 365)
        if not (reu_id and p_start):
            continue
        p_end = p_start + timedelta(days=dur_days)
        for ct in contratos_by_person.get(reu_id, []):
            c_ini = _date(ct.get("data_inicio"))
            c_fim = _date(ct.get("data_fim")) or date(9999, 12, 31)
            if c_ini and c_ini <= p_end and c_fim >= p_start:
                violations.append({
                    "domain": "juridico",
                    "rule": "active_employment_during_imprisonment",
                    "person_id": reu_id,
                    "contrato_id": ct.get("id"),
                    "pena_id": pn.get("id"),
                })

    return violations
