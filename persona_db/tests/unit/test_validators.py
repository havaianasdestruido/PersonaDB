from datetime import date

import pytest

from persona_db.validators import validate_dataset


TODAY = date(2026, 1, 1)


@pytest.mark.parametrize(
    ("death", "rules"),
    [
        ("2026-01-02", ["death_not_after_today"]),
        ("2026-01-01", []),
        ("1999-12-31", ["death_after_birth"]),
    ],
)
def test_death_date_boundaries(death, rules):
    report = validate_dataset(
        {"pessoa": [{"id": 1, "data_nascimento": "2000-01-01", "data_obito": death}]},
        today=TODAY,
    )
    assert [v["rule"] for v in report["violations"]] == rules
    assert report["critical_violations"] == len(rules)


@pytest.mark.parametrize("missing_person", [0, 1])
@pytest.mark.parametrize("missing_value", [None, "", "absent"])
@pytest.mark.parametrize("parent_key", ["pai_id", "mae_id"])
def test_missing_birth_date_reports_violation(missing_person, missing_value, parent_key):
    people = [
        {"id": 1, "data_nascimento": "1980-01-01"},
        {"id": 2, "data_nascimento": "2000-01-01", parent_key: 1},
    ]
    if missing_value == "absent":
        del people[missing_person]["data_nascimento"]
    else:
        people[missing_person]["data_nascimento"] = missing_value
    report = validate_dataset({"pessoa": people}, today=TODAY)
    assert report["violations"] == [
        {"rule": "birth_before_today", "person_id": people[missing_person]["id"]}
    ]
    assert report["critical_violations"] == 1


@pytest.mark.parametrize(
    ("parent_birth", "child_birth", "invalid"),
    [
        ("2000-06-15", "2014-06-14", True),
        ("2000-06-15", "2014-06-15", False),
        ("2000-06-15", "2014-06-16", False),
        ("2000-02-29", "2014-02-28", True),
        ("2000-02-29", "2014-03-01", False),
    ],
)
def test_parent_calendar_age(parent_birth, child_birth, invalid):
    report = validate_dataset(
        {"pessoa": [
            {"id": 1, "data_nascimento": parent_birth},
            {"id": 2, "data_nascimento": child_birth, "pai_id": 1},
        ]},
        today=TODAY,
    )
    expected = [{"rule": "parent_at_least_14", "person_id": 2, "parent_id": 1}]
    assert report["violations"] == (expected if invalid else [])


@pytest.mark.parametrize("field", ["altura", "peso"])
@pytest.mark.parametrize("value", [None, "invalid", [], {}, float("nan"), float("inf")])
def test_invalid_physical_values_are_reported(field, value):
    row = {"pessoa_id": 1, "altura": 175, "peso": 70, field: value}
    report = validate_dataset({"pessoa_caracteristica_fisica": [row]}, today=TODAY)
    assert report["violations"] == [{"rule": "physical_bounds", "person_id": 1}]
    assert report["critical_violations"] == 1


@pytest.mark.parametrize(
    ("height", "weight", "invalid"),
    [(50, 2, False), (250, 300, False), ("175", "70", False),
     (49, 70, True), (251, 70, True), (175, 1, True), (175, 301, True)],
)
def test_physical_numeric_bounds(height, weight, invalid):
    report = validate_dataset(
        {"pessoa_caracteristica_fisica": [{"pessoa_id": 1, "altura": height, "peso": weight}]},
        today=TODAY,
    )
    assert report["critical_violations"] == int(invalid)
