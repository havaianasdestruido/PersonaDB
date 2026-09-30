"""Runner de validação de consistência do PersonaDB (TASK-076).

Executa verificações estruturais e os 6 validadores de domínio (`val_genealogia`,
`val_temporal`, `val_financas`, `val_saude`, `val_juridico`, `val_social`) sobre
o dataset gerado em memória, produzindo relatório estruturado, registros para a
tabela `validacao_consistencia` e relatório HTML opcional.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from persona_db.validators.val_financas import validate_financas
from persona_db.validators.val_genealogia import validate_genealogia
from persona_db.validators.val_juridico import validate_juridico
from persona_db.validators.val_saude import validate_saude
from persona_db.validators.val_social import validate_social
from persona_db.validators.val_temporal import validate_temporal

Violation = dict[str, Any]


def _date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])


def check_people(dataset: dict[str, list[dict[str, Any]]], today: date) -> list[Violation]:
    """Verifica invariantes básicas da tabela central `pessoa`."""
    violations: list[Violation] = []
    seen_ids: set[str] = set()
    for p in dataset.get("pessoa", []):
        pid = p.get("id")
        if not pid or pid in seen_ids:
            violations.append({"domain": "hub", "rule": "unique_person_id", "person_id": pid})
        else:
            seen_ids.add(pid)
        born = _date(p.get("data_nascimento"))
        died = _date(p.get("data_obito"))
        if born is None or born > today:
            violations.append({"domain": "temporal", "rule": "birth_not_future", "person_id": pid, "value": str(born)})
        if died is not None:
            if born and died < born:
                violations.append({"domain": "temporal", "rule": "death_after_birth", "person_id": pid})
            if p.get("esta_vivo", True):
                violations.append({"domain": "temporal", "rule": "dead_flag_matches_obito", "person_id": pid})
        elif not p.get("esta_vivo", True):
            violations.append({"domain": "temporal", "rule": "living_has_no_obito", "person_id": pid})
    return violations


def check_parentage(dataset: dict[str, list[dict[str, Any]]], today: date) -> list[Violation]:
    """Verifica idade parental mínima (>= 14 anos) e ausência de auto-parentesco."""
    violations: list[Violation] = []
    by_id = {p["id"]: p for p in dataset.get("pessoa", []) if "id" in p}
    for p in dataset.get("pessoa", []):
        child_born = _date(p.get("data_nascimento"))
        for key in ("pai_id", "mae_id"):
            parent_id = p.get(key)
            if not parent_id:
                continue
            if parent_id == p["id"]:
                violations.append({"domain": "genealogia", "rule": "no_self_parent", "person_id": p["id"]})
                continue
            parent = by_id.get(parent_id)
            if parent is None or child_born is None:
                continue
            parent_born = _date(parent.get("data_nascimento"))
            if parent_born and (child_born - parent_born).days < 14 * 365:
                violations.append(
                    {
                        "domain": "genealogia",
                        "rule": "parent_at_least_14",
                        "person_id": p["id"],
                        "parent_id": parent_id,
                    }
                )
    return violations


def check_date_ranges(dataset: dict[str, list[dict[str, Any]]], today: date) -> list[Violation]:
    """Verifica pares `data_inicio <= data_fim` e `data_entrada <= data_saida`."""
    violations: list[Violation] = []
    pairs = (
        ("data_inicio", "data_fim"),
        ("data_entrada", "data_saida"),
    )
    for table_name, rows in dataset.items():
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            for start_col, end_col in pairs:
                s = _date(row.get(start_col))
                e = _date(row.get(end_col))
                if s and e and e < s:
                    violations.append(
                        {
                            "domain": "temporal",
                            "rule": "end_before_start",
                            "table": table_name,
                            "start": str(s),
                            "end": str(e),
                        }
                    )
    return violations


def check_physical_traits(dataset: dict[str, list[dict[str, Any]]], today: date) -> list[Violation]:
    """Verifica faixas antropométricas de altura e peso."""
    violations: list[Violation] = []
    for row in dataset.get("pessoa_caracteristica_fisica", []):
        altura = row.get("altura") if row.get("altura") is not None else row.get("altura_cm")
        peso = row.get("peso") if row.get("peso") is not None else row.get("peso_kg")
        if altura is not None and not (50 <= float(altura) <= 250):
            violations.append(
                {"domain": "saude", "rule": "height_out_of_range", "person_id": row.get("pessoa_id"), "value": altura}
            )
        if peso is not None and not (2 <= float(peso) <= 300):
            violations.append(
                {"domain": "saude", "rule": "weight_out_of_range", "person_id": row.get("pessoa_id"), "value": peso}
            )
    return violations


CHECKS = (
    check_people,
    check_parentage,
    check_date_ranges,
    check_physical_traits,
    validate_genealogia,
    validate_temporal,
    validate_financas,
    validate_saude,
    validate_juridico,
    validate_social,
)

DOMAIN_VALIDATORS = {
    "genealogia": validate_genealogia,
    "temporal": validate_temporal,
    "financas": validate_financas,
    "saude": validate_saude,
    "juridico": validate_juridico,
    "social": validate_social,
}


def validate_dataset(
    dataset: dict[str, list[dict[str, Any]]],
    today: date | None = None,
) -> dict[str, Any]:
    """Executa todos os validadores e retorna um relatório consolidado."""
    today = today or date(2026, 4, 19)
    raw_violations: list[Violation] = []
    for check in CHECKS:
        raw_violations.extend(check(dataset, today))

    # Deduplica violações idênticas produzidas por verificadores base e de domínio
    seen_keys: set[str] = set()
    violations: list[Violation] = []
    for v in raw_violations:
        key = json.dumps(v, sort_keys=True, default=str)
        if key not in seen_keys:
            seen_keys.add(key)
            violations.append(v)

    n_people = max(1, len(dataset.get("pessoa", [])))
    domain_consistency: dict[str, float] = {}
    for dom_name, fn in DOMAIN_VALIDATORS.items():
        dom_viols = fn(dataset, today)
        affected = {v.get("person_id") for v in dom_viols if v.get("person_id")}
        err_count = max(len(affected), len(dom_viols))
        pct = max(0.0, 100.0 * (1.0 - min(n_people, err_count) / n_people))
        domain_consistency[dom_name] = round(pct, 2)

    by_rule = dict(Counter(v.get("rule", "unknown") for v in violations))
    overall_pct = round(
        sum(domain_consistency.values()) / max(1, len(domain_consistency)),
        2,
    )
    return {
        "passed": len(violations) == 0,
        "violation_count": len(violations),
        "critical_violations": len(violations),
        "violations": violations,
        "violations_by_rule": by_rule,
        "domain_consistency": domain_consistency,
        "overall_consistency_pct": overall_pct,
        "row_counts": {k: len(v) for k, v in dataset.items() if isinstance(v, list)},
    }


def build_validation_table_rows(
    dataset: dict[str, list[dict[str, Any]]],
    today: date | None = None,
) -> list[dict[str, Any]]:
    """Constrói linhas para a tabela `validacao_consistencia` (Domínio 24)."""
    today = today or date(2026, 4, 19)
    report = validate_dataset(dataset, today=today)
    ts = f"{today.isoformat()}T12:00:00+00:00"
    rows: list[dict[str, Any]] = []
    if report["violations"]:
        for idx, v in enumerate(report["violations"]):
            rows.append({
                "id": str(uuid5(NAMESPACE_URL, f"valcons-viol-{idx}")),
                "tabela": str(v.get("table") or v.get("domain") or "pessoa"),
                "regra_violada": str(v.get("rule", "rule")),
                "registro_id": v.get("person_id"),
                "data": ts,
            })
    else:
        for p in dataset.get("pessoa", [])[:5]:
            rows.append({
                "id": str(uuid5(NAMESPACE_URL, f"valcons-ok-{p['id']}")),
                "tabela": "pessoa",
                "regra_violada": "nenhuma_violacao",
                "registro_id": p["id"],
                "data": ts,
            })
    return rows


def render_html_report(report: dict[str, Any], out_path: str | Path) -> Path:
    """Renderiza um relatório HTML de qualidade dos dados gerados."""
    target = Path(out_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    status_badge = "APROVADO (0 violações)" if report["passed"] else f"REPROVADO ({report['violation_count']} violações)"
    dom_rows = "".join(
        f"<tr><td>{dom}</td><td>{pct:.2f}%</td></tr>"
        for dom, pct in sorted(report.get("domain_consistency", {}).items())
    )
    tbl_rows = "".join(
        f"<tr><td>{tbl}</td><td>{cnt}</td></tr>"
        for tbl, cnt in sorted(report.get("row_counts", {}).items())
    )
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <title>Relatório de Qualidade — PersonaDB</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #1f2937; }}
    h1, h2 {{ color: #111827; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 1.5rem; }}
    th, td {{ border: 1px solid #d1d5db; padding: 0.5rem 0.75rem; text-align: left; }}
    th {{ background: #f3f4f6; }}
  </style>
</head>
<body>
  <h1>Relatório de Consistência — PersonaDB</h1>
  <p><strong>Status:</strong> {status_badge} | <strong>Consistência Geral:</strong> {report.get("overall_consistency_pct", 100.0):.2f}%</p>
  <h2>Consistência por Domínio</h2>
  <table>
    <thead><tr><th>Domínio</th><th>Consistência (%)</th></tr></thead>
    <tbody>{dom_rows}</tbody>
  </table>
  <h2>Contagem de Registros por Tabela ({len(report.get("row_counts", {}))} tabelas)</h2>
  <table>
    <thead><tr><th>Tabela</th><th>Registros</th></tr></thead>
    <tbody>{tbl_rows}</tbody>
  </table>
</body>
</html>
"""
    target.write_text(html, encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:
    """CLI de validação de consistência sobre um dataset sintético."""
    from persona_db.scripts.generate import generate_all

    parser = argparse.ArgumentParser(description="Executa os validadores de consistência do PersonaDB.")
    parser.add_argument("--personas", type=int, default=100, help="Quantidade de personas para validar.")
    parser.add_argument("--seed", type=int, default=7, help="Semente determinística.")
    parser.add_argument("--html-out", type=str, default=None, help="Caminho opcional para salvar relatório HTML.")
    args = parser.parse_args(argv)

    dataset = generate_all(n=args.personas, seed=args.seed)
    report = validate_dataset(dataset)
    if args.html_out:
        render_html_report(report, args.html_out)

    print(
        json.dumps(
            {
                "passed": report["passed"],
                "violation_count": report["violation_count"],
                "overall_consistency_pct": report["overall_consistency_pct"],
                "domain_consistency": report["domain_consistency"],
                "tables_count": len(report["row_counts"]),
                "total_rows": sum(report["row_counts"].values()),
            },
            ensure_ascii=False,
        )
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
