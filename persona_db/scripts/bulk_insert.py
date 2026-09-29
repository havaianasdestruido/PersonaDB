"""Stream JSON table rows into PostgreSQL using bounded insert batches.

This loader accepts unqualified table identifiers and uses ijson to avoid
loading the whole dataset (or even one complete table) into memory. Apply the
schema first. Install dependencies with ``pip install -e persona_db``.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

_IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")


def _table_names(source: Path) -> list[str]:
    """Read top-level JSON keys without materializing their values."""
    import ijson

    names = []
    with source.open("rb") as stream:
        for prefix, event, value in ijson.parse(stream):
            if prefix == "" and event == "map_key":
                names.append(value)
    return sorted(names, key=lambda name: (name != "pessoa", name))


def _rows(source: Path, table: str) -> Iterator[dict[str, Any]]:
    import ijson

    with source.open("rb") as stream:
        yield from ijson.items(stream, f"{table}.item")


def _columns(source: Path, table: str) -> list[str]:
    """Discover a table's union of keys while keeping only column names in memory."""
    columns: set[str] = set()
    for row in _rows(source, table):
        if not isinstance(row, dict):
            raise TypeError(f"Every {table} row must be an object")
        columns.update(row)
    result = sorted(columns)
    if not result or any(not _IDENTIFIER.fullmatch(column) for column in result):
        raise ValueError(f"Unsafe or empty column set for {table}")
    return result


def load_dataset(database_url: str, source: Path, page_size: int = 1000) -> int:
    """Insert table rows from a JSON snapshot in bounded-memory batches."""
    if page_size < 1:
        raise ValueError("page_size must be positive")
    try:
        import ijson  # noqa: F401 - validate the streaming parser dependency early
        import psycopg2
        from psycopg2.extras import execute_values
    except ImportError as exc:
        raise RuntimeError("Install persona-db dependencies to use PostgreSQL loading") from exc

    total = 0
    with psycopg2.connect(database_url) as conn, conn.cursor() as cur:
        for table in _table_names(source):
            if table.startswith("_"):
                continue
            if not _IDENTIFIER.fullmatch(table):
                raise ValueError(f"Unsafe table name: {table!r}")
            columns = _columns(source, table)
            if not columns:
                continue
            sql = f'INSERT INTO "{table}" ({", ".join(chr(34) + c + chr(34) for c in columns)}) VALUES %s'
            batch: list[tuple[Any, ...]] = []
            for row in _rows(source, table):
                if not isinstance(row, dict):
                    raise TypeError(f"Every {table} row must be an object")
                batch.append(tuple(
                    json.dumps(row.get(c), ensure_ascii=False)
                    if isinstance(row.get(c), (dict, list)) else row.get(c)
                    for c in columns
                ))
                if len(batch) == page_size:
                    execute_values(cur, sql, batch, page_size=page_size)
                    total += len(batch)
                    batch.clear()
            if batch:
                execute_values(cur, sql, batch, page_size=page_size)
                total += len(batch)
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
