"""Gera documentação Markdown (`docs/SCHEMA.md`) do schema PostgreSQL do PersonaDB (TASK-100).

Lê o catálogo vivo `information_schema` quando `--database-url` é fornecido ou
faz o parsing determinístico dos arquivos DDL em `persona_db/sql/schema/*.sql`,
produzindo:
- Índice completo de todas as tabelas por domínio (00 a 25).
- Colunas, tipos, chaves primárias, chaves estrangeiras, constraints `CHECK` e
  comentários (`COMMENT ON TABLE`) para cada tabela.
- Diagramas ER textuais em formato Mermaid por domínio.
"""
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import Any

_FK_QUERY = """SELECT kcu.column_name, ccu.table_name, ccu.column_name
  FROM information_schema.table_constraints tc
  JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name AND tc.constraint_schema=kcu.constraint_schema
  JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name=tc.constraint_name AND ccu.constraint_schema=tc.constraint_schema
  WHERE tc.constraint_type='FOREIGN KEY' AND tc.table_schema='public' AND tc.table_name=%s
  ORDER BY kcu.column_name"""

_CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+([a-zA-Z0-9_]+)\s*\((.*?)\)\s*(?:PARTITION\s+BY[^;]+)?;",
    re.DOTALL | re.IGNORECASE,
)
_COMMENT_TABLE_RE = re.compile(
    r"COMMENT\s+ON\s+TABLE\s+([a-zA-Z0-9_]+)\s+IS\s+'([^']*)';",
    re.IGNORECASE,
)
_ALTER_FK_RE = re.compile(
    r"ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?([a-zA-Z0-9_]+)\s+ADD\s+CONSTRAINT\s+[a-zA-Z0-9_]+\s+FOREIGN\s+KEY\s*\(([a-zA-Z0-9_]+)\)\s+REFERENCES\s+([a-zA-Z0-9_]+)\s*\(([a-zA-Z0-9_]+)\)",
    re.IGNORECASE,
)


def render(database_url: str) -> str:
    """Renderiza a documentação do schema conectando a um banco PostgreSQL ativo."""
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


def _parse_sql_file(sql_path: Path) -> dict[str, Any]:
    """Extrai tabelas, colunas, chaves estrangeiras e comentários de um arquivo `.sql`."""
    content = sql_path.read_text(encoding="utf-8")
    comments = {m.group(1): m.group(2) for m in _COMMENT_TABLE_RE.finditer(content)}
    alter_fks: dict[str, list[tuple[str, str, str]]] = {}
    for m in _ALTER_FK_RE.finditer(content):
        alter_fks.setdefault(m.group(1), []).append((m.group(2), m.group(3), m.group(4)))

    tables: list[dict[str, Any]] = []
    for match in _CREATE_TABLE_RE.finditer(content):
        tname = match.group(1)
        if re.search(r"_\d{4}$", tname) or tname.endswith("_default"):
            continue
        body = match.group(2)
        cols: list[dict[str, str]] = []
        fks: list[tuple[str, str, str]] = list(alter_fks.get(tname, []))

        for raw_line in body.splitlines():
            line = raw_line.strip().rstrip(",")
            if not line or line.startswith("--"):
                continue
            upper = line.upper()
            if upper.startswith(("PRIMARY KEY", "CONSTRAINT", "UNIQUE", "CHECK", "FOREIGN KEY")):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            col_name = parts[0]
            col_type = parts[1]
            rest = " ".join(parts[2:])
            is_pk = "PRIMARY KEY" in upper
            not_null = "NOT NULL" in upper or is_pk
            fk_match = re.search(r"REFERENCES\s+([a-zA-Z0-9_]+)\s*\(([a-zA-Z0-9_]+)\)", rest, re.IGNORECASE)
            fk_target = ""
            if fk_match:
                ref_tbl, ref_col = fk_match.group(1), fk_match.group(2)
                fk_target = f"`{ref_tbl}({ref_col})`"
                fks.append((col_name, ref_tbl, ref_col))
            check_match = re.search(r"CHECK\s*\((.*)\)", rest, re.IGNORECASE)
            constraint_str = f"CHECK ({check_match.group(1)})" if check_match else ("PK" if is_pk else "")
            cols.append({
                "name": col_name,
                "type": col_type,
                "nullable": "NO" if not_null else "YES",
                "fk": fk_target,
                "constraints": constraint_str,
            })

        tables.append({
            "name": tname,
            "comment": comments.get(tname, ""),
            "columns": cols,
            "fks": fks,
        })
    return {"file": sql_path.name, "tables": tables}


def render_from_sql_dir(schema_dir: Path | None = None) -> str:
    """Renderiza `docs/SCHEMA.md` diretamente dos arquivos SQL em `persona_db/sql/schema`."""
    schema_dir = schema_dir or (Path(__file__).resolve().parents[1] / "sql" / "schema")
    sql_files = sorted(
        p for p in schema_dir.glob("*.sql")
        if p.name[:2].isdigit() and int(p.name[:2]) <= 26
    )

    domains_data = [_parse_sql_file(p) for p in sql_files]
    total_tables = sum(len(d["tables"]) for d in domains_data)

    lines = [
        "# Documentação do Schema Relacional — PersonaDB",
        "",
        f"Catálogo gerado automaticamente a partir dos arquivos DDL em `persona_db/sql/schema/` (**{len(domains_data)} domínios**, **{total_tables} tabelas**).",
        "",
        "## Índice por Domínio",
        "",
    ]

    for dom in domains_data:
        dom_slug = dom["file"].replace(".sql", "")
        t_links = ", ".join(f"[`{t['name']}`](#{t['name']})" for t in dom["tables"])
        lines.append(f"- **{dom_slug}** ({len(dom['tables'])} tabelas): {t_links}")
    lines.append("")

    for dom in domains_data:
        dom_slug = dom["file"].replace(".sql", "")
        lines.append(f"## Domínio `{dom_slug}`")
        lines.append("")

        # Diagrama ER Mermaid do domínio
        lines.append("```mermaid")
        lines.append("erDiagram")
        for tbl in dom["tables"]:
            for col_name, ref_tbl, _ref_col in tbl["fks"]:
                lines.append(f"    {ref_tbl} ||--o{{ {tbl['name']} : \"{col_name}\"")
        lines.append("```")
        lines.append("")

        for tbl in dom["tables"]:
            lines.append(f"### `{tbl['name']}`")
            if tbl["comment"]:
                lines.append("")
                lines.append(f"> {tbl['comment']}")
            lines.append("")
            lines.append("| Coluna | Tipo | Nulo | FK | Constraints |")
            lines.append("|---|---|:---:|---|---|")
            for col in tbl["columns"]:
                c_str = col["constraints"].replace("|", "\\|")
                lines.append(
                    f"| `{col['name']}` | `{col['type']}` | {col['nullable']} | {col['fk']} | {c_str} |"
                )
            lines.append("")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada CLI para geração de `docs/SCHEMA.md`."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL"))
    parser.add_argument(
        "--schema-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "sql" / "schema",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "docs" / "SCHEMA.md",
    )
    args = parser.parse_args(argv)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.database_url:
        content = render(args.database_url)
    else:
        content = render_from_sql_dir(args.schema_dir)
    args.output.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
