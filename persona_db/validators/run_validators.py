"""Pure-Python consistency checks for generated dataset snapshots."""
from __future__ import annotations

from datetime import date
from typing import Any, Callable, Mapping


Violation = dict[str, Any]
Check = Callable[[dict[str, list[dict[str, Any]]], date], list[Violation]]


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def check_people(dataset: dict[str, list[dict[str, Any]]], today: date) -> list[Violation]:
    problems = []
    for person in dataset.get("pessoa", []):
        born, died = _date(person.get("data_nascimento")), _date(person.get("data_obito"))
        if born is None or born >= today:
            problems.append({"rule": "birth_before_today", "person_id": person.get("id")})
        if died and born and died < born:
            problems.append({"rule": "death_after_birth", "person_id": person.get("id")})
        if not person.get("esta_vivo", True) and died is None:
            problems.append({"rule": "dead_person_has_death_date", "person_id": person.get("id")})
    return problems


def check_parentage(dataset: dict[str, list[dict[str, Any]]], today: date) -> list[Violation]:
    people = {p["id"]: p for p in dataset.get("pessoa", [])}
    problems = []
    for child in people.values():
        for key in ("pai_id", "mae_id"):
            parent_id = child.get(key)
            if parent_id and parent_id in people:
                delta = (_date(child["data_nascimento"]) - _date(people[parent_id]["data_nascimento"])).days
                if delta < 14 * 365:
                    problems.append({"rule": "parent_at_least_14", "person_id": child["id"], "parent_id": parent_id})
    return problems


def check_date_ranges(dataset: dict[str, list[dict[str, Any]]], today: date) -> list[Violation]:
    problems = []
    for table, rows in dataset.items():
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            start = _date(row.get("data_inicio") or row.get("data_entrada"))
            end = _date(row.get("data_fim") or row.get("data_saida"))
            if start and end and end < start:
                problems.append({"rule": "end_not_before_start", "table": table, "id": row.get("id")})
    return problems


def check_physical_traits(dataset: dict[str, list[dict[str, Any]]], today: date) -> list[Violation]:
    return [
        {"rule": "physical_bounds", "person_id": row.get("pessoa_id")}
        for row in dataset.get("pessoa_caracteristica_fisica", [])
        if not 50 <= float(row.get("altura", 0)) <= 250 or not 2 <= float(row.get("peso", 0)) <= 300
    ]


CHECKS: tuple[Check, ...] = (check_people, check_parentage, check_date_ranges, check_physical_traits)


def validate_dataset(dataset: dict[str, list[dict[str, Any]]], today: date | None = None) -> dict[str, Any]:
    """Return a serializable quality report; no database is required."""
    anchor = today or date(2026, 1, 1)
    violations = [problem for check in CHECKS for problem in check(dataset, anchor)]
    table_rows = {name: rows for name, rows in dataset.items() if not name.startswith("_")}
    total = sum(len(rows) for rows in table_rows.values())
    return {"row_counts": {name: len(rows) for name, rows in sorted(table_rows.items())}, "total_rows": total,
            "violations": violations, "critical_violations": len(violations),
            "quality_score": max(0.0, round(100.0 - 100.0 * len(violations) / max(total, 1), 2))}
