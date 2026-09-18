"""Health engine — survival, diagnoses, chronic impact, mental risk.

Ownership: Agent 2. Sibling agents may import HealthEngine.
"""
from __future__ import annotations

import math

from .constants import DISEASE_TRANCHES
from .rng import SeededRNG


class HealthEngine:
    """Deterministic health-process generator."""

    SEVERITY_LEVELS: list[str] = ["leve", "moderado", "grave"]
    CHRONIC_DISEASES: tuple[str, ...] = ("diabetes", "hipertension", "depression")

    # ------------------------------------------------------------------
    # Hazard helpers
    # ------------------------------------------------------------------

    @staticmethod
    def lifetime_hazard(age: float, sex: str, disease: str) -> float:
        """Annual hazard rate for *disease* at a given age.

        All hazards are non-negative; diabetes, hipertension and depression
        are gated by their min_age, depression peaks between 25-44, and
        cancer follows a Gompertz curve.
        """
        if disease not in DISEASE_TRANCHES:
            return 0.0

        if disease == "cancer":
            info = DISEASE_TRANCHES["cancer"]
            a = info.get("gompertz_a", 0.0003)
            b = info.get("gompertz_b", 0.085)
            return float(a * math.exp(b * max(age, 0.0)))

        if disease == "diabetes":
            return 0.007 if age >= 40 else 0.0

        if disease == "hipertension":
            return 0.015 if age >= 35 else 0.0

        if disease == "depression":
            if age < 25:
                return 0.0
            return 0.021 if age <= 44 else 0.008

        info = DISEASE_TRANCHES[disease]
        min_age = info.get("min_age", 0)
        if age < min_age:
            return 0.0
        return float(info.get("hazard", 0.0))

    # ------------------------------------------------------------------
    # Survival
    # ------------------------------------------------------------------

    @staticmethod
    def survival(age: float, sex: str) -> float:
        """Probability of surviving from birth to *age*, S(t) in (0, 1].

        Trapezoid integral over yearly steps of the total force of
        mortality: base_force 0.02 (males) / 0.018 (females) plus all
        disease hazards.
        """
        age = max(float(age), 0.0)
        base_force = 0.018 if sex.lower() in ("f", "feminino", "female") else 0.02

        def force(t: float) -> float:
            return base_force + sum(
                HealthEngine.lifetime_hazard(t, sex, d) for d in DISEASE_TRANCHES
            )

        n = int(math.floor(age))
        cumulative_hazard = 0.0
        for t in range(n):
            cumulative_hazard += 0.5 * (force(float(t)) + force(float(t + 1)))

        frac = age - n
        if frac > 0:
            cumulative_hazard += 0.5 * (force(float(n)) + force(age)) * frac

        s = math.exp(-cumulative_hazard)
        return float(max(min(1.0, s), 1e-12))

    # ------------------------------------------------------------------
    # Diagnosis simulation
    # ------------------------------------------------------------------

    @staticmethod
    def _cumulative_hazard(age: float, sex: str, disease: str) -> float:
        """Lifetime cumulative hazard for *disease* up to *age* (annual scale)."""
        age = max(float(age), 0.0)
        n = int(math.floor(age))
        total = 0.0
        for t in range(n):
            total += 0.5 * (
                HealthEngine.lifetime_hazard(float(t), sex, disease)
                + HealthEngine.lifetime_hazard(float(t + 1), sex, disease)
            )
        frac = age - n
        if frac > 0:
            total += 0.5 * (
                HealthEngine.lifetime_hazard(float(n), sex, disease)
                + HealthEngine.lifetime_hazard(age, sex, disease)
            ) * frac
        return total

    @staticmethod
    def hereditary_multiplier(
        disease: str, has_predisposition: bool, base_risk: float
    ) -> float:
        """Genetic loading: predisposed individuals carry x1.9 the base risk."""
        return base_risk * 1.9 if has_predisposition else base_risk

    @staticmethod
    def simulate_diagnoses(
        rng: SeededRNG,
        age: float,
        sex: str,
        predispositions: list[str] | None = None,
    ) -> list[dict]:
        """Monte-Carlo diagnosis list for diseases in DISEASE_TRANCHES.

        Acceptance via u ~ Uniform(0,1): a diagnosis is recorded when
        u < 1 - exp(-H) where H is the lifetime cumulative hazard, with
        predispositions inflating H by the hereditary multiplier.
        """
        predispositions = list(predispositions) if predispositions else []
        diagnoses: list[dict] = []

        for disease in DISEASE_TRANCHES:
            min_age = DISEASE_TRANCHES[disease].get("min_age", 0)
            base_hazard = HealthEngine._cumulative_hazard(age, sex, disease)
            base_hazard = HealthEngine.hereditary_multiplier(
                disease, disease in predispositions, base_hazard
            )
            total_hazard = min(base_hazard, 10.0)  # numerical stability cap
            p_accepted = 1.0 - math.exp(-total_hazard)

            u = rng.uniform(0.0, 1.0)
            if u >= p_accepted:
                continue

            lo = max(float(min_age), 0.0)
            hi = max(float(age), lo)
            age_at_diagnosis = rng.uniform(lo, hi)

            if age > 60:
                sev_probs = [0.20, 0.45, 0.35]
            elif age > 40:
                sev_probs = [0.30, 0.45, 0.25]
            else:
                sev_probs = [0.45, 0.40, 0.15]
            severity = str(rng.choice(HealthEngine.SEVERITY_LEVELS, weights=sev_probs))

            diagnoses.append({
                "disease": disease,
                "age_at_diagnosis": round(float(age_at_diagnosis), 1),
                "severity": severity,
                "chronic": disease in HealthEngine.CHRONIC_DISEASES,
            })

        return diagnoses

    # Backwards-compatible alias.
    add_hereditary_multiplier = hereditary_multiplier

    # ------------------------------------------------------------------
    # Mental health
    # ------------------------------------------------------------------

    @staticmethod
    def mental_risk_score(risk_factors: dict) -> float:
        """Weighted sum of psychosocial risk factors (~0..1.3)."""
        weights = {
            "historico_familiar": 0.3,
            "trauma": 0.25,
            "isolamento": 0.2,
            "desemprego": 0.2,
            "divorcio": 0.15,
            "luto": 0.2,
        }
        score = 0.0
        for key, w in weights.items():
            score += w * float(risk_factors.get(key, 0))
        return round(score, 4)

    @staticmethod
    def mental_disorder(rng: SeededRNG, risk_score: float) -> bool:
        """Bernoulli draw from sigmoid(risk_score - 0.7)."""
        logit = risk_score - 0.7
        p = 1.0 / (1.0 + math.exp(-logit))
        return rng.bernoulli(p)

    # ------------------------------------------------------------------
    # Chronic impact
    # ------------------------------------------------------------------

    @staticmethod
    def chronic_impact(rng: SeededRNG, has_chronic: bool) -> dict:
        """Financial/employment/relationship modifiers for chronic disease."""
        if not has_chronic:
            return {
                "sick_leave": False,
                "income_reduction": 0.0,
                "divorce_multiplier": 1.0,
                "debt_probability": 0.0,
            }
        sick_leave = rng.bernoulli(0.45)
        income_reduction = round(float(rng.beta_sample(2.0, 5.0)) * 0.4, 2)
        divorce_multiplier = 1.8 if rng.bernoulli(0.35) else 1.0
        return {
            "sick_leave": sick_leave,
            "income_reduction": income_reduction,
            "divorce_multiplier": divorce_multiplier,
            "debt_probability": 0.34,
        }