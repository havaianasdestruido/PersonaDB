"""Generate Markdown documentation from PostgreSQL's live catalog."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

_FK_QUERY = """SELECT kcu.column_name, ccu.table_name, ccu.column_name
  FROM information_schema.table_constraints tc
  JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name AND tc.constraint_schema=kcu.constraint_schema
  JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name=tc.constraint_name AND ccu.constraint_schema=tc.constraint_schema
  WHERE tc.constraint_type='FOREIGN KEY' AND tc.table_schema='public' AND tc.table_name=%s
  ORDER BY kcu.column_name"""


def render(database_url: str) -> str:
    try:
        import psycopg2
    except ImportError as exc:
        raise RuntimeError("Install psycopg2-binary to inspect the schema") from exc
    result = ["# PersonaDB PostgreSQL schema", "", "Generated from the live public schema catalog.", ""]
    with psycopg2.connect(database_url) as conn, conn.cursor() as cur:
        cur.execute("""SELECT c.table_name, c.column_name, c.data_type, c.is_nullable,
          c.column_default, pgd.description
          FROM information_schema.columns c
          LEFT JOIN pg_catalog.pg_class pc ON pc.relname=c.table_name
          LEFT JOIN pg_catalog.pg_namespace pn ON pn.oid=pc.relnamespace AND pn.nspname=c.table_schema
          LEFT JOIN pg_catalog.pg_description pgd ON pgd.objoid=pc.oid AND pgd.objsubid=c.ordinal_position
          WHERE c.table_schema='public' ORDER BY c.table_name,c.ordinal_position""")
        rows = cur.fetchall()
        current = None
        for table, column, typ, nullable, default, description in rows:
            if current != table:
                if current is not None:
                    cur.execute(_FK_QUERY, (current,))
                    fks = cur.fetchall()
                    if fks:
                        result += ["", "Foreign keys: " + ", ".join(f"`{a}` → `{b}.{c}`" for a, b, c in fks), ""]
                current = table
                result += [f"## `{table}`", "", "| Column | Type | Nullable | Default | Description |", "|---|---|---:|---|---|"]
            values = [column, typ, nullable, default or "", description or ""]
            result.append("| " + " | ".join(str(v).replace("|", "\\|").replace("\n", " ") for v in values) + " |")
        if current is not None:
            cur.execute(_FK_QUERY, (current,))
            fks = cur.fetchall()
            if fks:
                result += ["", "Foreign keys: " + ", ".join(f"`{a}` → `{b}.{c}`" for a, b, c in fks), ""]
    return "\n".join(result) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL"))
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "docs" / "SCHEMA.md")
    args = parser.parse_args()
    if not args.database_url:
        parser.error("DATABASE_URL is required")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render(args.database_url), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
