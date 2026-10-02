#!/usr/bin/env python3
"""Gera a documentação de referência do PersonaDB consumida pelo Docusaurus.

Executado por `npm run gen:docs` (e automaticamente antes de `npm start` e
`npm run build`). Usa **apenas a biblioteca padrão** do Python — nenhuma
dependência do pacote `persona-db` precisa estar instalada, pois tudo é obtido
por análise estática (`ast`) do código-fonte e por parsing dos arquivos DDL.

Artefatos produzidos (todos ignorados pelo Git, pois são derivados do código):

    website/docs/referencia-api/**      → uma página por módulo Python
    website/docs/schema/**              → uma página por arquivo DDL
    website/docs/geradores/catalogo.md  → catálogo dos 24 geradores
    website/docs/validadores/regras.md  → catálogo das regras de validação
    website/src/data/stats.json         → métricas exibidas na página inicial
"""
from __future__ import annotations

import ast
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

WEBSITE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WEBSITE_ROOT.parent
PKG_ROOT = REPO_ROOT / "persona_db"
DOCS = WEBSITE_ROOT / "docs"
DATA_DIR = WEBSITE_ROOT / "src" / "data"

GITHUB_BLOB = "https://github.com/havaianasdestruido/PersonaDB/blob/main"

GENERATED_BANNER = (
    "<!-- Arquivo gerado automaticamente por website/scripts/generate_reference.py. "
    "Não edite manualmente: edite o código-fonte e rode `npm run gen:docs`. -->"
)

# Pacotes Python documentados, na ordem em que aparecem na sidebar.
PACKAGES: list[dict[str, Any]] = [
    {
        "dir": "engines",
        "label": "engines/",
        "description": "Motores matemáticos e probabilísticos.",
        "position": 2,
    },
    {
        "dir": "generators",
        "label": "generators/",
        "description": "Geradores por domínio do schema.",
        "position": 3,
    },
    {
        "dir": "validators",
        "label": "validators/",
        "description": "Validadores de consistência do dataset.",
        "position": 4,
    },
    {
        "dir": "scripts",
        "label": "scripts/",
        "description": "CLIs de geração, carga, exportação e documentação.",
        "position": 5,
    },
    {
        "dir": "seeds",
        "label": "seeds/",
        "description": "Catálogos determinísticos e tabelas de probabilidade.",
        "position": 6,
    },
    {
        "dir": "tests",
        "label": "tests/",
        "description": "Suíte de testes unitários, de integração e estatísticos.",
        "position": 7,
        "tests": True,
    },
]


# ---------------------------------------------------------------------------
# Utilidades de texto
# ---------------------------------------------------------------------------
def md_escape(text: str) -> str:
    """Neutraliza `<` fora de trechos de código para Markdown/CommonMark."""
    parts = re.split(r"(`[^`]*`)", text)
    return "".join(p if p.startswith("`") else p.replace("<", "&lt;") for p in parts)


def clean_doc(doc: str | None) -> str:
    return md_escape((doc or "").strip())


def summary_of(doc: str | None, fallback: str = "") -> str:
    """Primeira frase/linha de uma docstring, para front matter e tabelas."""
    text = (doc or "").strip()
    if not text:
        return fallback
    first = text.split("\n\n")[0].replace("\n", " ").strip()
    first = re.sub(r"\s+", " ", first)
    return first[:240]


def yaml_quote(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def table(headers: Iterable[str], rows: Iterable[Iterable[str]]) -> list[str]:
    headers = list(headers)
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for row in rows:
        cells = [str(c).replace("|", "\\|").replace("\n", " ") for c in row]
        out.append("| " + " | ".join(cells) + " |")
    out.append("")
    return out


def write(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(lines).rstrip() + "\n"
    if not path.exists() or path.read_text(encoding="utf-8") != body:
        path.write_text(body, encoding="utf-8")


def doc_stem(rel_path: str) -> str:
    """Nome do arquivo .md para um módulo.

    Docusaurus ignora arquivos iniciados por `_` (tratados como partials),
    então `__init__.py` vira `package-init.md`.
    """
    stem = Path(rel_path).stem
    return "package-init" if stem.startswith("_") else stem


def category(
    path: Path, label: str, position: int, description: str, slug: str | None = None
) -> None:
    link: dict[str, Any] = {"type": "generated-index", "description": description}
    if slug:
        link["slug"] = slug
    payload = {"label": label, "position": position, "link": link}
    path.mkdir(parents=True, exist_ok=True)
    (path / "_category_.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def front_matter(title: str, label: str, description: str, position: int) -> list[str]:
    return [
        "---",
        f"title: {yaml_quote(title)}",
        f"sidebar_label: {yaml_quote(label)}",
        f"description: {yaml_quote(description or title)}",
        f"sidebar_position: {position}",
        "---",
        "",
        GENERATED_BANNER,
        "",
    ]


# ---------------------------------------------------------------------------
# Análise estática de módulos Python
# ---------------------------------------------------------------------------
@dataclass
class FunctionDoc:
    name: str
    signature: str
    doc: str
    lineno: int
    decorators: list[str] = field(default_factory=list)


@dataclass
class ClassDoc:
    name: str
    bases: list[str]
    doc: str
    lineno: int
    attributes: list[tuple[str, str]] = field(default_factory=list)
    methods: list[FunctionDoc] = field(default_factory=list)


@dataclass
class ModuleDoc:
    rel_path: str
    dotted: str
    doc: str
    loc: int
    constants: list[tuple[str, str, str]] = field(default_factory=list)
    functions: list[FunctionDoc] = field(default_factory=list)
    classes: list[ClassDoc] = field(default_factory=list)
    table_keys: set[str] = field(default_factory=set)
    imports: list[str] = field(default_factory=list)


def _unparse(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover - defensivo
        return "..."


def _value_preview(node: ast.AST | None, limit: int = 110) -> str:
    text = _unparse(node)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    return text


def _function_doc(node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionDoc:
    args = _unparse(node.args)
    returns = _unparse(node.returns)
    prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
    signature = f"{prefix}{node.name}({args})" + (f" -> {returns}" if returns else "")
    return FunctionDoc(
        name=node.name,
        signature=signature,
        doc=ast.get_docstring(node) or "",
        lineno=node.lineno,
        decorators=[_unparse(d) for d in node.decorator_list],
    )


# Nomes de parâmetros que recebem tabelas já geradas por outros módulos: o que
# é escrito neles pertence ao gerador de origem, não ao módulo atual.
_INPUT_TABLE_PARAMS = {"existing_tables", "dataset", "tables", "previous"}


def _table_keys(tree: ast.AST) -> set[str]:
    """Nomes de tabela *produzidos* pelo módulo.

    Detecta os padrões de escrita usados pelos geradores do PersonaDB:

    * `rows = {"tabela": []}` — dicionário de acumulação;
    * `return {"tabela": _monta_tabela(...)}` — dicionário devolvido;
    * `rows["tabela"].append(...)` / `.extend(...)`;
    * `rows["tabela"] = [...]` e `rows.setdefault("tabela", [])`.

    Evita dois tipos de falso positivo: leituras (`row["nota"]`,
    `existing_tables["imovel"]`) e escritas em tabelas de entrada
    (`existing_tables["contrato_trabalho"] = ...`), que pertencem ao gerador
    que as criou.
    """
    keys: set[str] = set()
    returned_dicts = {
        id(node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict)
    }

    def _is_input(node: ast.AST) -> bool:
        return isinstance(node, ast.Name) and node.id in _INPUT_TABLE_PARAMS

    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            # Num dicionário devolvido, qualquer valor conta (lista literal ou
            # chamada de função); fora dele, só listas literais.
            any_value = id(node) in returned_dicts
            for key, value in zip(node.keys, node.values):
                if (
                    isinstance(key, ast.Constant)
                    and isinstance(key.value, str)
                    and (any_value or isinstance(value, ast.List))
                ):
                    keys.add(key.value)
        elif (
            isinstance(node, ast.Subscript)
            and isinstance(node.ctx, ast.Store)
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
            and not _is_input(node.value)
        ):
            keys.add(node.slice.value)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            func = node.func
            if func.attr in ("append", "extend"):
                target = func.value
                if (
                    isinstance(target, ast.Subscript)
                    and isinstance(target.slice, ast.Constant)
                    and isinstance(target.slice.value, str)
                    and not _is_input(target.value)
                ):
                    keys.add(target.slice.value)
            elif func.attr == "setdefault" and node.args and not _is_input(func.value):
                first = node.args[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    keys.add(first.value)
    return keys


def parse_module(path: Path) -> ModuleDoc:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    rel = path.relative_to(REPO_ROOT).as_posix()
    dotted = rel[:-3].replace("/", ".")
    mod = ModuleDoc(
        rel_path=rel,
        dotted=dotted,
        doc=ast.get_docstring(tree) or "",
        loc=len(source.splitlines()),
    )

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                mod.functions.append(_function_doc(node))
        elif isinstance(node, ast.ClassDef):
            cls = ClassDoc(
                name=node.name,
                bases=[_unparse(b) for b in node.bases],
                doc=ast.get_docstring(node) or "",
                lineno=node.lineno,
            )
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if sub.name.startswith("_") and sub.name != "__init__":
                        continue
                    cls.methods.append(_function_doc(sub))
                elif isinstance(sub, ast.AnnAssign) and isinstance(sub.target, ast.Name):
                    if not sub.target.id.startswith("_"):
                        cls.attributes.append((sub.target.id, _value_preview(sub.value)))
                elif isinstance(sub, ast.Assign):
                    for target in sub.targets:
                        if isinstance(target, ast.Name) and not target.id.startswith("_"):
                            cls.attributes.append((target.id, _value_preview(sub.value)))
            mod.classes.append(cls)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            if not name.startswith("_") and name != "__all__":
                mod.constants.append(
                    (name, _unparse(node.annotation), _value_preview(node.value))
                )
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    if target.id == "__all__":
                        continue
                    mod.constants.append((target.id, "", _value_preview(node.value)))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            mod.imports.append(_unparse(node))

    mod.table_keys = _table_keys(tree)

    # Remove constantes duplicadas mantendo a última definição.
    dedup: dict[str, tuple[str, str, str]] = {}
    for name, annotation, value in mod.constants:
        dedup[name] = (name, annotation, value)
    mod.constants = list(dedup.values())
    return mod


def iter_python_modules() -> list[tuple[dict[str, Any], Path]]:
    found: list[tuple[dict[str, Any], Path]] = []
    for pkg in PACKAGES:
        base = PKG_ROOT / pkg["dir"]
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            found.append((pkg, path))
    return found


def render_function(fn: FunctionDoc, mod: ModuleDoc, level: str) -> list[str]:
    out = [f"{level} `{fn.name}()`", ""]
    if fn.decorators:
        out += ["".join(f"`@{d}` " for d in fn.decorators), ""]
    out += ["```python", fn.signature, "```", ""]
    if fn.doc:
        out += [clean_doc(fn.doc), ""]
    out += [
        f"<small>[`{mod.rel_path}:{fn.lineno}`]"
        f"({GITHUB_BLOB}/{mod.rel_path}#L{fn.lineno})</small>",
        "",
    ]
    return out


def render_module_page(mod: ModuleDoc, position: int, is_test: bool) -> list[str]:
    name = mod.rel_path.split("/")[-1]
    title = f"{mod.dotted}"
    lines = front_matter(
        title=title,
        label=name,
        description=summary_of(mod.doc, f"Referência de API do módulo {mod.dotted}."),
        position=position,
    )
    lines += [f"# `{mod.rel_path}`", ""]
    if mod.doc:
        lines += [clean_doc(mod.doc), ""]
    lines += [
        f":::info Fonte",
        f"Módulo `{mod.dotted}` — {mod.loc} linhas · "
        f"{len(mod.classes)} classe(s) · {len(mod.functions)} função(ões) pública(s). "
        f"[Ver no GitHub]({GITHUB_BLOB}/{mod.rel_path})",
        ":::",
        "",
    ]

    if is_test:
        tests = [fn for fn in mod.functions if fn.name.startswith("test_")]
        other = [fn for fn in mod.functions if not fn.name.startswith("test_")]
        if tests:
            lines += ["## Casos de teste", ""]
            lines += table(
                ["Teste", "O que verifica"],
                [
                    (f"`{fn.name}`", summary_of(fn.doc, "—"))
                    for fn in tests
                ],
            )
        for cls in mod.classes:
            lines += [f"## `class {cls.name}`", ""]
            if cls.doc:
                lines += [clean_doc(cls.doc), ""]
            lines += table(
                ["Teste", "O que verifica"],
                [(f"`{m.name}`", summary_of(m.doc, "—")) for m in cls.methods],
            )
        for fn in other:
            lines += render_function(fn, mod, "##")
        return lines

    if mod.constants:
        lines += ["## Constantes e tabelas de módulo", ""]
        lines += table(
            ["Nome", "Anotação", "Valor"],
            [
                (f"`{n}`", f"`{a}`" if a else "—", f"`{v}`" if v else "—")
                for n, a, v in mod.constants
            ],
        )

    if mod.classes:
        lines += ["## Classes", ""]
        for cls in mod.classes:
            bases = f"({', '.join(cls.bases)})" if cls.bases else ""
            lines += [f"### `class {cls.name}{bases}`", ""]
            if cls.doc:
                lines += [clean_doc(cls.doc), ""]
            if cls.attributes:
                lines += table(
                    ["Atributo de classe", "Valor"],
                    [(f"`{n}`", f"`{v}`" if v else "—") for n, v in cls.attributes],
                )
            for method in cls.methods:
                lines += render_function(method, mod, "####")

    if mod.functions:
        lines += ["## Funções", ""]
        for fn in mod.functions:
            lines += render_function(fn, mod, "###")

    if not (mod.constants or mod.classes or mod.functions):
        lines += ["_Este módulo não expõe membros públicos._", ""]

    return lines


# ---------------------------------------------------------------------------
# Parsing do schema SQL
# ---------------------------------------------------------------------------
_CREATE_TABLE_RE = re.compile(
    r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+([a-zA-Z0-9_]+)\s*\((.*?)\)\s*"
    r"(?:PARTITION\s+BY[^;]+)?;",
    re.DOTALL | re.IGNORECASE,
)
_COMMENT_TABLE_RE = re.compile(
    r"COMMENT\s+ON\s+TABLE\s+([a-zA-Z0-9_]+)\s+IS\s+'([^']*)';", re.IGNORECASE
)
_ALTER_FK_RE = re.compile(
    r"ALTER\s+TABLE\s+(?:IF\s+EXISTS\s+)?([a-zA-Z0-9_]+)\s+ADD\s+CONSTRAINT\s+"
    r"[a-zA-Z0-9_]+\s+FOREIGN\s+KEY\s*\(([a-zA-Z0-9_]+)\)\s+REFERENCES\s+"
    r"([a-zA-Z0-9_]+)\s*\(([a-zA-Z0-9_]+)\)",
    re.IGNORECASE,
)
_ENUM_RE = re.compile(
    r"CREATE\s+TYPE\s+([a-zA-Z0-9_]+)\s+AS\s+ENUM\s*\((.*?)\)\s*;", re.DOTALL | re.IGNORECASE
)
_FUNCTION_RE = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+([a-zA-Z0-9_]+)\s*\(", re.IGNORECASE
)
_VIEW_RE = re.compile(
    r"CREATE\s+(?:OR\s+REPLACE\s+)?(MATERIALIZED\s+)?VIEW\s+(?:IF\s+NOT\s+EXISTS\s+)?"
    r"([a-zA-Z0-9_]+)",
    re.IGNORECASE,
)
_TRIGGER_RE = re.compile(r"CREATE\s+TRIGGER\s+([a-zA-Z0-9_]+)", re.IGNORECASE)
_INDEX_RE = re.compile(
    r"CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:CONCURRENTLY\s+)?(?:IF\s+NOT\s+EXISTS\s+)?"
    r"([a-zA-Z0-9_]+)\s+ON\s+([a-zA-Z0-9_]+)",
    re.IGNORECASE,
)


def _table_declarations(body: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for token in re.findall(r"'(?:''|[^'])*'|--[^\n]*|[(),]|[^'(),-]+|-", body):
        if token.startswith("--"):
            continue
        if token == "," and depth == 0:
            parts.append(" ".join("".join(current).split()))
            current = []
            continue
        if token == "(":
            depth += 1
        elif token == ")":
            depth -= 1
        current.append(token)
    if current:
        parts.append(" ".join("".join(current).split()))
    return parts


def parse_sql_file(path: Path) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
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
        constraints: list[str] = []

        for line in _table_declarations(body):
            if not line or line.startswith("--"):
                continue
            upper = line.upper()
            if upper.startswith(("PRIMARY KEY", "CONSTRAINT", "UNIQUE", "CHECK", "FOREIGN KEY")):
                constraints.append(line)
                continue
            parts = line.split(maxsplit=1)
            if len(parts) < 2:
                continue
            col_name = parts[0]
            declaration = re.split(
                r"\s+(?=(?:CONSTRAINT|PRIMARY\s+KEY|NOT\s+NULL|NULL|UNIQUE|CHECK|"
                r"REFERENCES|DEFAULT|COLLATE|GENERATED)\b)",
                parts[1],
                maxsplit=1,
                flags=re.IGNORECASE,
            )
            col_type = declaration[0]
            rest = declaration[1] if len(declaration) > 1 else ""
            is_pk = "PRIMARY KEY" in upper
            not_null = "NOT NULL" in upper or is_pk
            fk_match = re.search(
                r"REFERENCES\s+([a-zA-Z0-9_]+)\s*\(([a-zA-Z0-9_]+)\)", rest, re.IGNORECASE
            )
            fk_target = ""
            if fk_match:
                fk_target = f"{fk_match.group(1)}.{fk_match.group(2)}"
                fks.append((col_name, fk_match.group(1), fk_match.group(2)))
            check = re.search(r"CHECK\s*\((.*)\)", rest, re.IGNORECASE)
            default = re.search(r"DEFAULT\s+([^\s].*?)(?:$|\s+(?:NOT|CHECK|REFERENCES))", rest, re.IGNORECASE)
            cols.append(
                {
                    "name": col_name,
                    "type": col_type,
                    "nullable": "não" if not_null else "sim",
                    "fk": fk_target,
                    "default": default.group(1).strip() if default else "",
                    "check": f"CHECK ({check.group(1)})" if check else ("PK" if is_pk else ""),
                }
            )

        by_name = {c["name"]: c for c in cols}
        for constraint in constraints:
            clause = re.sub(r"^CONSTRAINT\s+\w+\s+", "", constraint, flags=re.IGNORECASE)
            pk = re.match(r"PRIMARY\s+KEY\s*\(([^)]+)\)", clause, re.IGNORECASE)
            fk = re.match(
                r"FOREIGN\s+KEY\s*\(([^)]+)\)\s+REFERENCES\s+(\w+)\s*\(([^)]+)\)",
                clause,
                re.IGNORECASE,
            )
            if pk:
                for raw in pk.group(1).split(","):
                    col = by_name.get(raw.strip())
                    if col:
                        col["nullable"] = "não"
                        col["check"] = "; ".join(filter(None, ["PK", col["check"]]))
            elif fk:
                for raw, ref_col in zip(fk.group(1).split(","), fk.group(3).split(",")):
                    fks.append((raw.strip(), fk.group(2), ref_col.strip()))
        for col_name, ref_tbl, ref_col in fks:
            if col_name in by_name:
                by_name[col_name]["fk"] = f"{ref_tbl}.{ref_col}"

        tables.append(
            {
                "name": tname,
                "comment": comments.get(tname, ""),
                "columns": cols,
                "fks": fks,
                "constraints": constraints,
            }
        )

    enums = [
        (m.group(1), [v.strip().strip("'") for v in m.group(2).split(",")])
        for m in _ENUM_RE.finditer(content)
    ]
    return {
        "file": path.name,
        "slug": path.stem,
        "loc": len(content.splitlines()),
        "tables": tables,
        "enums": enums,
        "functions": sorted({m.group(1) for m in _FUNCTION_RE.finditer(content)}),
        "views": sorted({m.group(2) for m in _VIEW_RE.finditer(content)}),
        "triggers": sorted({m.group(1) for m in _TRIGGER_RE.finditer(content)}),
        "indexes": [(m.group(1), m.group(2)) for m in _INDEX_RE.finditer(content)],
    }


DOMAIN_TITLES = {
    "00_hub": "Hub central",
    "01_identidade": "Identidade e biometria",
    "02_genealogia": "Genealogia e herança",
    "03_saude": "Saúde",
    "04_educacao": "Educação",
    "05_carreira": "Carreira e trabalho",
    "06_financas": "Finanças e patrimônio",
    "07_residencia": "Residência e endereços",
    "08_relacionamentos": "Relacionamentos e família",
    "09_rede_social": "Rede social e convivência",
    "10_vida_digital": "Vida digital",
    "11_juridico": "Jurídico e criminal",
    "12_eleitoral": "Eleitoral e política",
    "13_viagens": "Viagens e mobilidade",
    "14_pets": "Pets e animais",
    "15_consumo": "Consumo e varejo",
    "16_timeline": "Linha do tempo",
    "17_comportamento": "Comportamento e personalidade",
    "18_religiao": "Religião e crenças",
    "19_esporte": "Esporte, hobbies e coleções",
    "20_militar": "Serviço militar",
    "21_imigracao": "Imigração e documentos internacionais",
    "22_comunicacao": "Comunicação",
    "23_midia": "Mídia e reputação",
    "24_meta": "Metadados, auditoria e proveniência",
    "25_juncoes": "Tabelas de junção N:N",
    "26_metadata": "Versionamento do schema",
    "98_indexes": "Índices, partições e estatísticas",
    "99_functions": "Funções, triggers e views",
}


def render_schema_pages(
    domains: list[dict[str, Any]], table_to_generators: dict[str, list[str]]
) -> None:
    target = DOCS / "schema"
    category(
        target,
        "Schema PostgreSQL",
        1,
        "Catálogo das tabelas, colunas, chaves e constraints geradas a partir dos DDL.",
        slug="/schema-dominios",
    )

    total_tables = sum(len(d["tables"]) for d in domains)
    total_cols = sum(len(t["columns"]) for d in domains for t in d["tables"])
    total_fks = sum(len(t["fks"]) for d in domains for t in d["tables"])

    index = front_matter(
        "Schema relacional",
        "Visão geral",
        "Catálogo completo das tabelas PostgreSQL do PersonaDB geradas a partir dos arquivos DDL.",
        0,
    )
    index += [
        "# Schema relacional do PersonaDB",
        "",
        "Catálogo extraído automaticamente dos arquivos DDL em "
        f"[`persona_db/sql/schema/`]({GITHUB_BLOB}/persona_db/sql/schema): "
        f"**{len(domains)} arquivos de domínio**, **{total_tables} tabelas**, "
        f"**{total_cols} colunas** e **{total_fks} chaves estrangeiras**.",
        "",
        "Toda tabela satélite referencia `pessoa.id` por `pessoa_id` (salvo catálogos "
        "compartilhados, como `hospital` ou `empresa`) e as tabelas de junção usam chave "
        "primária composta.",
        "",
        "## Domínios",
        "",
    ]
    index += table(
        ["Arquivo", "Domínio", "Tabelas", "Gerador responsável"],
        [
            (
                f"[`{d['file']}`](./{d['slug']}.md)",
                DOMAIN_TITLES.get(d["slug"], d["slug"]),
                str(len(d["tables"])),
                ", ".join(
                    sorted(
                        {
                            g
                            for t in d["tables"]
                            for g in table_to_generators.get(t["name"], [])
                        }
                    )
                )
                or "—",
            )
            for d in domains
        ],
    )

    all_tables = sorted(
        ((t["name"], d["slug"]) for d in domains for t in d["tables"]),
    )
    index += [
        "## Índice alfabético de tabelas",
        "",
    ]
    index += table(
        ["Tabela", "Domínio"],
        [(f"[`{name}`](./{slug}.md#{name})", slug) for name, slug in all_tables],
    )
    write(target / "index.md", index)

    for position, dom in enumerate(domains, start=1):
        slug = dom["slug"]
        title = DOMAIN_TITLES.get(slug, slug)
        lines = front_matter(
            f"{slug} — {title}",
            f"{slug}",
            f"Tabelas do domínio {title} ({dom['file']}).",
            position,
        )
        lines += [
            f"# `{dom['file']}` — {title}",
            "",
            f"{len(dom['tables'])} tabela(s) · {dom['loc']} linhas de DDL · "
            f"[ver arquivo]({GITHUB_BLOB}/persona_db/sql/schema/{dom['file']})",
            "",
        ]

        generators = sorted(
            {g for t in dom["tables"] for g in table_to_generators.get(t["name"], [])}
        )
        if generators:
            lines += [
                ":::tip Geradores que populam este domínio",
                ", ".join(f"`{g}`" for g in generators),
                ":::",
                "",
            ]

        if dom["enums"]:
            lines += ["## Tipos ENUM", ""]
            lines += table(
                ["Tipo", "Valores"],
                [(f"`{n}`", ", ".join(f"`{v}`" for v in vals)) for n, vals in dom["enums"]],
            )

        edges = sorted(
            {
                (ref_tbl, t["name"], col)
                for t in dom["tables"]
                for col, ref_tbl, _ in t["fks"]
                if ref_tbl != t["name"]
            }
        )
        if edges:
            lines += ["## Diagrama ER", "", "```mermaid", "erDiagram"]
            for ref_tbl, tname, col in edges:
                lines.append(f'    {ref_tbl} ||--o{{ {tname} : "{col}"')
            lines += ["```", ""]

        if dom["functions"] or dom["views"] or dom["triggers"]:
            lines += ["## Objetos de banco", ""]
            if dom["functions"]:
                lines += table(["Função"], [(f"`{f}()`",) for f in dom["functions"]])
            if dom["views"]:
                lines += table(["View"], [(f"`{v}`",) for v in dom["views"]])
            if dom["triggers"]:
                lines += table(["Trigger"], [(f"`{t}`",) for t in dom["triggers"]])

        if dom["indexes"]:
            lines += ["## Índices declarados", ""]
            lines += table(
                ["Índice", "Tabela"], [(f"`{n}`", f"`{t}`") for n, t in dom["indexes"]]
            )

        if dom["tables"]:
            lines += ["## Tabelas", ""]
        for tbl in dom["tables"]:
            lines += [f"### `{tbl['name']}`", ""]
            if tbl["comment"]:
                lines += [f"> {md_escape(tbl['comment'])}", ""]
            gens = table_to_generators.get(tbl["name"], [])
            if gens:
                lines += [
                    "Gerada por: " + ", ".join(f"`{g}`" for g in sorted(gens)) + ".",
                    "",
                ]
            lines += table(
                ["Coluna", "Tipo", "Nulo?", "FK", "Default", "Constraints"],
                [
                    (
                        f"`{c['name']}`",
                        f"`{c['type']}`",
                        c["nullable"],
                        f"`{c['fk']}`" if c["fk"] else "—",
                        f"`{c['default']}`" if c["default"] else "—",
                        md_escape(c["check"]) or "—",
                    )
                    for c in tbl["columns"]
                ],
            )
            if tbl["constraints"]:
                lines += ["<details>", "<summary>Constraints de tabela</summary>", ""]
                lines += ["```sql"] + [c for c in tbl["constraints"]] + ["```", ""]
                lines += ["</details>", ""]

        write(target / f"{slug}.md", lines)


# ---------------------------------------------------------------------------
# Páginas derivadas: catálogo de geradores e catálogo de regras
# ---------------------------------------------------------------------------
def render_generator_catalog(
    modules: dict[str, ModuleDoc], known_tables: set[str], pipeline_order: list[str]
) -> dict[str, list[str]]:
    """Escreve `docs/geradores/catalogo.md` e devolve o mapa tabela → geradores."""
    table_to_generators: dict[str, list[str]] = {}
    rows: list[tuple[str, ...]] = []
    details: list[str] = []

    gen_modules = {
        name: mod
        for name, mod in modules.items()
        if name.startswith("persona_db.generators.gen_")
    }

    def order_key(dotted: str) -> tuple[int, str]:
        short = dotted.split(".")[-1]
        prefix = short[4:6]
        try:
            idx = pipeline_order.index(short)
        except ValueError:
            idx = 99
        return (idx, prefix)

    for dotted in sorted(gen_modules, key=order_key):
        mod = gen_modules[dotted]
        short = dotted.split(".")[-1]
        tables = sorted(mod.table_keys & known_tables)
        for tname in tables:
            table_to_generators.setdefault(tname, []).append(short)
        pipeline_pos = (
            str(pipeline_order.index(short) + 1) if short in pipeline_order else "—"
        )
        rows.append(
            (
                f"[`{short}`](#{short})",
                pipeline_pos,
                str(len(tables)),
                summary_of(mod.doc, "—"),
            )
        )
        details += [
            f"## `{short}`",
            "",
            clean_doc(mod.doc) or "_Sem docstring de módulo._",
            "",
            f"- **Arquivo:** [`{mod.rel_path}`]({GITHUB_BLOB}/{mod.rel_path}) "
            f"({mod.loc} linhas)",
            f"- **Posição no pipeline:** {pipeline_pos}",
            f"- **Referência de API:** [`{short}`](../referencia-api/generators/{short}.md)",
            "",
        ]
        if tables:
            details += [
                "**Tabelas populadas** (detectadas cruzando literais do módulo com o DDL):",
                "",
                " ".join(f"`{t}`" for t in tables),
                "",
            ]

    lines = front_matter(
        "Catálogo dos geradores",
        "Catálogo",
        "Lista dos 24 geradores de domínio, sua posição no pipeline e as tabelas que populam.",
        3,
    )
    lines += [
        "# Catálogo dos geradores de domínio",
        "",
        f"O PersonaDB possui **{len(gen_modules)} geradores** executados em ordem "
        "topológica por `persona_db.scripts.generate.DOMAIN_PIPELINE`. A tabela abaixo é "
        "derivada do código-fonte a cada build da documentação.",
        "",
    ]
    lines += table(["Gerador", "Ordem", "Tabelas", "Resumo"], rows)
    lines += details
    write(DOCS / "geradores" / "catalogo.md", lines)
    return table_to_generators


_RULE_RE = re.compile(r'"rule":\s*"([a-z0-9_]+)"')
_DOMAIN_RE = re.compile(r'"domain":\s*"([a-z0-9_]+)"')


def render_rules_catalog(known_tables: set[str]) -> int:
    validators_dir = PKG_ROOT / "validators"
    rows: list[tuple[str, ...]] = []
    total = 0
    for path in sorted(validators_dir.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        module = path.stem
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            segment = ast.get_source_segment(source, node) or ""
            rules = sorted(set(_RULE_RE.findall(segment)))
            if not rules:
                continue
            domains = sorted(set(_DOMAIN_RE.findall(segment))) or ["—"]
            for rule in rules:
                total += 1
                rows.append(
                    (
                        f"`{rule}`",
                        ", ".join(domains),
                        f"`{module}.{node.name}`",
                        summary_of(ast.get_docstring(node), "—"),
                    )
                )

    lines = front_matter(
        "Catálogo de regras de validação",
        "Catálogo de regras",
        "Todas as regras de consistência verificadas pelos validadores do PersonaDB.",
        3,
    )
    lines += [
        "# Catálogo de regras de validação",
        "",
        f"As **{total} regras** abaixo são extraídas estaticamente dos módulos em "
        f"[`persona_db/validators/`]({GITHUB_BLOB}/persona_db/validators). Cada violação "
        "encontrada vira uma linha em `validacao_consistencia` e entra no relatório HTML.",
        "",
    ]
    lines += table(["Regra", "Domínio", "Função", "Verificação"], sorted(rows))
    write(DOCS / "validadores" / "regras.md", lines)
    return total


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------
def pipeline_order_from_source() -> list[str]:
    source = (PKG_ROOT / "scripts" / "generate.py").read_text(encoding="utf-8")
    block = re.search(r"DOMAIN_PIPELINE[^=]*=\s*\((.*?)\n\)", source, re.DOTALL)
    if not block:
        return []
    return re.findall(r"gen_\d\d_[a-z_]+", block.group(1))


def main() -> int:
    modules: dict[str, ModuleDoc] = {}
    api_root = DOCS / "referencia-api"

    # Diretórios totalmente derivados: limpos a cada execução para não deixar
    # páginas órfãs quando um módulo ou arquivo DDL é removido.
    for stale in (api_root, DOCS / "schema"):
        shutil.rmtree(stale, ignore_errors=True)

    # 1) Schema SQL ---------------------------------------------------------
    sql_dir = PKG_ROOT / "sql" / "schema"
    domains = [parse_sql_file(p) for p in sorted(sql_dir.glob("*.sql"))]
    known_tables = {t["name"] for d in domains for t in d["tables"]}

    # 2) Módulos Python -----------------------------------------------------
    per_package: dict[str, list[ModuleDoc]] = {}
    for pkg, path in iter_python_modules():
        mod = parse_module(path)
        modules[mod.dotted] = mod
        per_package.setdefault(pkg["dir"], []).append(mod)

    for pkg in PACKAGES:
        mods = per_package.get(pkg["dir"], [])
        if not mods:
            continue
        pkg_dir = api_root / pkg["dir"]
        category(
            pkg_dir,
            pkg["label"],
            pkg["position"],
            pkg["description"],
            slug=f"/referencia-api/{pkg['dir']}",
        )
        for position, mod in enumerate(sorted(mods, key=lambda m: m.rel_path), start=1):
            page = render_module_page(mod, position, is_test=bool(pkg.get("tests")))
            sub = Path(mod.rel_path).parent.relative_to(f"persona_db/{pkg['dir']}")
            write(pkg_dir / sub / f"{doc_stem(mod.rel_path)}.md", page)

    # 3) Catálogos derivados ------------------------------------------------
    pipeline = pipeline_order_from_source()
    table_to_generators = render_generator_catalog(modules, known_tables, pipeline)
    rule_count = render_rules_catalog(known_tables)
    render_schema_pages(domains, table_to_generators)

    # 4) Índice da referência de API ---------------------------------------
    total_loc = sum(m.loc for m in modules.values())
    index = front_matter(
        "Referência de API",
        "Visão geral",
        "Índice de todos os módulos Python do PersonaDB documentados automaticamente.",
        0,
    )
    index += [
        "# Referência de API",
        "",
        f"Documentação extraída por análise estática (`ast`) de **{len(modules)} módulos "
        f"Python** ({total_loc} linhas) do pacote `persona_db`. Assinaturas, docstrings e "
        "links para o código-fonte são regenerados a cada build.",
        "",
        ":::note Como regenerar",
        "```bash\ncd website && npm run gen:docs\n```",
        ":::",
        "",
        "## Pacotes",
        "",
    ]
    index += table(
        ["Pacote", "Módulos", "Linhas", "Descrição"],
        [
            (
                f"`persona_db/{pkg['dir']}/`",
                str(len(per_package.get(pkg["dir"], []))),
                str(sum(m.loc for m in per_package.get(pkg["dir"], []))),
                pkg["description"],
            )
            for pkg in PACKAGES
            if per_package.get(pkg["dir"])
        ],
    )
    index += ["## Todos os módulos", ""]
    index += table(
        ["Módulo", "Resumo"],
        [
            (
                f"[`{m.dotted}`](./{Path(m.rel_path).parent.relative_to('persona_db').as_posix()}"
                f"/{doc_stem(m.rel_path)}.md)",
                summary_of(m.doc, "—"),
            )
            for m in sorted(modules.values(), key=lambda m: m.rel_path)
        ],
    )
    write(api_root / "index.md", index)

    # 5) Estatísticas para a página inicial --------------------------------
    stats = {
        "tables": len(known_tables),
        "domains": len([d for d in domains if d["tables"]]),
        "sqlFiles": len(domains),
        "sqlLines": sum(d["loc"] for d in domains),
        "generators": len([m for m in modules if ".generators.gen_" in m]),
        "engines": len(
            [
                m
                for m in modules
                if m.startswith("persona_db.engines.")
                and m.rsplit(".", 1)[-1] not in {"__init__", "constants", "root"}
            ]
        ),
        "validators": len([m for m in modules if ".validators.val_" in m]),
        "rules": rule_count,
        "pythonModules": len(modules),
        "pythonLines": total_loc,
        "columns": sum(len(t["columns"]) for d in domains for t in d["tables"]),
        "foreignKeys": sum(len(t["fks"]) for d in domains for t in d["tables"]),
        "tests": sum(
            1
            for m in modules.values()
            if "/tests/" in m.rel_path
            for fn in m.functions
            if fn.name.startswith("test_")
        ),
    }
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(
        f"[gen:docs] {len(modules)} módulos Python, {len(known_tables)} tabelas, "
        f"{rule_count} regras de validação documentadas."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
