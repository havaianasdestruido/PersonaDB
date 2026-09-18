"""Coordinator-owned helper for agents to record completion status."""
from __future__ import annotations

import json
import os
import sys

STATUS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "agent_status.json"
)


def mark_done(
    agent_id: str,
    files: list[str] | None = None,
    extra: dict | None = None,
) -> None:
    with open(STATUS_PATH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    data.setdefault("agents", {})[agent_id] = {
        "status": "success",
        "files": files or [],
        "extra": extra or {},
    }
    with open(STATUS_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def mark_failed(agent_id: str, reason: str) -> None:
    with open(STATUS_PATH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    data.setdefault("agents", {})[agent_id] = {"status": "failed", "reason": reason}
    with open(STATUS_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def requires_success(agent_ids: list[str]) -> bool:
    with open(STATUS_PATH, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    agents = data.get("agents", {})
    return all(agents.get(a, {}).get("status") == "success" for a in agent_ids)


if __name__ == "__main__":
    sys.exit(0)