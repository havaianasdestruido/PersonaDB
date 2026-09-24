"""Run the currently implemented synthetic-person pipeline.

The command deliberately produces a portable JSON snapshot before any database
work.  This makes deterministic generation usable in CI and gives bulk loaders
a single, documented input contract.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

from persona_db.generators import gen_00_pessoa, gen_01_identidade, gen_02_genealogia, gen_03_saude
from persona_db.validators.run_validators import validate_dataset


def generate_dataset(n_people: int, seed: int = 7, today: date | None = None) -> dict[str, list[dict[str, Any]]]:
    """Generate all available domains in their dependency order."""
    personas = gen_00_pessoa.generate_personas(n_people, seed=seed, today=today)
    tables: dict[str, list[dict[str, Any]]] = {"pessoa": personas}
    for domain in (
        gen_02_genealogia.generate(personas, seed=seed, today=today),
        gen_01_identidade.generate_all(personas, seed=seed),
        gen_03_saude.generate(personas, seed=seed, today=today),
    ):
        for table, rows in domain.items():
            tables.setdefault(table, []).extend(rows)
    return tables


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a deterministic PersonaDB JSON dataset.")
    parser.add_argument("--people", type=int, default=100, help="number of personas (default: 100)")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--today", type=date.fromisoformat, default=None, metavar="YYYY-MM-DD")
    parser.add_argument("--output", type=Path, default=Path("dataset.json"))
    args = parser.parse_args()
    if args.people < 1:
        parser.error("--people must be positive")
    dataset = generate_dataset(args.people, args.seed, args.today)
    report = validate_dataset(dataset, today=args.today)
    if report["critical_violations"]:
        raise SystemExit(f"generation produced {report['critical_violations']} critical violations")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dataset, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote {sum(map(len, dataset.values()))} rows in {len(dataset)} tables to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
