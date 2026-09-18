"""Testes do Agent 3: genetics, family e geography engines."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from persona_db.engines.rng import SeededRNG  # noqa: E402
from persona_db.engines.genetics import GeneticEngine  # noqa: E402
from persona_db.engines.family import FamilyEngine  # noqa: E402
from persona_db.engines.geography import GeographyEngine, CITY_SET, NEIGHBORHOODS  # noqa: E402


def _rng(seed=42):
    return SeededRNG(seed)


def test_punnett_oo_only_O():
    chart = GeneticEngine.punnett_abo("O", "O")
    assert set(chart.keys()) == {"O"}
    assert chart["O"] == 1.0


def test_punnett_AO_contains_O():
    chart = GeneticEngine.punnett_abo("A", "O")
    assert "O" in chart


def test_blue_eyes_from_bb_parents():
    engine = GeneticEngine(_rng())
    chart = engine.eye_color_chart(("b", "b"), ("b", "b"))
    assert chart["azul"] == 1.0


def test_blood_OO_never_B_AB():
    for _ in range(50):
        res = GeneticEngine(_rng(7)).herdar_tipo_sanguineo("O", "O", "positivo", "positivo")
        assert res[0] == "O"


def test_handedness_ordering():
    both = GeneticEngine.handedness_prob(True, True)
    father = GeneticEngine.handedness_prob(True, False)
    mother = GeneticEngine.handedness_prob(False, True)
    none = GeneticEngine.handedness_prob(False, False)
    assert both > father > none
    assert both > mother > none
    assert 0.2 <= both <= 0.32


def test_tall_parents_tall_children():
    engine = GeneticEngine(_rng(11))
    heights = [engine.expected_child_height(190, 175, "M") for _ in range(1000)]
    assert sum(heights) / len(heights) > 178.0


def test_height_determinism():
    a = GeneticEngine(_rng(99)).expected_child_height(180, 165, "F")
    b = GeneticEngine(_rng(99)).expected_child_height(180, 165, "F")
    assert a == b


def test_children_count_class_order():
    fe = FamilyEngine(_rng(5))
    n_a = sum(fe.children_count("B1", {}) for _ in range(2000)) / 2000
    n_de = sum(fe.children_count("D_E", {}) for _ in range(2000)) / 2000
    assert n_de > n_a


def test_children_determinism():
    assert FamilyEngine(_rng(3)).children_count("C1", {}) == FamilyEngine(_rng(3)).children_count("C1", {})


def test_geography_sizes():
    assert len(CITY_SET) >= 50
    assert len(NEIGHBORHOODS) >= 400


def test_geography_references():
    ids = {c["city_id"] for c in CITY_SET}
    for b in NEIGHBORHOODS:
        assert b["city_id"] in ids


def test_city_for_class_returns_valid():
    geo = GeographyEngine(_rng(2))
    city = geo.city_for_class("A")
    assert city in CITY_SET


def test_gravity_model_sane():
    geo = GeographyEngine(_rng(2))
    flow_near = geo.gravity_model(1_000_000, 2_000_000, 50)
    flow_far = geo.gravity_model(1_000_000, 2_000_000, 500)
    assert flow_near > flow_far
    assert geo.gravity_model(1, 1, 1) > 0