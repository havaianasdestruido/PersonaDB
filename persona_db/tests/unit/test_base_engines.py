"""Unit tests for Agent 2 engines: rng, socio, health.

Self-contained, deterministic, fixed-seed. Uses pytest.importorskip for
optional deps so collection never fails.
"""
from __future__ import annotations

import math
import os
import sys

import pytest

# Ensure project root (parent of persona_db package) is importable.
# tests/unit -> project root requires three parents.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "persona_db"))

np = pytest.importorskip("numpy")

from persona_db.engines.rng import SeededRNG, new_rng
from persona_db.engines.socio import SocioeconomicEngine
from persona_db.engines.health import HealthEngine


# ======================================================================
# SeededRNG tests
# ======================================================================


class TestSeededRNG:
    """Determinism and distribution basics for SeededRNG."""

    def test_deterministic_same_params(self):
        """Same seed+persona+domain => identical sequences."""
        r1 = SeededRNG(42).fork("p1", "dom")
        r2 = SeededRNG(42).fork("p1", "dom")
        seq1 = [r1.normal(0, 1) for _ in range(20)]
        seq2 = [r2.normal(0, 1) for _ in range(20)]
        assert seq1 == seq2

    def test_fork_different_persona(self):
        """Different persona => different sequences."""
        r1 = SeededRNG(42).fork("p1", "dom")
        r2 = SeededRNG(42).fork("p2", "dom")
        assert [r1.normal(0, 1) for _ in range(50)] != [r2.normal(0, 1) for _ in range(50)]

    def test_fork_different_domain(self):
        """Different domain => different sequences."""
        r1 = SeededRNG(42).fork("p1", "a")
        r2 = SeededRNG(42).fork("p1", "b")
        assert [r1.normal(0, 1) for _ in range(50)] != [r2.normal(0, 1) for _ in range(50)]

    def test_fork_respects_salt(self):
        """Pending salt => different sequences from base fork."""
        base = SeededRNG(1).fork("p", "d")
        salted = SeededRNG(1).fork("p", "d", salt="x")
        assert [base.normal(0, 1) for _ in range(30)] != [salted.normal(0, 1) for _ in range(30)]

    def test_bernoulli_distribution(self):
        """Over 1000 draws at p=0.3, fraction within [25%, 35%]."""
        rng = SeededRNG(99)
        frac = sum(rng.bernoulli(0.3) for _ in range(1000)) / 1000
        assert 0.25 <= frac <= 0.35

    def test_bernoulli_returns_bool(self):
        rng = SeededRNG(7)
        for _ in range(100):
            assert isinstance(rng.bernoulli(0.5), bool)

    def test_normal_clipped_bounds(self):
        """normal_clipped must respect low/high bounds."""
        rng = SeededRNG(123)
        for _ in range(200):
            v = rng.normal_clipped(50, 20, 0, 100)
            assert 0 <= v <= 100

    def test_normal_clipped_deterministic(self):
        a = SeededRNG(3)
        b = SeededRNG(3)
        seq_a = [a.normal_clipped(0, 10, -1, 1) for _ in range(30)]
        seq_b = [b.normal_clipped(0, 10, -1, 1) for _ in range(30)]
        assert seq_a == seq_b

    def test_choice_with_weights(self):
        rng = SeededRNG(10)
        items = ["a", "b", "c"]
        counts = {"a": 0, "b": 0, "c": 0}
        for _ in range(3000):
            counts[rng.choice(items, weights=[0.1, 0.8, 0.1])] += 1
        assert counts["b"] > counts["a"]
        assert counts["b"] > counts["c"]

    def test_choice_unweighted(self):
        rng = SeededRNG(12)
        for _ in range(50):
            assert rng.choice(["x", "y"]) in ("x", "y")

    def test_beta_sample_range(self):
        rng = SeededRNG(5)
        for _ in range(100):
            assert 0.0 <= rng.beta_sample(2, 5) <= 1.0

    def test_integer_inclusive(self):
        rng = SeededRNG(3)
        for _ in range(200):
            assert 1 <= rng.integer(1, 6) <= 6

    def test_integer_returns_int(self):
        rng = SeededRNG(4)
        for _ in range(100):
            assert isinstance(rng.integer(0, 10), int)

    def test_dirichlet_sums_to_one(self):
        rng = SeededRNG(8)
        for _ in range(50):
            v = rng.dirichlet([1, 2, 3])
            assert abs(sum(v) - 1.0) < 1e-10

    def test_dirichlet_nonnegative(self):
        rng = SeededRNG(9)
        for _ in range(50):
            assert (rng.dirichlet([2, 2, 2]) >= 0).all()

    def test_log_normal_positive(self):
        rng = SeededRNG(11)
        for _ in range(100):
            assert rng.log_normal(0, 1) > 0

    def test_poisson_nonnegative_int(self):
        rng = SeededRNG(13)
        for _ in range(100):
            v = rng.poisson(2.0)
            assert isinstance(v, int)
            assert v >= 0

    def test_uniform_range(self):
        rng = SeededRNG(14)
        for _ in range(100):
            assert 5.0 <= rng.uniform(5.0, 7.0) <= 7.0

    def test_rng_property(self):
        rng = SeededRNG(1)
        assert rng.rng.random(5).shape == (5,)

    def test_new_rng_works(self):
        a = new_rng(21)
        b = new_rng(21)
        assert [a.normal(0, 1) for _ in range(20)] == [b.normal(0, 1) for _ in range(20)]

    def test_new_rng_autoseed(self):
        r1 = new_rng()
        r2 = new_rng()
        assert [r1.integer(0, 10**9) for _ in range(10)] != [r2.integer(0, 10**9) for _ in range(10)]


# ======================================================================
# SocioeconomicEngine tests
# ======================================================================


class TestSocioeconomicEngine:
    """Social class sampling and mobility constraints."""

    def test_sample_class_valid(self):
        rng = SeededRNG(42)
        for _ in range(200):
            c = SocioeconomicEngine.sample_class(rng, None)
            assert c in SocioeconomicEngine.SOCIAL_CLASSES

    def test_sample_class_matches_marginal_broadly(self):
        rng = SeededRNG(31)
        counts = {c: 0 for c in SocioeconomicEngine.SOCIAL_CLASSES}
        for _ in range(5000):
            counts[SocioeconomicEngine.sample_class(rng, None)] += 1
        assert counts["A"] < counts["C1"] < counts["D_E"]

    def test_mobility_child_of_de_rarely_a(self):
        """Child of D_E rarely reaches A: < 15% over 1500 samples."""
        rng = SeededRNG(77)
        count_a = sum(
            1 for _ in range(1500)
            if SocioeconomicEngine.sample_class(rng, "D_E") == "A"
        )
        assert count_a / 1500 < 0.15

    def test_mobility_child_of_a_seldom_de(self):
        """Child of A seldom gets D_E: < 15% over 1500 samples."""
        rng = SeededRNG(88)
        count_de = sum(
            1 for _ in range(1500)
            if SocioeconomicEngine.sample_class(rng, "A") == "D_E"
        )
        assert count_de / 1500 < 0.15

    def test_mobility_matrix_rows_sum_to_one(self):
        for row in SocioeconomicEngine.MOBILITY_MATRIX:
            assert abs(sum(row) - 1.0) < 1e-9
            assert len(row) == len(SocioeconomicEngine.SOCIAL_CLASSES)

    def test_mobility_matrix_diagonal_band(self):
        for i, row in enumerate(SocioeconomicEngine.MOBILITY_MATRIX):
            assert 0.55 <= row[i] <= 0.65

    def test_education_high_parent_high_income(self):
        """With parent superior + high income, P(superior|pos) > 0.5."""
        rng = SeededRNG(55)
        count_high = sum(
            1 for _ in range(500)
            if SocioeconomicEngine.education_level(rng, "superior", 1.5, "B1")
            in ("superior", "pos")
        )
        assert count_high / 500 > 0.5

    def test_education_parent_gap(self):
        """Superior-educated parent raises attainment over fundamental parent."""
        rng_hi = SeededRNG(61)
        rng_lo = SeededRNG(61)
        n = 1000
        sup_hi = sum(
            1 for _ in range(n)
            if SocioeconomicEngine.education_level(rng_hi, "superior", 0.5, "C1")
            in ("superior", "pos")
        )
        sup_lo = sum(
            1 for _ in range(n)
            if SocioeconomicEngine.education_level(rng_lo, "fundamental", 0.5, "C1")
            in ("superior", "pos")
        )
        assert sup_hi > sup_lo

    def test_salary_floor(self):
        """Salary never below BRL 1200."""
        rng = SeededRNG(33)
        for _ in range(200):
            s = SocioeconomicEngine.salary(
                rng, "fundamental", 0.0, "aberto", False, False
            )
            assert s >= 1200.0

    def test_salary_female_gap(self):
        """Female salary systematically lower (same inputs)."""
        rng_f = SeededRNG(100)
        rng_m = SeededRNG(100)
        sals_f = [
            SocioeconomicEngine.salary(rng_f, "superior", 10, "aberto", True, False)
            for _ in range(500)
        ]
        sals_m = [
            SocioeconomicEngine.salary(rng_m, "superior", 10, "aberto", False, False)
            for _ in range(500)
        ]
        assert sum(sals_f) / 500 < sum(sals_m) / 500

    def test_salary_education_ordering(self):
        """Higher education yields higher average gross salary."""
        rng_lo = SeededRNG(12)
        rng_hi = SeededRNG(12)
        base = [SocioeconomicEngine.salary(rng_lo, "fundamental", 5, "aberto", False, False) for _ in range(300)]
        hi = [SocioeconomicEngine.salary(rng_hi, "pos", 5, "aberto", False, False) for _ in range(300)]
        assert sum(hi) / 300 > sum(base) / 300

    def test_family_influence_same_sector(self):
        """Same-sector parent can trigger nepotism multiplier (1.0-1.35)."""
        rng = SeededRNG(22)
        multipliers = [
            SocioeconomicEngine.family_influence_weight(rng, "tech", "tech")
            for _ in range(200)
        ]
        assert any(m > 1.0 for m in multipliers)
        assert all(1.0 <= m <= 1.35 for m in multipliers)

    def test_family_influence_different_sector(self):
        """Different-sector parent always returns 1.0."""
        rng = SeededRNG(22)
        for _ in range(200):
            assert SocioeconomicEngine.family_influence_weight(rng, "tech", "health") == 1.0

    def test_family_influence_no_parent(self):
        rng = SeededRNG(1)
        for _ in range(50):
            assert SocioeconomicEngine.family_influence_weight(rng, "tech", None) == 1.0


# ======================================================================
# HealthEngine tests
# ======================================================================


class TestHealthEngine:
    """Survival, diagnoses, and mental health generators."""

    def test_survival_decreasing(self):
        """Survival should generally decrease with age."""
        prev = 1.0
        for age in range(1, 80):
            s = HealthEngine.survival(float(age), "masculino")
            assert s <= prev
            prev = s

    def test_survival_range(self):
        """Survival always in (0, 1]."""
        for age in [0, 10, 30, 50, 70, 90]:
            s = HealthEngine.survival(float(age), "feminino")
            assert 0 < s <= 1.0

    def test_survival_female_higher(self):
        """Female survival at 60 should be >= male survival."""
        sf = HealthEngine.survival(60.0, "feminino")
        sm = HealthEngine.survival(60.0, "masculino")
        assert sf >= sm

    def test_lifetime_hazard_diabetes_gate(self):
        assert HealthEngine.lifetime_hazard(30, "masculino", "diabetes") == 0.0
        assert HealthEngine.lifetime_hazard(39.9, "masculino", "diabetes") == 0.0
        assert HealthEngine.lifetime_hazard(40, "masculino", "diabetes") == 0.007
        assert HealthEngine.lifetime_hazard(70, "feminino", "diabetes") == 0.007

    def test_lifetime_hazard_hipertension_gate(self):
        assert HealthEngine.lifetime_hazard(34, "masculino", "hipertension") == 0.0
        assert HealthEngine.lifetime_hazard(35, "masculino", "hipertension") == 0.015

    def test_lifetime_hazard_depression_peak(self):
        assert HealthEngine.lifetime_hazard(20, "feminino", "depression") == 0.0
        assert HealthEngine.lifetime_hazard(30, "feminino", "depression") == 0.021
        assert HealthEngine.lifetime_hazard(44, "feminino", "depression") == 0.021
        assert HealthEngine.lifetime_hazard(45, "feminino", "depression") == 0.008

    def test_lifetime_hazard_cancer_nonnegative_growing(self):
        prev = 0.0
        for age in range(0, 90, 10):
            h = HealthEngine.lifetime_hazard(float(age), "masculino", "cancer")
            assert h >= 0.0
            assert h >= prev
            prev = h

    def test_simulate_diagnoses_no_early_diabetes(self):
        """No diabetes diagnosis before age 40."""
        rng = SeededRNG(42)
        for age in range(20, 40):
            dxs = HealthEngine.simulate_diagnoses(rng, float(age), "masculino")
            diabetes = [d for d in dxs if d["disease"] == "diabetes"]
            assert len(diabetes) == 0

    def test_simulate_diagnoses_dict_keys(self):
        """Output is list of dicts with expected keys."""
        rng = SeededRNG(10)
        dxs = HealthEngine.simulate_diagnoses(rng, 70.0, "feminino")
        if dxs:
            for d in dxs:
                assert set(d.keys()) == {
                    "disease", "age_at_diagnosis", "severity", "chronic"
                }

    def test_simulate_diagnoses_known_diseases(self):
        rng = SeededRNG(27)
        dxs = HealthEngine.simulate_diagnoses(rng, 60.0, "masculino")
        for d in dxs:
            assert d["disease"] in ("diabetes", "hipertension", "depression", "cancer")
            assert 0.0 <= d["age_at_diagnosis"] <= 60.0
            assert d["severity"] in ("leve", "moderado", "grave")
            assert d["chronic"] in (True, False)

    def test_simulate_diagnoses_deterministic(self):
        a = HealthEngine.simulate_diagnoses(SeededRNG(50).fork("p", "health"), 70.0, "feminino")
        b = HealthEngine.simulate_diagnoses(SeededRNG(50).fork("p", "health"), 70.0, "feminino")
        assert a == b

    def test_hereditary_multiplier(self):
        assert HealthEngine.hereditary_multiplier("x", True, 0.1) == pytest.approx(0.19)
        assert HealthEngine.hereditary_multiplier("x", False, 0.1) == pytest.approx(0.1)

    def test_hereditary_alias(self):
        assert HealthEngine.add_hereditary_multiplier("x", False, 0.1) == pytest.approx(0.1)

    def test_predisposition_raises_diagnosis_rate(self):
        rng_hi = SeededRNG(17)
        rng_lo = SeededRNG(17)
        n = 600
        with_pred = sum(
            1 for _ in range(n)
            if HealthEngine.simulate_diagnoses(rng_hi, 75.0, "masculino", ["diabetes"])
        )
        without = sum(
            1 for _ in range(n)
            if HealthEngine.simulate_diagnoses(rng_lo, 75.0, "masculino")
        )
        assert with_pred >= without

    def test_mental_risk_score(self):
        factors = {
            "historico_familiar": 1.0,
            "trauma": 1.0,
            "isolamento": 1.0,
            "desemprego": 1.0,
            "divorcio": 1.0,
            "luto": 1.0,
        }
        score = HealthEngine.mental_risk_score(factors)
        assert 1.0 < score <= 1.4
        assert HealthEngine.mental_risk_score({}) == 0.0

    def test_mental_disorder_returns_bool(self):
        rng = SeededRNG(5)
        for _ in range(100):
            assert isinstance(HealthEngine.mental_disorder(rng, 0.8), bool)

    def test_mental_disorder_rate_grows_with_score(self):
        rng_lo = SeededRNG(70)
        rng_hi = SeededRNG(70)
        n = 2000
        frac_lo = sum(HealthEngine.mental_disorder(rng_lo, 0.3) for _ in range(n)) / n
        frac_hi = sum(HealthEngine.mental_disorder(rng_hi, 1.3) for _ in range(n)) / n
        assert frac_hi > frac_lo

    def test_chronic_impact_no_chronic(self):
        rng = SeededRNG(5)
        r = HealthEngine.chronic_impact(rng, False)
        assert r["sick_leave"] is False
        assert r["income_reduction"] == 0.0
        assert r["divorce_multiplier"] == 1.0
        assert r["debt_probability"] == 0.0

    def test_chronic_impact_with_chronic(self):
        rng = SeededRNG(9)
        r = HealthEngine.chronic_impact(rng, True)
        assert isinstance(r["sick_leave"], bool)
        assert 0.0 <= r["income_reduction"] <= 0.4
        assert r["divorce_multiplier"] in (1.0, 1.8)
        assert r["debt_probability"] == 0.34

    def test_chronic_impact_deterministic(self):
        a = HealthEngine.chronic_impact(SeededRNG(15), True)
        b = HealthEngine.chronic_impact(SeededRNG(15), True)
        assert a == b