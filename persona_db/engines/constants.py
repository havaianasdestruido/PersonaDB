"""Shared constants and anchors for all engines.

Ownership: COORDINATOR ONLY; agents import, never edit.
Tuned ranges are defaults that agent modules may READ via this anchor,
but calibrating values inside their owned modules follows normal practices.
"""
from __future__ import annotations

# Distribution for Brazilian social classes (2024 proxy).
SOCIAL_CLASS_DIST = {
    "A": 0.03,
    "B1": 0.07,
    "B2": 0.15,
    "C1": 0.22,
    "C2": 0.25,
    "D_E": 0.28,
}

# Standard Punnett / ABO likelihood anchors (used by genetics engine).
BLOOD_GROUP_PRIORS = {
    "O": 0.47,
    "A": 0.41,
    "B": 0.09,
    "AB": 0.03,
}

# Health/disease calibrated priors referenced by health engine.
MORTALITY_SURVIVAL_K = 365.0
DISEASE_TRANCHES = {
    "diabetes": {"min_age": 40, "hazard": 0.007},
    "hipertension": {"min_age": 35, "hazard": 0.015},
    "depression": {"min_age": 25, "hazard": 0.021},
    "cancer": {"gompertz_a": 0.0003, "gompertz_b": 0.085},
}

# Criminal risk logistic coefficients (used by criminal engine).
RISK_LOGLIT = {
    "masculino": 1.8,
    "idade_15_25": 0.9,
    "classe_D_E": 0.7,
    "pai_criminal": 1.1,
    "mae_criminal": 0.8,
    "irmao_criminal": 0.6,
    "desemprego": 0.5,
    "abandono_escolar": 0.4,
    "transtorno_mental": 0.3,
    "ensino_superior": -0.9,
    "renda_alta": -0.8,
    "intercept": -3.5,
}


def class_to_index(cls: str) -> int:
    return list(SOCIAL_CLASS_DIST).index(cls)