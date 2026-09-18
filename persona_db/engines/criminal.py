"""Motor criminal e jurídico — envolvimento, impacto e reincidência.

Owned by Agent 4. Signatures estáveis para generators/validators.
"""
from __future__ import annotations

import math

try:  # pragma: no cover - fallback stub
    from .rng import SeededRNG
    from .constants import RISK_LOGLIT
except Exception:  # pragma: no cover
    SeededRNG = object
    RISK_LOGLIT = {}


_CRIME_TYPES = [
    "crimes_violentos",
    "crimes_patrimoniais",
    "crimes_digitais",
    "crimes_de_transito",
    "crimes_corporativos",
    "trafico",
]

_SENTENCE_RANGES = {
    "crimes_violentos": (36, 144),
    "crimes_patrimoniais": (12, 60),
    "crimes_digitais": (24, 72),
    "crimes_de_transito": (6, 36),
    "crimes_corporativos": (12, 48),
    "trafico": (60, 180),
}

_ARREST_BY_TYPE = {
    "crimes_violentos": 0.65,
    "crimes_patrimoniais": 0.38,
    "crimes_digitais": 0.22,
    "crimes_de_transito": 0.55,
    "crimes_corporativos": 0.10,
    "trafico": 0.58,
}


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


class CriminalEngine:
    """Engrenagem de geração criminal coerente com fatores de risco."""

    def __init__(self, rng: SeededRNG):
        self._rng = rng

    # -- Probabilidade ------------------------------------------------------
    def crime_probability(self, features: dict) -> float:
        """P(crime) via modelo logístico com RISK_LOGLIT de constants."""
        logit = RISK_LOGLIT.get("intercept", -3.5)
        f = features
        if f.get("sex") == "masculino":
            logit += RISK_LOGLIT["masculino"]
        if 15 <= f.get("age", 99) <= 25:
            logit += RISK_LOGLIT["idade_15_25"]
        if f.get("class_label") == "D_E":
            logit += RISK_LOGLIT["classe_D_E"]
        for k in ("pai_criminal", "mae_criminal", "irmao_criminal",
                  "desemprego", "abandono_escolar", "transtorno_mental"):
            if f.get(k):
                logit += RISK_LOGLIT[k]
        if f.get("education") in ("superior", "pos"):
            logit += RISK_LOGLIT["ensino_superior"]
        if f.get("income_annual", 0) >= 150_000:
            logit += RISK_LOGLIT["renda_alta"]
        return _sigmoid(logit)

    def commits_crime(self, features: dict) -> bool:
        return self._rng.bernoulli(self.crime_probability(features))

    # -- Tipo e processo ----------------------------------------------------
    def crime_type(self, features: dict) -> str:
        weights = [0.22, 0.30, 0.12, 0.18, 0.06, 0.12]
        if 15 <= features.get("age", 99) <= 25 and features.get("sex") == "masculino":
            weights[0] += 0.10
            weights[1] -= 0.05
            weights[3] -= 0.05
        return self._rng.choice(_CRIME_TYPES, weights=weights)

    def arrested(self, crime_type: str, class_label: str, quality_advocate: float = 0.5) -> bool:
        p = _ARREST_BY_TYPE.get(crime_type, 0.3)
        if class_label == "D_E":
            p *= 1.15
        elif class_label == "A":
            p *= 0.75
        p *= (1.0 - 0.5 * quality_advocate)
        return self._rng.bernoulli(min(0.95, p))

    def sentence_months(self, crime_type: str, recidivist: bool = False) -> int:
        lo, hi = _SENTENCE_RANGES.get(crime_type, (12, 60))
        if recidivist:
            lo = min(lo * 2, hi)
        return self._rng.integer(lo, hi)

    def recidivism(self, employment_formal: bool, family_support: bool) -> bool:
        p = 0.42 - 0.3 * employment_formal - 0.2 * family_support
        p += self._rng.normal(0.0, 0.05)
        return self._rng.bernoulli(max(0.05, min(0.75, p)))

    # -- Impactos ------------------------------------------------------------
    def employment_impact(self, has_antecedent: bool, sector: str) -> dict:
        if has_antecedent:
            return {
                "hiring_multiplier": 0.45,
                "salary_reduction": self._rng.normal(0.325, 0.037),
                "barred_sectors": ["publico", "financeiro", "educacao"],
                "blocked": sector in ("publico", "financeiro", "educacao"),
            }
        return {
            "hiring_multiplier": 1.0,
            "salary_reduction": 0.0,
            "barred_sectors": [],
            "blocked": False,
        }

    def relationship_impact(self, arrested: bool, domestic_violence: bool) -> dict:
        return {
            "divorce_prob": 0.73 if arrested else 0.15,
            "custody_loss": 0.65 if domestic_violence else 0.10,
        }

    def financial_impact(self, went_to_court: bool) -> dict:
        cost = math.exp(self._rng.normal(9.5, 0.8))
        return {
            "cost_process": round(cost, 2),
            "asset_loss_prob": 0.28 if went_to_court else 0.03,
        }

    # -- Pipeline completo ---------------------------------------------------
    def criminal_process_series(self, features: dict) -> dict:
        """Trajetória criminal coerente e completa para uma pessoa."""
        p = self.crime_probability(features)
        did = self._rng.bernoulli(p)
        if not did:
            return {
                "did_crime": False,
                "crime_type": None,
                "was_arrested": False,
                "months_sentence": 0,
                "convicted": False,
                "process_cost": 0.0,
                "divorce_impact": self.relationship_impact(False, False),
                "employment_impact": self.employment_impact(False, features.get("sector", "")),
                "recidivism": False,
            }
        ctype = self.crime_type(features)
        was_arrested = self.arrested(ctype, features.get("class_label", "C1"))
        convicted = was_arrested and self._rng.bernoulli(0.85 if ctype != "crimes_corporativos" else 0.6)
        months = self.sentence_months(ctype, False) if convicted else 0
        fin = self.financial_impact(convicted or was_arrested)
        divorce = self.relationship_impact(was_arrested, ctype == "crimes_violentos")
        emp = self.employment_impact(convicted or was_arrested, features.get("sector", ""))
        return {
            "did_crime": True,
            "crime_type": ctype,
            "was_arrested": was_arrested,
            "months_sentence": months,
            "convicted": convicted,
            "process_cost": fin["cost_process"],
            "asset_loss_prob": fin["asset_loss_prob"],
            "divorce_impact": divorce,
            "employment_impact": emp,
            "recidivism": self.recidivism(
                features.get("formal_employment", False),
                features.get("family_support", False),
            ),
        }