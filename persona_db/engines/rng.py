"""Deterministic seeded RNG wrapper for all PersonaDB engines.

Provides SeededRNG — a thin wrapper around numpy.random.Generator with
reproducible fork semantics. Every engine MUST use SeededRNG instead of
the plain `random` module so that simulations are fully reproducible.

Ownership: Agent 2. Sibling agents import SeededRNG; never edit this file.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Sequence

import numpy as np


class SeededRNG:
    """Deterministic RNG wrapping a numpy Generator.

    Two SeededRNG instances seeded with the same parameters produce
    identical sequences regardless of global numpy state.
    """

    def __init__(self, master_seed: int | None = None) -> None:
        if master_seed is None:
            master_seed = int.from_bytes(os.urandom(8), "big")
        self._master_seed = int(master_seed)
        self._rng = np.random.default_rng(self._master_seed)

    # ------------------------------------------------------------------
    # Forking
    # ------------------------------------------------------------------

    def fork(self, persona_id: str, domain: str, salt: str = "") -> "SeededRNG":
        """Return a new SeededRNG derived deterministically from this one.

        seed_int = int.from_bytes(blake2b(master|persona|domain|salt)[:8], 'big')
        so identical (seed, persona_id, domain) always yield identical
        sequences while sibling personalities stay decorrelated.
        """
        payload = f"{self._master_seed}|{persona_id}|{domain}|{salt}"
        seed_bytes = hashlib.blake2b(payload.encode()).digest()[:8]
        seed_int = int.from_bytes(seed_bytes, "big")
        return SeededRNG(master_seed=seed_int)

    # ------------------------------------------------------------------
    # Sampling helpers
    # ------------------------------------------------------------------

    def bernoulli(self, p: float) -> bool:
        return bool(self._rng.random() < p)

    def choice(
        self,
        options: Sequence[Any],
        weights: Sequence[float] | None = None,
    ) -> Any:
        w = None
        if weights is not None:
            w = np.asarray(weights, dtype=np.float64)
            s = w.sum()
            if s > 0:
                w = w / s
        return self._rng.choice(options, p=w)

    def beta_sample(self, alpha: float, beta: float) -> float:
        return float(self._rng.beta(alpha, beta))

    def normal_clipped(
        self, mu: float, sigma: float, low: float, high: float
    ) -> float:
        raw = float(self._rng.normal(mu, sigma))
        return max(low, min(high, raw))

    def uniform(self, low: float, high: float) -> float:
        return float(self._rng.uniform(low, high))

    def dirichlet(self, alphas: Sequence[float]) -> np.ndarray:
        return self._rng.dirichlet(np.asarray(alphas, dtype=np.float64))

    def integer(self, low: int, high: int) -> int:
        """Inclusive random integer in [low, high]."""
        return int(self._rng.integers(low, high + 1))

    def normal(self, mu: float, sigma: float) -> float:
        return float(self._rng.normal(mu, sigma))

    def poisson(self, lam: float) -> int:
        return int(self._rng.poisson(lam))

    def log_normal(self, mu: float, sigma: float) -> float:
        return float(self._rng.lognormal(mu, sigma))

    # ------------------------------------------------------------------
    # Access to underlying generator
    # ------------------------------------------------------------------

    @property
    def rng(self) -> np.random.Generator:
        return self._rng


# ======================================================================
# Module-level helpers
# ======================================================================


def new_rng(seed: int | None = None) -> SeededRNG:
    """Factory shortcut."""
    return SeededRNG(master_seed=seed)


_LOG_DIR = Path(__file__).resolve().parent.parent / "data"
_LOG_FILE = _LOG_DIR / "rng_log.jsonl"


def register_seed(persona_id: str, info: dict) -> None:
    """Append a JSON record to persona_db/data/rng_log.jsonl.

    The data directory is created if missing. Write failures are silently
    ignored so seeding/logging never breaks a simulation run.
    """
    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        record = {"persona_id": persona_id, **info}
        with open(_LOG_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass