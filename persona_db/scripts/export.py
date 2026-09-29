"""Export a generated JSON dataset to portable archive formats.

CSV archives contain one file per table. JSON-person archives contain one
complete record per person (including all rows keyed by pessoa_id).
Parquet support is optional and requires a pandas parquet engine.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import tarfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, list[dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or any(not isinstance(rows, list) for rows in payload.values()):
        raise ValueError("Input must be a JSON object mapping table names to row arrays")
    return payload


def export_csv(dataset: dict[str, list[dict[str, Any]]], target: Path) -> None:
    """Write UTF-8 table CSVs into a compressed tar archive."""
    with tarfile.open(target, "w:gz") as archive:
        for table, rows in sorted(dataset.items()):
            if not rows:
                continue
            columns = sorted({key for row in rows for key in row})
            stream = io.StringIO(newline="")
            writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in row.items()})
            data = stream.getvalue().encode("utf-8")
            info = tarfile.TarInfo(f"{table}.csv")
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))


_SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def _destination(root: Path, component: str, suffix: str) -> Path:
    """Validate a filename component and ensure its resolved path stays in root."""
    if not _SAFE_COMPONENT.fullmatch(component) or component in {".", ".."}:
        raise ValueError(f"Invalid output filename component: {component!r}")
    resolved_root = root.resolve()
    destination = (resolved_root / f"{component}{suffix}").resolve()
    if not destination.is_relative_to(resolved_root):
        raise ValueError(f"Output path escapes destination directory: {component!r}")
    return destination


def export_people(dataset: dict[str, list[dict[str, Any]]], target: Path) -> None:
    """Write one aggregate JSON document per person, replacing stale JSON outputs."""
    people = dataset.get("pessoa", [])
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(dict)
    for table, rows in dataset.items():
        if table.startswith("_") or table == "pessoa":
            continue
        for row in rows:
            person_id = row.get("pessoa_id")
            if person_id is not None:
                grouped[str(person_id)].setdefault(table, []).append(row)
    target.mkdir(parents=True, exist_ok=True)
    root = target.resolve()
    destinations = [(person, _destination(root, str(person.get("id", "")), ".json")) for person in people]
    for stale in root.glob("*.json"):
        stale.unlink()
    for person, destination in destinations:
        pid = str(person.get("id"))
        destination.write_text(json.dumps({"pessoa": person, **grouped.get(pid, {})}, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def export_parquet(dataset: dict[str, list[dict[str, Any]]], target: Path) -> None:
    """Write one parquet file per nonempty table, removing stale parquet outputs."""
    import pandas as pd
    target.mkdir(parents=True, exist_ok=True)
    root = target.resolve()
    destinations = [(table, rows, _destination(root, table, ".parquet")) for table, rows in dataset.items() if rows]
    for stale in root.glob("*.parquet"):
        stale.unlink()
    for table, rows, destination in destinations:
        pd.DataFrame(rows).to_parquet(destination, index=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON dataset created by scripts.generate")
    parser.add_argument("--format", choices=("csv", "people", "parquet"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    dataset = _load(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "csv":
        export_csv(dataset, args.output)
    elif args.format == "people":
        export_people(dataset, args.output)
    else:
        export_parquet(dataset, args.output)
    # Sidecar makes the export self-describing and records provenance.
    meta = {"created_at": datetime.now(timezone.utc).isoformat(), "format": args.format,
            "row_counts": {k: len(v) for k, v in dataset.items()}, "total_rows": sum(map(len, dataset.values()))}
    args.output.with_suffix(args.output.suffix + ".README.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
