"""Testes do Agent 4: motor criminal."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from persona_db.engines.rng import SeededRNG  # noqa: E402
from persona_db.engines.criminal import CriminalEngine  # noqa: E402


def _rng(seed=42):
    return SeededRNG(seed)


ADVERSE = {
    "sex": "masculino",
    "age": 22,
    "class_label": "D_E",
    "pai_criminal": False,
    "mae_criminal": False,
    "irmao_criminal": False,
    "desemprego": True,
    "abandono_escolar": True,
    "transtorno_mental": False,
    "education": "fundamental",
    "income_annual": 24_000,
}


def test_risk_factors_increase_probability():
    clean = {"sex": "feminino", "age": 40, "class_label": "A"}
    engine = CriminalEngine(_rng(1))
    assert engine.crime_probability(ADVERSE) > engine.crime_probability(clean)


def test_commits_crime_rate_in_range():
    engine = CriminalEngine(_rng(3))
    hits = sum(engine.commits_crime(ADVERSE) for _ in range(2000))
    assert 0.60 <= hits / 2000 <= 0.80


def test_crime_type_valid():
    engine = CriminalEngine(_rng(5))
    for _ in range(200):
        assert engine.crime_type(ADVERSE) in (
            "crimes_violentos", "crimes_patrimoniais", "crimes_digitais",
            "crimes_de_transito", "crimes_corporativos", "trafico",
        )


def test_arrested_class_effect():
    e1 = CriminalEngine(_rng(7))
    e2 = CriminalEngine(_rng(97))  # per-class draws
    n_de = sum(e1.arrested("crimes_patrimoniais", "D_E", 0.4) for _ in range(2000))
    n_a = sum(e2.arrested("crimes_patrimoniais", "A", 0.4) for _ in range(2000))
    assert n_de > n_a


def test_recidivism_reduction():
    e_yes = CriminalEngine(_rng(9))
    e_no = CriminalEngine(_rng(91))
    yes = sum(e_yes.recidivism(True, True) for _ in range(2000))
    no = sum(e_no.recidivism(False, False) for _ in range(2000))
    assert yes < no


def test_determinism():
    r1 = CriminalEngine(_rng(77)).commits_crime(ADVERSE)
    r2 = CriminalEngine(_rng(77)).commits_crime(ADVERSE)
    assert r1 == r2


def test_employment_impact():
    engine = CriminalEngine(_rng(13))
    imp = engine.employment_impact(True, "financeiro")
    assert imp["hiring_multiplier"] == 0.45
    assert imp["blocked"] is True
    assert 0.25 <= imp["salary_reduction"] <= 0.40
    assert "educacao" in imp["barred_sectors"]


def test_pipeline_keys():
    engine = CriminalEngine(_rng(15))
    out = engine.criminal_process_series(ADVERSE)
    for key in ("did_crime", "crime_type", "was_arrested", "months_sentence",
                "convicted", "process_cost", "divorce_impact",
                "employment_impact", "recidivism"):
        assert key in out