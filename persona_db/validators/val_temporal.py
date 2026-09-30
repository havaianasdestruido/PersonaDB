"""val_temporal — validador de consistência temporal transversal (TASK-071).

Regras verificadas:
- `data_fim >= data_inicio` em todas as tabelas com pares de data (`data_inicio`/`data_fim`,
  `data_entrada`/`data_saida`, `data_ida`/`data_volta`).
- Casamento após 16 anos de idade para ambos os cônjuges.
- Primeiro emprego após 14 anos (menor aprendiz / estágio / temporário) ou 18 anos (CLT / PJ / público).
- Ensino superior (`superior` / `pos`) somente após conclusão do ensino médio.
- Diagnósticos de doença após o nascimento e antes ou na data de óbito.
- Processos criminais com datas coerentes com a maioridade penal (18+ anos).
- Viagens internacionais com passaporte válido na data de retorno.
- Filhos nascidos com mãe em idade fértil (14-50 anos) e pai em faixa reprodutiva (14-70 anos).
"""
from __future__ import annotations

from datetime import date
from typing import Any

Violation = dict[str, Any]


def _date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])


def validate_temporal(
    dataset: dict[str, list[dict[str, Any]]],
    today: date | None = None,
) -> list[Violation]:
    """Executa todas as verificações de consistência temporal transversal."""
    violations: list[Violation] = []
    people = {p["id"]: p for p in dataset.get("pessoa", []) if "id" in p}

    # 1. Intervalos início/fim em qualquer tabela
    date_pairs = (
        ("data_inicio", "data_fim"),
        ("data_entrada", "data_saida"),
        ("data_ida", "data_volta"),
    )
    for table_name, rows in dataset.items():
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            for start_col, end_col in date_pairs:
                s = _date(row.get(start_col))
                e = _date(row.get(end_col))
                if s and e and e < s:
                    violations.append({
                        "domain": "temporal",
                        "rule": "end_before_start",
                        "table": table_name,
                        "start": s.isoformat(),
                        "end": e.isoformat(),
                    })

    # 2. Casamento >= 16 anos para ambos os cônjuges
    for cas in dataset.get("casamento", []):
        dt = _date(cas.get("data"))
        if not dt:
            continue
        for col in ("pessoa_id_a", "pessoa_id_b"):
            p = people.get(cas.get(col))
            if p:
                b = _date(p.get("data_nascimento"))
                if b and (dt - b).days < 16 * 365:
                    violations.append({
                        "domain": "temporal",
                        "rule": "marriage_under_16",
                        "person_id": p["id"],
                        "marriage_date": dt.isoformat(),
                    })

    # 3. Primeiro emprego >= 14 anos (aprendiz/estágio/temporário) ou >= 18 anos (CLT/PJ/público)
    for ct in dataset.get("contrato_trabalho", []):
        p = people.get(ct.get("pessoa_id"))
        dt = _date(ct.get("data_inicio"))
        if p and dt:
            b = _date(p.get("data_nascimento"))
            if b:
                age_days = (dt - b).days
                tipo = ct.get("tipo_contrato", "CLT")
                min_days = 14 * 365 if tipo in ("estagio", "temporario", "autonomo") else 18 * 365
                if age_days < min_days:
                    violations.append({
                        "domain": "temporal",
                        "rule": "employment_underage",
                        "person_id": p["id"],
                        "tipo_contrato": tipo,
                        "start_date": dt.isoformat(),
                    })

    # 4. Ensino superior após conclusão do ensino médio
    cursos_nivel = {c["id"]: c.get("nivel") for c in dataset.get("curso", []) if "id" in c}
    mats_by_person: dict[str, list[dict[str, Any]]] = {}
    for m in dataset.get("matricula", []):
        pid = m.get("pessoa_id")
        if pid:
            mats_by_person.setdefault(pid, []).append(m)

    for pid, mats in mats_by_person.items():
        medio_end: date | None = None
        for m in mats:
            if cursos_nivel.get(m.get("curso_id")) in ("medio", "tecnico") and m.get("status") in ("concluida", "concluido"):
                df = _date(m.get("data_fim"))
                if df and (medio_end is None or df < medio_end):
                    medio_end = df
        for m in mats:
            if cursos_nivel.get(m.get("curso_id")) in ("superior", "pos"):
                di = _date(m.get("data_inicio"))
                if medio_end is None or (di and di < medio_end):
                    violations.append({
                        "domain": "temporal",
                        "rule": "higher_ed_before_high_school",
                        "person_id": pid,
                    })

    # 5. Diagnósticos de doença dentro de [nascimento, óbito]
    for tbl in ("doenca_pessoa", "condicao_cronica"):
        for row in dataset.get(tbl, []):
            p = people.get(row.get("pessoa_id"))
            dt = _date(row.get("data_diagnostico"))
            if p and dt:
                b = _date(p.get("data_nascimento"))
                d = _date(p.get("data_obito"))
                if (b and dt < b) or (d and dt > d):
                    violations.append({
                        "domain": "temporal",
                        "rule": "diagnosis_outside_lifespan",
                        "table": tbl,
                        "person_id": p["id"],
                        "date": dt.isoformat(),
                    })

    # 6. Processos criminais com idade >= 18 anos
    for proc in dataset.get("processo", []):
        if proc.get("tipo") == "criminal":
            p = people.get(proc.get("pessoa_id_reu"))
            dt = _date(proc.get("data_abertura"))
            if p and dt:
                b = _date(p.get("data_nascimento"))
                if b and (dt - b).days < 18 * 365:
                    violations.append({
                        "domain": "temporal",
                        "rule": "criminal_process_under_18",
                        "person_id": p["id"],
                        "process_id": proc.get("id"),
                    })

    # 7. Viagens internacionais com passaporte válido na data da volta
    passports_by_person: dict[str, list[date]] = {}
    for dv in dataset.get("documento_viagem", []):
        if dv.get("tipo") == "passaporte" and dv.get("pessoa_id") and dv.get("validade"):
            v = _date(dv.get("validade"))
            if v:
                passports_by_person.setdefault(dv["pessoa_id"], []).append(v)
    for pd in dataset.get("pessoa_documento", []):
        if pd.get("tipo_documento") == "passaporte" and pd.get("pessoa_id") and pd.get("data_validade"):
            v = _date(pd.get("data_validade"))
            if v:
                passports_by_person.setdefault(pd["pessoa_id"], []).append(v)

    dest_pais = {d["id"]: d.get("pais") for d in dataset.get("destino", []) if "id" in d}
    for vg in dataset.get("viagem", []):
        pais = dest_pais.get(vg.get("destino_id"), "Brasil")
        if pais and pais != "Brasil":
            pid = vg.get("pessoa_id")
            volta = _date(vg.get("data_volta")) or _date(vg.get("data_ida"))
            valid_dates = passports_by_person.get(pid, [])
            if not valid_dates or (volta and max(valid_dates) < volta):
                violations.append({
                    "domain": "temporal",
                    "rule": "international_trip_without_valid_passport",
                    "person_id": pid,
                    "viagem_id": vg.get("id"),
                })

    # 8. Idade fértil da mãe (14-50 anos) e do pai (14-70 anos) no nascimento do filho
    for child in people.values():
        cb = _date(child.get("data_nascimento"))
        if not cb:
            continue
        mae = people.get(child.get("mae_id")) if child.get("mae_id") else None
        if mae:
            mb = _date(mae.get("data_nascimento"))
            if mb:
                age_m = (cb - mb).days / 365.25
                if age_m < 14.0 or age_m > 50.5:
                    violations.append({
                        "domain": "temporal",
                        "rule": "mother_outside_fertile_age",
                        "person_id": child["id"],
                        "mother_id": mae["id"],
                        "mother_age": round(age_m, 2),
                    })
        pai = people.get(child.get("pai_id")) if child.get("pai_id") else None
        if pai:
            pb = _date(pai.get("data_nascimento"))
            if pb:
                age_p = (cb - pb).days / 365.25
                if age_p < 14.0 or age_p > 70.5:
                    violations.append({
                        "domain": "temporal",
                        "rule": "father_outside_reproductive_age",
                        "person_id": child["id"],
                        "father_id": pai["id"],
                        "father_age": round(age_p, 2),
                    })

    return violations
