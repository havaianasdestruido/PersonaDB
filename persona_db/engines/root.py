"""Root bootstrap shared by trainers and generators.

Ownership: COORDINATOR ONLY. Agents may read and import, never edit.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERSONA_DB_ROOT = os.path.join(PROJECT_ROOT, "persona_db")

for _p in (PERSONA_DB_ROOT, os.path.join(PERSONA_DB_ROOT, "engines")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def mtime_of(root: str) -> float:
    latest = 0.0
    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            p = os.path.join(dirpath, name)
            try:
                latest = max(latest, os.path.getmtime(p))
            except OSError:
                continue
    return latest


def hash_path(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_agent_status() -> dict:
    p = os.path.join(PROJECT_ROOT, "_coordination", "agent_status.json")
    if not os.path.exists(p):
        return {"agents": {}}
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def agent_done(agent_id: str) -> bool:
    return load_agent_status().get("agents", {}).get(agent_id, {}).get("status") == "success"