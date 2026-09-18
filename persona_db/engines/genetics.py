"""Genetic trait inheritance engine.

Owned by Agent 3. Public API consumed by generators and validators.
All randomness flows through SeededRNG (duck-typed parameter).
"""
from __future__ import annotations

import math

try:  # pragma: no cover - fallback stub for import safety
    from .rng import SeededRNG
except Exception:  # pragma: no cover
    SeededRNG = object

# ---------------------------------------------------------------------------
# Cor dos olhos — modelo poligênico simplificado OCA2/HERC2
# Alelos: B=castanho(dominante), b=azul(recessivo), G=verde(intermediário)
# ---------------------------------------------------------------------------
_OLHO_ALELOS = ("B", "b", "G", "g")

_PHENOTYPE_OF_GENOTYPE = {
    frozenset(("B", "B")): "castanho",
    frozenset(("B", "b")): "castanho",
    frozenset(("B", "G")): "castanho",
    frozenset(("B", "g")): "castanho",
    frozenset(("G", "G")): "verde",
    frozenset(("G", "g")): "verde",
    frozenset(("b", "b")): "azul",
    frozenset(("b", "G")): "verde",
    frozenset(("b", "g")): "verde",
    frozenset(("g", "g")): "avela",
}


class GeneticEngine:
    """Fachada única para herança genética de traços físicos."""

    PHENOTYPE_ENUMS = {
        "cor_olhos": ["castanho", "azul", "verde", "avela", "cinza", "ambar"],
        "cor_cabelo": ["preto", "castanho", "loiro", "ruivo", "grisalho", "branco"],
        "mao_dominante": ["direita", "esquerda", "ambidestro"],
        "tipo_sanguineo": ["A", "B", "AB", "O"],
        "fator_rh": ["positivo", "negativo"],
    }

    def __init__(self, rng: SeededRNG):
        self._rng = rng

    # -- Olhos ------------------------------------------------------------
    @staticmethod
    def _genotype_to_phenotype(gt: tuple[str, str]) -> str:
        return _PHENOTYPE_OF_GENOTYPE[frozenset(gt)]

    @staticmethod
    def eye_color_chart(parent1_gt: tuple[str, str], parent2_gt: tuple[str, str]) -> dict:
        """Tabela completa de Punnett -> {fenótipo: probabilidade}."""
        chart: dict[str, float] = {}
        for a in parent1_gt:
            for b in parent2_gt:
                pheno = _PHENOTYPE_OF_GENOTYPE[frozenset((a, b))]
                chart[pheno] = chart.get(pheno, 0.0) + 0.25
        return chart

    def genotype_sample(self) -> tuple[str, str]:
        """Amostra um genótipo com frequências populacionais realistas."""
        weights = [0.55, 0.22, 0.12, 0.11]  # B, b, G, g
        a = self._rng.choice(_OLHO_ALELOS, weights=weights)
        b = self._rng.choice(_OLHO_ALELOS, weights=weights)
        return (a, b)

    def _rare_variant(self, base: str) -> str:
        r = self._rng.choice(["avela", "cinza", "ambar"], weights=[0.6, 0.3, 0.1])
        if base == "castanho" and r == "ambar":
            return "ambar"
        if base in ("verde", "azul") and r in ("avela", "cinza"):
            return r
        return base

    def draw_eye_color(
        self,
        gt_pai: tuple[str, str],
        gt_mae: tuple[str, str],
        ancestry_african_pct: float | None = None,
    ) -> str:
        chart = self.eye_color_chart(gt_pai, gt_mae)
        pheno = self._rng.choice(list(chart.keys()), weights=list(chart.values()))
        if pheno in ("castanho", "verde", "azul"):
            boost = 1.0
            if ancestry_african_pct and ancestry_african_pct > 0.4:
                boost += 0.06
            if self._rng.beta_sample(2.0, 50.0) < 0.03 * boost:
                pheno = self._rare_variant(pheno)
            if pheno in ("castanho", "verde") and ancestry_african_pct:
                if self._rng.bernoulli(min(0.05, 0.02 + ancestry_african_pct * 0.05)):
                    pheno = self._rare_variant(pheno)
        return pheno

    # -- Cabelo -----------------------------------------------------------
    _HAIR_ORDER = ["preto", "castanho", "loiro", "ruivo"]

    def hair_color(
        self, hair_pai_str: str, hair_mae_str: str, ancestry_european_pct: float = 0.0
    ) -> str:
        """Dominância: preto > castanho > loiro > ruivo, com modificadores de ancestralidade."""
        pool = [hair_pai_str, hair_mae_str]
        ranks = {h: self._HAIR_ORDER.index(h) if h in self._HAIR_ORDER else 99 for h in pool}
        base = min(pool, key=lambda h: ranks[h])

        ruivo_p = 0.01 * (0.5 + ancestry_european_pct)
        loiro_p = 0.04 * (0.3 + ancestry_european_pct) if base in ("castanho", "preto") else 0.0

        if base in ("preto", "castanho") and ancestry_european_pct < 0.2:
            if self._rng.bernoulli(loiro_p):
                base = "loiro"
        if base in ("preto", "castanho", "loiro"):
            if self._rng.bernoulli(ruivo_p):
                base = "ruivo"

        r = self._rng.normal(0, 1)
        if r > 2.3:
            return "grisalho"
        if r > 3.0:
            return "branco"
        return base

    # -- Lateralidade ------------------------------------------------------
    @staticmethod
    def handedness_prob(pai_canhoto: bool, mae_canhota: bool) -> float:
        """Modelo logístico: logit(P) = -2.1 + 0.69*pai + 0.55*mae."""
        logit = -2.1 + 0.69 * pai_canhoto + 0.55 * mae_canhota
        return 1.0 / (1.0 + math.exp(-logit))

    def handedness(self, pai_canhoto: bool, mae_canhota: bool) -> str:
        p_esq = self.handedness_prob(pai_canhoto, mae_canhota)
        roll = self._rng.normal(0, 1)
        if self._rng.bernoulli(0.02):
            return "ambidestro"
        if self._rng.bernoulli(p_esq):
            return "esquerda"
        return "direita"

    # -- Tipo sanguíneo ABO + Rh -------------------------------------------
    # Fenótipo -> conjunto de possíveis genótipos
    _ABO_GENOTYPES = {
        "A": [("IA", "IA"), ("IA", "i")],
        "B": [("IB", "IB"), ("IB", "i")],
        "AB": [("IA", "IB")],
        "O": [("i", "i")],
    }
    _RH_GENOTYPES = {"positivo": [("D", "D"), ("D", "d")], "negativo": [("d", "d")]}

    @classmethod
    def _all_parent_gamete_pairs(cls, tipo: str) -> list[tuple[str, str]]:
        return cls._ABO_GENOTYPES[tipo]

    @classmethod
    def _phenotype_of_abo(cls, ga: str, gb: str) -> str:
        if "IA" in (ga, gb) and "IB" in (ga, gb):
            return "AB"
        if "IA" in (ga, gb):
            return "A"
        if "IB" in (ga, gb):
            return "B"
        return "O"

    @classmethod
    def punnett_abo(cls, tipo_pai: str, tipo_mae: str) -> dict:
        """Probabilidades de fenótipo ABO filho via Punnett completo."""
        out: dict[str, float] = {}
        game_pai = cls._genotypes_gametes(tipo_pai)
        game_mae = cls._genotypes_gametes(tipo_mae)
        for ap, wp in game_pai:
            for am, wm in game_mae:
                p = cls._phenotype_of_abo(ap, am)
                out[p] = out.get(p, 0.0) + wp * wm
        return out

    @classmethod
    def _genotypes_gametes(cls, tipo: str) -> list[tuple[str, float]]:
        """Distribuição de gametas dados os genótipos possíveis do fenótipo."""
        gametes: dict[str, float] = {}
        for gt in cls._ABO_GENOTYPES[tipo]:
            for allele in gt:
                gametes[allele] = gametes.get(allele, 0.0) + 0.5
        total = sum(gametes.values()) or 1.0
        return [(a, w / total) for a, w in gametes.items()]

    @classmethod
    def rh_punnett(cls, rh_pai: str, rh_mae: str) -> dict:
        """Punnett simplificado para Rh (D dominante)."""
        out = {"positivo": 0.0, "negativo": 0.0}
        gam_pai = cls._rh_gametes(rh_pai)
        gam_mae = cls._rh_gametes(rh_mae)
        for gp, wp in gam_pai:
            for gm, wm in gam_mae:
                pheno = "positivo" if ("D" in (gp, gm)) else "negativo"
                out[pheno] += wp * wm
        return out

    @classmethod
    def _rh_gametes(cls, rh: str) -> list[tuple[str, float]]:
        gts = cls._RH_GENOTYPES[rh]
        gametes: dict[str, float] = {}
        for gt in gts:
            for allele in gt:
                gametes[allele] = gametes.get(allele, 0.0) + 0.5
        total = sum(gametes.values()) or 1.0
        return [(a, w / total) for a, w in gametes.items()]

    def herdar_tipo_sanguineo(
        self,
        tipo_pai: str,
        tipo_mae: str,
        rh_pai: str,
        rh_mae: str,
    ) -> str:
        abo = self.punnett_abo(tipo_pai, tipo_mae)
        rh = self.rh_punnett(rh_pai, rh_mae)
        tipo = self._rng.choice(list(abo.keys()), weights=list(abo.values()))
        rh_tipo = self._rng.choice(list(rh.keys()), weights=list(rh.values()))
        return f"{tipo}{'+' if rh_tipo == 'positivo' else '-'}"

    @classmethod
    def validate_child_blood(cls, tipo_pai, tipo_mae, rh_pai, rh_mae, tipo_filho) -> bool:
        """Validador: tipo de sangue filho é possível dados os pais."""
        abo = cls.punnett_abo(tipo_pai, tipo_mae)
        rh = cls.rh_punnett(rh_pai, rh_mae)
        filho_abo = tipo_filho[0] if len(tipo_filho) == 2 else tipo_filho[:-1]
        filho_rh = "positivo" if tipo_filho.endswith("+") else "negativo"
        if tipo_filho[0] in "AB":
            filho_abo = tipo_filho[0:2]
        if abo.get(filho_abo, 0.0) <= 0.0:
            return False
        if rh.get(filho_rh, 0.0) <= 0.0:
            return False
        return True

    # -- Altura (herança poligênica / mid-parent) ---------------------------
    def expected_child_height(self, altura_pai_cm: float, altura_mae_cm: float, sex_filho: str) -> float:
        if sex_filho.upper().startswith("M"):
            mae_corrigida = altura_mae_cm * 1.08
        else:
            mae_corrigida = altura_mae_cm * 0.923
        esperada = (altura_pai_cm + mae_corrigida) / 2.0
        altura = esperada + self._rng.normal(0.0, 6.5)
        return max(40.0, min(230.0, round(altura, 1)))

    # -- Peso (correlacionado com altura via BMI) ----------------------------
    def peso_from_height(self, altura_cm: float, sex: str, disease_chronic: bool = False) -> float:
        bmi = math.exp(self._rng.normal(3.0, 0.14))
        if disease_chronic:
            bmi *= 0.94
        peso = bmi * (altura_cm / 100.0) ** 2
        return max(2.0, min(300.0, round(peso, 1)))

    # -- Doenças hereditárias (PRS simplificado) -----------------------------
    _PRS_BETA = {
        "diabetes_t2": {"beta": 0.55, "threshold": 0.0},
        "hipertensao": {"beta": 0.50, "threshold": 0.05},
        "depressao": {"beta": 0.45, "threshold": 0.10},
        "daltonismo": {"beta": 1.20, "threshold": -0.2},
        "fenilcetonuria": {"beta": 1.50, "threshold": 0.1},
    }

    def prs_risk(self, condition: str, family_effects: dict | None = None, genotypes: dict | None = None) -> float:
        params = self._PRS_BETA.get(condition, {"beta": 0.5, "threshold": 0.0})
        family_effects = family_effects or {}
        f = family_effects.get(condition, 0.0)
        geno_effect = 0.0
        if genotypes:
            for k, v in genotypes.items():
                geno_effect += float(v)
        z = params["beta"] * geno_effect + f + self._rng.normal(0.0, 0.1)
        return 1.0 / (1.0 + math.exp(-z))

    def has_hereditary_disease(self, prs: float, threshold: float = 0.5) -> bool:
        return self._rng.bernoulli(min(1.0, max(0.0, prs)))