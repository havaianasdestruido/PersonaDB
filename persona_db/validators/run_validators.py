"""Pure-Python consistency checks for generated dataset snapshots."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import date
from typing import Any

Violation = dict[str, Any]
Check = Callable[[dict[str, list[dict[str, Any]]], date], list[Violation]]


def _date(value: str | None) -> date | None:
    """Parse a nonempty ISO date, or return ``None`` for a missing value.

    Malformed nonempty dates raise ``ValueError``.
    """
    return date.fromisoformat(value) if value else None


def check_people(dataset: dict[str, list[dict[str, Any]]], today: date) -> list[Violation]:
    """Report missing or non-past births and inconsistent death information.

    Birth dates must precede ``today``. Each violation identifies its rule and
    person; invalid nonempty dates propagate date parsing errors.
    """
    problems = []
    for person in dataset.get("pessoa", []):
        born, died = _date(person.get("data_nascimento")), _date(person.get("data_obito"))
        if born is None or born >= today:
            problems.append({"rule": "birth_before_today", "person_id": person.get("id")})
        if died and born and died < born:
            problems.append({"rule": "death_after_birth", "person_id": person.get("id")})
        if died and died > today:
            problems.append({"rule": "death_not_after_today", "person_id": person.get("id")})
        if not person.get("esta_vivo", True) and died is None:
            problems.append({"rule": "dead_person_has_death_date", "person_id": person.get("id")})
    return problems


def check_parentage(dataset: dict[str, list[dict[str, Any]]], today: date) -> list[Violation]:
    """Report parents younger than 14 on their children's birth dates.

    Only parents present in ``pessoa`` are checked. Violations identify both
    people. Missing dates are skipped; malformed dates propagate errors.
    February 29 birthdays reach the next age on March 1 in non-leap years.
    """
    people = {p["id"]: p for p in dataset.get("pessoa", [])}
    problems = []
    for child in people.values():
        for key in ("pai_id", "mae_id"):
            parent_id = child.get(key)
            if parent_id and parent_id in people:
                child_born = _date(child.get("data_nascimento"))
                parent_born = _date(people[parent_id].get("data_nascimento"))
                if child_born is None or parent_born is None:
                    continue
                age = child_born.year - parent_born.year - (
                    (child_born.month, child_born.day) < (parent_born.month, parent_born.day)
                )
                if age < 14:
                    problems.append({"rule": "parent_at_least_14", "person_id": child["id"], "parent_id": parent_id})
    return problems


def check_date_ranges(dataset: dict[str, list[dict[str, Any]]], today: date) -> list[Violation]:
    """Report rows whose end date precedes their start date.

    Checks ``data_inicio`` or ``data_entrada`` against ``data_fim`` or
    ``data_saida``, preferring the first nonempty field in each pair. Non-mapping
    rows are skipped. Only rows with both parsed dates are compared; invalid
    dates propagate parsing errors.
    """
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
    """Report physical rows outside inclusive height and weight bounds.

    Raw ``altura`` values must be 50–250 and ``peso`` values 2–300; no unit
    conversion is applied. Missing, null, and nonnumeric values are violations.
    """
    problems = []
    for row in dataset.get("pessoa_caracteristica_fisica", []):
        try:
            valid = 50 <= float(row.get("altura")) <= 250 and 2 <= float(row.get("peso")) <= 300
        except (TypeError, ValueError):
            valid = False
        if not valid:
            problems.append({"rule": "physical_bounds", "person_id": row.get("pessoa_id")})
    return problems


CHECKS: tuple[Check, ...] = (check_people, check_parentage, check_date_ranges, check_physical_traits)


def validate_dataset(dataset: dict[str, list[dict[str, Any]]], today: date | None = None) -> dict[str, Any]:
    """Return row counts, violations, and a quality score without database access.

    ``today`` defaults to January 1, 2026. Underscore-prefixed entries are
    excluded from row counts. Every violation is counted as critical; the score
    is 100 minus the violation percentage of counted rows (using at least one
    as the denominator), rounded to two decimals and floored at zero. Errors
    from individual checks propagate.
    """
    anchor = today or date(2026, 1, 1)
    violations = [problem for check in CHECKS for problem in check(dataset, anchor)]
    table_rows = {name: rows for name, rows in dataset.items() if not name.startswith("_")}
    total = sum(len(rows) for rows in table_rows.values())
    return {"row_counts": {name: len(rows) for name, rows in sorted(table_rows.items())}, "total_rows": total,
            "violations": violations, "critical_violations": len(violations),
            "quality_score": max(0.0, round(100.0 - 100.0 * len(violations) / max(total, 1), 2))}
