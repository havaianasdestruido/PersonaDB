"""Relacionamentos, família e fecundidade — engine probabilístico.

Owned by Agent 3. Signature-stable for generators/validators.
"""
from __future__ import annotations

import math

try:  # pragma: no cover - fallback stub
    from .rng import SeededRNG
except Exception:  # pragma: no cover
    SeededRNG = object

_SOCIAL_ORDER = ["A", "B1", "B2", "C1", "C2", "D_E"]


class FamilyEngine:
    """Hazard-style engine para núcleos familiares."""

    P_CASAMENTO_ALGUM_DIA = 0.72
    P_DIVORCIO = 0.21
    P_SEGUNDO_CASAMENTO = 0.38
    SAME_CLASS_PROB = 0.58
    SAME_EDU_PROB = 0.55
    SAME_RELIGION_PROB = 0.61

    _POSSON_LAMBDA = {("A", "B1", "B2"): 1.4, ("C1",): 1.9, ("C2", "D_E"): 2.6}

    def __init__(self, rng: SeededRNG):
        self._rng = rng

    @staticmethod
    def _gauss(x: float, mu: float, sigma: float, peak: float) -> float:
        return peak * math.exp(-0.5 * ((x - mu) / sigma) ** 2)

    def marriage_hazard(self, age: float, sex: str) -> float:
        """Hazard de primeiro casamento por idade (pico M 28-32, F 25-29)."""
        if sex.upper().startswith("M"):
            return self._gauss(age, 30.0, 6.0, 0.12)
        return self._gauss(age, 27.0, 5.0, 0.13)

    def first_marriage_age(self, sex: str) -> float | None:
        """Idade ao primeiro casamento ou None (28% nunca se casam)."""
        if self._rng.bernoulli(1.0 - self.P_CASAMENTO_ALGUM_DIA):
            return None
        if sex.upper().startswith("M"):
            return max(16.0, min(55.0, self._rng.normal(30.0, 4.0)))
        return max(16.0, min(55.0, self._rng.normal(27.0, 4.0)))

    def children_count(self, class_label: str, modificators: dict | None = None) -> int:
        """Nº de filhos por classe social (Poisson) com modificadores."""
        lam = 2.6
        for classes, m in self._POSSON_LAMBDA.items():
            if class_label in classes:
                lam = m
                break
        mods = modificators or {}
        lam += mods.get("doenca", 0.0) + mods.get("divorcio", 0.0) + mods.get("superior", 0.0)
        return max(0, int(self._rng.poisson(max(0.0, lam))))

    def homogamy_age_diff(self) -> float:
        return abs(self._rng.normal(2.5, 4.2))

    def spouse_class(self, own_class: str) -> str:
        """58%% mesma classe, resto adjacente."""
        if self._rng.bernoulli(self.SAME_CLASS_PROB):
            return own_class
        idx = _SOCIAL_ORDER.index(own_class)
        step = 1 if self._rng.normal(0, 1) >= 0 else -1
        nxt = max(0, min(len(_SOCIAL_ORDER) - 1, idx + step))
        return _SOCIAL_ORDER[nxt]

    def divorce(self, risk_factors: dict | None = None) -> bool:
        """Decisão de divórcio com fatores de risco/proteção."""
        logit = -1.35
        rf = risk_factors or {}
        logit += 0.8 * rf.get("doenca_mental_conjuge", 0.0)
        logit += 1.2 * rf.get("antecedente_criminal_conjuge", 0.0)
        logit += 0.3 * rf.get("diferenca_classe", 0.0)
        logit += 0.5 * rf.get("desemprego_prolongado", 0.0)
        logit -= 0.4 * rf.get("filhos_pequenos", 0.0)
        logit -= 0.5 * rf.get("religiosidade_alta", 0.0)
        p = 1.0 / (1.0 + math.exp(-logit))
        return self._rng.bernoulli(min(0.9, p))

    def death_likelihood(self, age: float, sex: str) -> bool:
        """Aproximação grosseira de mortalidade para simulação."""
        if age < 5:
            p = 0.008
        elif age < 40:
            p = 0.002 + 0.0002 * age
        elif age < 70:
            p = 0.02 + (age - 40) * 0.004
        else:
            p = 0.12 + (age - 70) * 0.03
        if sex.upper().startswith("M"):
            p *= 1.15
        return self._rng.bernoulli(min(0.99, p))

    def union_lifecycle(self, sex: str, class_label: str) -> dict:
        """Ciclo de vida afetiva completo e coerente."""
        age = self.first_marriage_age(sex)
        if age is None:
            return {"casou": False, "primeiro_casamento_idade": None}
        spouse = self.spouse_class(class_label)
        return {
            "casou": True,
            "primeiro_casamento_idade": round(age, 1),
            "conjuge_classe": spouse,
            "divorcio": self.divorce(),
        }