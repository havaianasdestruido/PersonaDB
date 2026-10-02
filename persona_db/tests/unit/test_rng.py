"""Testes unitários do motor de aleatoriedade determinística `SeededRNG` (TASK-090).

Verifica:
- Determinismo: mesma seed produz exatamente a mesma sequência.
- Fork isolamento: sub-seeds distintas por `(persona_id, domain)` não interferem entre si.
- Convergência estatística para os parâmetros teóricos (`N = 10_000`) das
  distribuições Normal, Log-Normal, Poisson, Beta e Dirichlet.
"""
from __future__ import annotations

import math

import numpy as np
from persona_db.engines.rng import SeededRNG, new_rng


def test_determinism_same_seed_same_sequence() -> None:
    """Mesma semente deve gerar sequência idêntica em todos os samplers."""
    rng_a = new_rng(2026)
    rng_b = new_rng(2026)

    seq_a = [
        (
            rng_a.uniform(0.0, 10.0),
            rng_a.normal(5.0, 2.0),
            rng_a.log_normal(1.0, 0.5),
            rng_a.poisson(3.2),
            rng_a.beta_sample(2.0, 5.0),
            rng_a.integer(1, 100),
        )
        for _ in range(100)
    ]
    seq_b = [
        (
            rng_b.uniform(0.0, 10.0),
            rng_b.normal(5.0, 2.0),
            rng_b.log_normal(1.0, 0.5),
            rng_b.poisson(3.2),
            rng_b.beta_sample(2.0, 5.0),
            rng_b.integer(1, 100),
        )
        for _ in range(100)
    ]
    assert seq_a == seq_b


def test_fork_isolation_across_personas_and_domains() -> None:
    """Consumir amostras em um fork não deve alterar o estado do RNG pai nem de outros forks."""
    master_1 = SeededRNG(99)
    master_2 = SeededRNG(99)

    fork_1_health = master_1.fork("persona-001", "saude")
    for _ in range(500):
        fork_1_health.normal(0.0, 1.0)
    fork_1_fin = master_1.fork("persona-001", "financas")

    # Mesmo sem ter consumido o fork de saúde em master_2, o fork de finanças é idêntico
    fork_2_fin = master_2.fork("persona-001", "financas")
    assert [fork_1_fin.uniform(0.0, 1.0) for _ in range(50)] == [fork_2_fin.uniform(0.0, 1.0) for _ in range(50)]
    assert master_1.fork("persona-001", "saude")._master_seed != master_1.fork("persona-001", "financas")._master_seed
    assert master_1.fork("persona-001", "saude")._master_seed != master_1.fork("persona-002", "saude")._master_seed


def test_distributions_converge_at_n_10000() -> None:
    """Amostras de tamanho N = 10_000 devem convergir para média e variância teóricas."""
    n = 10_000
    rng = SeededRNG(42)

    # 1. Normal(mu=10.0, sigma=2.5)
    norm_samples = np.array([rng.normal(10.0, 2.5) for _ in range(n)])
    assert abs(float(norm_samples.mean()) - 10.0) < 0.08
    assert abs(float(norm_samples.std()) - 2.5) < 0.08

    # 2. Log-Normal(mu=1.2, sigma=0.4) -> E[X] = exp(mu + sigma^2 / 2)
    mu, sigma = 1.2, 0.4
    ln_samples = np.array([rng.log_normal(mu, sigma) for _ in range(n)])
    expected_ln_mean = math.exp(mu + (sigma**2) / 2.0)
    assert abs(float(ln_samples.mean()) - expected_ln_mean) < 0.06

    # 3. Poisson(lam=4.5) -> E[X] = Var[X] = 4.5
    pois_samples = np.array([rng.poisson(4.5) for _ in range(n)])
    assert abs(float(pois_samples.mean()) - 4.5) < 0.08
    assert abs(float(pois_samples.var()) - 4.5) < 0.15

    # 4. Beta(a=2.0, b=6.0) -> E[X] = a / (a + b) = 0.25
    beta_samples = np.array([rng.beta_sample(2.0, 6.0) for _ in range(n)])
    assert abs(float(beta_samples.mean()) - 0.25) < 0.01

    # 5. Dirichlet(alphas=[2.0, 3.0, 5.0]) -> E[X] = [0.2, 0.3, 0.5], soma = 1.0
    dir_samples = np.array([rng.dirichlet([2.0, 3.0, 5.0]) for _ in range(n)])
    means = dir_samples.mean(axis=0)
    assert np.allclose(dir_samples.sum(axis=1), 1.0, atol=1e-9)
    assert np.allclose(means, [0.2, 0.3, 0.5], atol=0.01)
