# Coordination File Sync Protocol

## Rule 1 — Exclusive writers
Each agent writes ONLY files listed in its ownership map (defined in AGENT_BRIEFS.md).
Any file not owned by an agent is READ-ONLY for that agent.

## Rule 2 — Shared trusted modules
The following files are created ONCE by the coordinator and must NEVER be edited by any agent:
- `_coordination/AGENT_BRIEFS.md`
- `_coordination/agent_status.json`
- `persona_db/engines/root.py` (RNG bootstrap + constants anchor)
- `persona_db/engines/constants.py`
- `persona_db/seeds/__init__.py` (version metadata only)
Agents may import/extend via mechanisms owned by them, but they may not rewrite these files.

## Rule 3 — Dependencies
An agent may only start when every dependency file exists and `agent_status.json` marks the
upstream agent as `"status": "success"`.

## Rule 4 — Sync markers
After finishing, each agent appends its own entry to `_coordination/agent_status.json`
(a single `"agents"` object, keyed by numeric id) using a small helper owned by the coordinator.

## Rule 5 — Failure recovery
If an agent reports failure, the coordinator marks its status `"failed"` and re-runs that agent
alone. Downstream agents that depend on it must wait for a new `"success"` entry.