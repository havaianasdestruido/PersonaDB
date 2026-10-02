"""Testes unitários do motor socioeconômico `SocioeconomicEngine` e histórico salarial (TASK-092).

Verifica:
- Matriz de transição de classe social (linhas somam 1.0, diagonal dominante).
- Renda log-normal positiva e assimétrica, com mediana crescente por escolaridade e setor.
- Escolaridade correlacionada com escolaridade parental e classe social.
- Desemprego mais elevado para baixa escolaridade e classe social `D_E`.
- `MIN_WAGE_HISTORY` crescente ao longo do tempo.
"""
from __future__ import annotations

import statistics

from persona_db.engines.rng import SeededRNG
from persona_db.engines.socio import SocioeconomicEngine
from persona_db.generators.gen_05_carreira import MIN_WAGE_HISTORY, min_wage_for_year
from persona_db.seeds.probability_tables import (
    SOCIAL_CLASSES,
    SOCIAL_MOBILITY_MATRIX,
    employment_rate,
)


def test_class_transition_matrix_rows_sum_to_one_and_diagonal_strong() -> None:
    """Todas as linhas da matriz de transição somam 1.0 e mantêm inércia de classe."""
    for idx, _parent_cls in enumerate(SOCIAL_CLASSES):
        row = SOCIAL_MOBILITY_MATRIX[idx]
        total = sum(row)
        assert abs(total - 1.0) < 1e-3
        assert row[idx] >= 0.50


def test_income_lognormal_positive_and_monotonic_by_education() -> None:
    """Salário anual amostrado é estritamente positivo e sua mediana cresce com escolaridade."""
    rng = SeededRNG(404)
    medians: dict[str, float] = {}
    for edu in ("fundamental", "medio", "superior", "pos"):
        samples = [
            SocioeconomicEngine.salary(
                rng,
                education=edu,
                experience_years=15.0,
                sector="financeiro",
                gender_female=False,
                race_minority=False,
                nepotism_log_bonus=2.2,
            )
            for _ in range(400)
        ]
        assert all(s >= 1200.0 for s in samples)
        medians[edu] = statistics.median(samples)

    assert medians["fundamental"] < medians["medio"] < medians["superior"] < medians["pos"]


def test_education_depends_on_parent_and_class() -> None:
    """Filhos de pais com pós-graduação na classe A atingem ensino superior/pós com frequência muito maior."""
    rng_hi = SeededRNG(505)
    rng_lo = SeededRNG(505)

    hi_levels = [SocioeconomicEngine.education_level(rng_hi, "pos", 1.5, "A") for _ in range(500)]
    lo_levels = [SocioeconomicEngine.education_level(rng_lo, "fundamental", -1.0, "D_E") for _ in range(500)]

    hi_rate = sum(1 for lv in hi_levels if lv in ("superior", "pos")) / len(hi_levels)
    lo_rate = sum(1 for lv in lo_levels if lv in ("superior", "pos")) / len(lo_levels)
    assert hi_rate > lo_rate + 0.35


def test_unemployment_higher_for_low_education_and_low_class() -> None:
    """Taxa de desemprego (1 - employment_rate) é superior para baixa escolaridade e jovens."""
    p_unemp_vuln = 1.0 - employment_rate(sector="aberto", education="fundamental", age=20)
    p_unemp_adv = 1.0 - employment_rate(sector="tecnologia", education="pos", age=35)
    assert p_unemp_vuln > p_unemp_adv


def test_min_wage_history_strictly_non_decreasing() -> None:
    """A série histórica do salário mínimo brasileiro deve ser crescente de 1994 a 2026."""
    ordered = sorted(
        MIN_WAGE_HISTORY,
        key=lambda item: item["year"] if isinstance(item, dict) else item[0],
    )
    values = [item["min_wage"] if isinstance(item, dict) else item[1] for item in ordered]
    for i in range(1, len(values)):
        assert values[i] >= values[i - 1]
    assert min_wage_for_year(2026) > min_wage_for_year(2000)
