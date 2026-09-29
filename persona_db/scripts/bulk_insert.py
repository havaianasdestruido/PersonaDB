"""Load JSON snapshots into PostgreSQL using parameterized batch inserts.

This loader intentionally accepts only known, unqualified table identifiers and
uses psycopg2's execute_values for bounded-memory batches. Apply schema first.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")


def load_dataset(database_url: str, source: Path, page_size: int = 1000) -> int:
    """Insert table rows from a generated JSON snapshot in one transaction."""
    if page_size < 1:
        raise ValueError("page_size must be positive")
    try:
        import psycopg2
        from psycopg2.extras import execute_values
    except ImportError as exc:
        raise RuntimeError("Install persona-db dependencies to use PostgreSQL loading") from exc
    dataset: dict[str, list[dict[str, Any]]] = json.loads(source.read_text(encoding="utf-8"))
    total = 0
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            # Natural dependency order: persona first, then remaining entities.
            for table in sorted(dataset, key=lambda t: (t != "pessoa", t)):
                rows = dataset[table]
                if table.startswith("_") or not rows:
                    continue
                if not _IDENTIFIER.fullmatch(table):
                    raise ValueError(f"Unsafe table name: {table!r}")
                if any(not isinstance(row, dict) for row in rows):
                    raise ValueError(f"Every {table} row must be an object")
                columns = sorted({key for row in rows for key in row})
                if not columns or any(not _IDENTIFIER.fullmatch(c) for c in columns):
                    raise ValueError(f"Unsafe or empty column set for {table}")
                # Missing keys are SQL NULL; JSON values are explicitly adapted.
                values = [tuple(json.dumps(row.get(c), ensure_ascii=False) if isinstance(row.get(c), (dict, list)) else row.get(c) for c in columns) for row in rows]
                sql = f'INSERT INTO "{table}" ({", ".join(chr(34) + c + chr(34) for c in columns)}) VALUES %s'
                execute_values(cur, sql, values, page_size=page_size)
                total += len(values)
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL"))
    parser.add_argument("--page-size", type=int, default=1000)
    args = parser.parse_args()
    if not args.database_url:
        parser.error("DATABASE_URL or --database-url is required")
    print(f"Inserted {load_dataset(args.database_url, args.input, args.page_size)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
