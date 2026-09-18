"""Socioeconomic engine — social class, education, salary, family influence.

Ownership: Agent 2. Sibling agents may import SocioeconomicEngine.
"""
from __future__ import annotations

import numpy as np

from .constants import SOCIAL_CLASS_DIST
from .rng import SeededRNG


class SocioeconomicEngine:
    """Deterministic socioeconomic attribute generator."""

    SOCIAL_CLASSES: list[str] = ["A", "B1", "B2", "C1", "C2", "D_E"]

    # Mobility matrix: rows = parent class (A..D_E), cols = child class.
    # Diagonals are 0.55-0.65 (strong intergenerational stickiness); every
    # row sums to 1.0.
    MOBILITY_MATRIX: list[list[float]] = [
        [0.62, 0.20, 0.10, 0.05, 0.02, 0.01],  # A parent
        [0.08, 0.55, 0.22, 0.10, 0.03, 0.02],  # B1 parent
        [0.03, 0.10, 0.58, 0.20, 0.06, 0.03],  # B2 parent
        [0.01, 0.04, 0.12, 0.56, 0.18, 0.09],  # C1 parent
        [0.01, 0.02, 0.06, 0.16, 0.57, 0.18],  # C2 parent
        [0.01, 0.01, 0.04, 0.10, 0.24, 0.60],  # D_E parent
    ]

    # Annual gross BRL salary shift per sector (log-scale, relative to 'aberto').
    SECTOR_SHIFT: dict[str, float] = {
        "aberto": 0.00,
        "agro": -0.08,
        "comercio": -0.02,
        "construcao": -0.06,
        "educacao": -0.04,
        "saude": 0.03,
        "industria": 0.02,
        "tecnologia": 0.10,
        "financeiro": 0.14,
        "publico": 0.06,
    }

    # ------------------------------------------------------------------
    # Social class
    # ------------------------------------------------------------------

    @classmethod
    def sample_class(cls, rng: SeededRNG, parent_class: str | None) -> str:
        """Sample a social class.

        With a known parent class the intergenerational mobility matrix
        drives the draw; otherwise the marginal SOCIAL_CLASS_DIST applies.
        """
        if parent_class in cls.SOCIAL_CLASSES:
            row_idx = cls.SOCIAL_CLASSES.index(parent_class)
            probs = cls.MOBILITY_MATRIX[row_idx]
        else:
            probs = [SOCIAL_CLASS_DIST[c] for c in cls.SOCIAL_CLASSES]
        return str(rng.choice(cls.SOCIAL_CLASSES, weights=probs))

    # ------------------------------------------------------------------
    # Education
    # ------------------------------------------------------------------

    @classmethod
    def education_level(
        cls,
        rng: SeededRNG,
        parent_education: str | None,
        income_std: float,
        class_label: str,
    ) -> str:
        """Sample attained education from ['fundamental','medio','superior','pos'].

        A multinomial logit model where parent education, household income
        (per std, coefficient 0.23) and social-class premium shift the odds.
        """
        levels = ["fundamental", "medio", "superior", "pos"]
        logits = {"fundamental": 0.20, "medio": 0.90, "superior": 0.30, "pos": -0.50}

        if parent_education == "superior":
            logits["superior"] += 0.58
            logits["pos"] += 0.35
        elif parent_education == "pos":
            logits["superior"] += 0.45
            logits["pos"] += 0.60
        elif parent_education == "medio":
            logits["superior"] += 0.20
        elif parent_education == "fundamental":
            logits["superior"] -= 0.12

        # Income effect: coefficient 0.23 per standard deviation.
        income_shift = 0.23 * income_std
        logits["superior"] += income_shift
        logits["pos"] += income_shift * 0.6

        # Class income premium on higher attainment.
        class_premium = {
            "A": (0.55, 0.70),
            "B1": (0.30, 0.35),
            "B2": (0.10, 0.05),
            "C1": (0.00, -0.10),
            "C2": (-0.15, -0.20),
            "D_E": (-0.35, -0.30),
        }
        sup, pos = class_premium.get(class_label, (0.0, 0.0))
        logits["superior"] += sup
        logits["pos"] += pos

        arr = np.array([logits[lvl] for lvl in levels], dtype=np.float64)
        arr -= arr.max()
        exp_arr = np.exp(arr)
        probs = exp_arr / exp_arr.sum()
        return str(rng.choice(levels, weights=probs))

    # ------------------------------------------------------------------
    # Salary
    # ------------------------------------------------------------------

    @staticmethod
    def salary(
        rng: SeededRNG,
        education: str,
        experience_years: float,
        sector: str,
        gender_female: bool,
        race_minority: bool,
        nepotism_log_bonus: float = 0.0,
    ) -> float:
        """Annual gross salary in BRL (log-normal model with covariates).

        log(salary) = 5.2
            + education_premium
            + 0.022*exp - 0.0002*exp**2
            + sector_shift
            - 0.14 (female) - 0.11 (minority) + nepotism bonus
            + eps, eps ~ Normal(0, 0.35)
        Rounded to 2 decimals with a BRL 1200 floor.
        """
        log_sal = 5.2

        edu_premium = {
            "fundamental": 0.0,
            "medio": 0.35,
            "superior": 0.85,
            "pos": 1.25,
        }
        log_sal += edu_premium.get(education, 0.0)

        log_sal += 0.022 * experience_years - 0.0002 * experience_years ** 2

        log_sal += SocioeconomicEngine.SECTOR_SHIFT.get(sector, 0.0)

        if gender_female:
            log_sal -= 0.14
        if race_minority:
            log_sal -= 0.11
        log_sal += nepotism_log_bonus

        log_sal += rng.normal(0.0, 0.35)

        salary_val = round(float(np.exp(log_sal)), 2)
        return max(salary_val, 1200.0)

    # ------------------------------------------------------------------
    # Family influence weight (nepotism)
    # ------------------------------------------------------------------

    @staticmethod
    def family_influence_weight(
        rng: SeededRNG,
        sector_career: str,
        sector_parent: str | None,
    ) -> float:
        """Multiplier in [1.0, 1.35] reflecting sector nepotism.

        A parent already embedded in the chosen sector raises the child's
        odds/pull through connections; different or absent parent = 1.0.
        """
        if sector_parent is None:
            return 1.0
        if sector_career == sector_parent and rng.bernoulli(0.32):
            return rng.uniform(1.0, 1.35)
        return 1.0