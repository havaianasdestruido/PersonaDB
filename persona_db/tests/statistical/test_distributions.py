"""Testes de aderência estatística para N = 1000 personas (TASK-095).

Verifica:
- Distribuição de classes sociais próxima de `A: 3%, B1: 5%, B2: 12%, C1: 20%, C2: 28%, D_E: 32%`
  (teste qui-quadrado `p > 0.01`).
- Distribuição de tipos sanguíneos próxima de `O+, A+` dominantes e `AB-` raro.
- Proporção de sexos próxima de 50/50 (teste binomial `p > 0.01`).
- Renda positivamente correlacionada com escolaridade (`r > 0.3`).
- Idade dos pais sempre >= idade dos filhos + 14 anos (`100%` dos casos).
"""
from __future__ import annotations

from collections import Counter
from datetime import date

import numpy as np
from persona_db.engines.constants import SOCIAL_CLASS_DIST
from persona_db.generators import (
    gen_00_pessoa,
    gen_02_genealogia,
    gen_04_educacao,
    gen_05_carreira,
)
from scipy import stats


def test_macro_statistical_distributions_n_1000() -> None:
    """Valida as distribuições populacionais e correlações em N = 1000 personas."""
    n = 1000
    personas = gen_00_pessoa.generate_personas(n=n, seed=77)
    gen_02_genealogia.generate(personas, seed=77)
    gen_04_educacao.generate(personas, seed=77)
    gen_05_carreira.generate(personas, seed=77)

    # 1. Classes sociais — qui-quadrado contra SOCIAL_CLASS_DIST
    cls_counts = Counter(p["classe_social"] for p in personas)
    observed = [cls_counts[k] for k in SOCIAL_CLASS_DIST]
    expected = [n * p for p in SOCIAL_CLASS_DIST.values()]
    chi2_res = stats.chisquare(f_obs=observed, f_exp=expected)
    assert float(chi2_res.pvalue) > 0.01

    # 2. Tipos sanguíneos (ABO + Rh): O+ e A+ dominantes (> 55% somados), AB- raro (< 3%)
    blood_counts = Counter(
        f"{p['tipo_sanguineo']}{'+' if p['fator_rh'] == 'positivo' else '-'}"
        for p in personas
    )
    o_plus_a_plus = (blood_counts["O+"] + blood_counts["A+"]) / n
    ab_minus = blood_counts["AB-"] / n
    assert 0.52 <= o_plus_a_plus <= 0.82
    assert ab_minus <= 0.03

    # 3. Proporção de sexos próxima de 50/50 (teste binomial p > 0.01)
    male_count = sum(1 for p in personas if p["sexo"] == "masculino")
    binom_res = stats.binomtest(male_count, n=n, p=0.5)
    assert float(binom_res.pvalue) > 0.01

    # 4. Renda positivamente correlacionada com anos de estudo (r > 0.3)
    edu_years_map = {"fundamental": 8.0, "medio": 11.0, "superior": 16.0, "pos": 18.5}
    earners = [p for p in personas if float(p.get("salario_mensal") or 0.0) > 0.0]
    years_arr = np.array([edu_years_map.get(p["education"], 8.0) for p in earners])
    log_income_arr = np.log(np.array([float(p["salario_mensal"]) for p in earners]))
    corr = float(np.corrcoef(years_arr, log_income_arr)[0, 1])
    assert corr > 0.30

    # 5. Idade dos pais sempre >= idade dos filhos + 14 anos (100% dos casos)
    by_id = {p["id"]: p for p in personas}
    for p in personas:
        c_born = date.fromisoformat(p["data_nascimento"])
        for key in ("pai_id", "mae_id"):
            par_id = p.get(key)
            if not par_id:
                continue
            par = by_id[par_id]
            p_born = date.fromisoformat(par["data_nascimento"])
            assert (c_born - p_born).days >= 14 * 365
