"""Small reproducible benchmark for the in-memory generation pipeline."""
from __future__ import annotations

import argparse
import time

from persona_db.scripts.generate import generate_dataset


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--people", type=int, default=1_000)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    start = time.perf_counter()
    dataset = generate_dataset(args.people, args.seed)
    elapsed = time.perf_counter() - start
    print(f"{args.people} personas; {sum(map(len, dataset.values()))} rows; {elapsed:.3f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
