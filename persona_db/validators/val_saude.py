"""val_saude — validador de consistência médica, hospitalar e fisiológica (TASK-073).

Regras verificadas:
- Tipo sanguíneo consistente entre `pessoa` e `pessoa_caracteristica_fisica`.
- Prescrições (`prescricao`) apenas para pessoas com diagnósticos registrados
  (`doenca_pessoa`, `condicao_cronica` ou `saude_mental_registro`).
- Cirurgias (`cirurgia`) apenas para pacientes com diagnóstico (`doenca_pessoa`).
- Vacinas (`vacina_dose`) com números de dose positivos e intervalo mínimo (>= 14 dias)
  respeitado entre doses consecutivas da mesma vacina.
- Internações (`internacao`) com `data_entrada < data_saida`.
- Altas hospitalares (`alta_hospitalar`) referenciando internação existente.
- Peso (`2..300` kg) e altura (`50..250` cm) dentro de limites fisiológicos.
"""
from __future__ import annotations

from datetime import date
from typing import Any

Violation = dict[str, Any]


def _date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])


def validate_saude(
    dataset: dict[str, list[dict[str, Any]]],
    today: date | None = None,
) -> list[Violation]:
    """Executa todas as verificações de consistência de saúde."""
    violations: list[Violation] = []
    people = {p["id"]: p for p in dataset.get("pessoa", []) if "id" in p}
    traits = {
        r["pessoa_id"]: r
        for r in dataset.get("pessoa_caracteristica_fisica", [])
        if "pessoa_id" in r
    }

    # 1. Consistência de tipo sanguíneo e limites fisiológicos de peso e altura
    for pid, r in traits.items():
        p = people.get(pid)
        if p:
            if p.get("tipo_sanguineo") and r.get("tipo_sanguineo") != p.get("tipo_sanguineo"):
                violations.append({
                    "domain": "saude",
                    "rule": "blood_type_mismatch",
                    "person_id": pid,
                })
            if p.get("fator_rh") and r.get("fator_rh") != p.get("fator_rh"):
                violations.append({
                    "domain": "saude",
                    "rule": "rh_factor_mismatch",
                    "person_id": pid,
                })
        alt = float(r.get("altura") if r.get("altura") is not None else (r.get("altura_cm") or 0.0))
        peso = float(r.get("peso") if r.get("peso") is not None else (r.get("peso_kg") or 0.0))
        if not (50.0 <= alt <= 250.0):
            violations.append({
                "domain": "saude",
                "rule": "height_out_of_range",
                "person_id": pid,
                "value": alt,
            })
        if not (2.0 <= peso <= 300.0):
            violations.append({
                "domain": "saude",
                "rule": "weight_out_of_range",
                "person_id": pid,
                "value": peso,
            })

    # 2. Prescrições exigem condição diagnosticada
    diagnosed_people: set[str] = set()
    for tbl in ("doenca_pessoa", "condicao_cronica", "saude_mental_registro"):
        for row in dataset.get(tbl, []):
            if row.get("pessoa_id"):
                diagnosed_people.add(row["pessoa_id"])

    for pr in dataset.get("prescricao", []):
        pid = pr.get("pessoa_id")
        if pid not in diagnosed_people:
            violations.append({
                "domain": "saude",
                "rule": "prescription_without_diagnosis",
                "person_id": pid,
                "prescricao_id": pr.get("id"),
            })

    # 3. Cirurgias exigem diagnóstico em doenca_pessoa
    disease_people = {r.get("pessoa_id") for r in dataset.get("doenca_pessoa", []) if r.get("pessoa_id")}
    for cir in dataset.get("cirurgia", []):
        pid = cir.get("pessoa_id")
        if pid not in disease_people:
            violations.append({
                "domain": "saude",
                "rule": "surgery_without_diagnosis",
                "person_id": pid,
                "cirurgia_id": cir.get("id"),
            })

    # 4. Doses de vacina e intervalos mínimos (>= 14 dias entre doses consecutivas)
    doses_by_person_vac: dict[tuple[str, str], list[tuple[int, date]]] = {}
    for vd in dataset.get("vacina_dose", []):
        pid = vd.get("pessoa_id")
        vid = vd.get("vacina_id")
        num = int(vd.get("dose_numero") or 0)
        dt = _date(vd.get("data"))
        if num < 1:
            violations.append({
                "domain": "saude",
                "rule": "invalid_vaccine_dose_number",
                "person_id": pid,
            })
        if pid and vid and dt:
            doses_by_person_vac.setdefault((pid, vid), []).append((num, dt))

    for (pid, vid), dose_list in doses_by_person_vac.items():
        dose_list.sort(key=lambda item: item[0])
        for idx in range(1, len(dose_list)):
            prev_num, prev_dt = dose_list[idx - 1]
            cur_num, cur_dt = dose_list[idx]
            if cur_num <= prev_num or (cur_dt - prev_dt).days < 14:
                violations.append({
                    "domain": "saude",
                    "rule": "vaccine_interval_violation",
                    "person_id": pid,
                    "vacina_id": vid,
                })

    # 5. Internações com data_entrada < data_saida e altas hospitalares válidas
    internacoes = {i["id"]: i for i in dataset.get("internacao", []) if "id" in i}
    for iid, inter in internacoes.items():
        de = _date(inter.get("data_entrada"))
        ds = _date(inter.get("data_saida"))
        if de and ds and ds <= de:
            violations.append({
                "domain": "saude",
                "rule": "hospitalization_invalid_dates",
                "internacao_id": iid,
            })

    for alta in dataset.get("alta_hospitalar", []):
        if alta.get("internacao_id") not in internacoes:
            violations.append({
                "domain": "saude",
                "rule": "discharge_without_hospitalization",
                "alta_id": alta.get("id"),
                "internacao_id": alta.get("internacao_id"),
            })

    return violations
