# AGENT_BRIEFS — Ownership Map & Sync

Protocol: each agent exclusively writes its owned files and treats every other file as read-only.
Dependencies must show `"status": "success"` in `_coordination/agent_status.json`.
After finishing, agents append their status entry using `_coordination/status.py`.

## Agent 1 — Infrastructure (completed by coordinator)
- Own: root dotfiles, `persona_db/pyproject.toml`, `persona_db/docker-compose.yml`,
  `persona_db/Makefile`, `persona_db/.env.example`, `_coordination/**`.
- Depends: none.

## Agent 2 — Base engines (RNG + Socio + Health)
- Own: `persona_db/engines/rng.py`, `persona_db/engines/socio.py`,
  `persona_db/engines/health.py`, `persona_db/tests/unit/test_base_engines.py`.
- Read: `engines/root.py`, `engines/constants.py`.
- Depends: agent1.

## Agent 3 — Genetics + Family + Geography
- Own: `persona_db/engines/genetics.py`, `persona_db/engines/family.py`,
  `persona_db/engines/geography.py`, `persona_db/tests/unit/test_genetics_family_geo.py`.
- Read: `engines/rng.py` (agent2), constants.
- Depends: agent1; import rng from agent2 (stub allowed until agent2 writes it).

## Agent 4 — Criminal engine
- Own: `persona_db/engines/criminal.py`, `persona_db/tests/unit/test_criminal.py`.
- Read: `engines/rng.py`, `engines/constants.py`.
- Depends: agent1; may import only rng.

## Agent 5 — Seeds
- Own: `persona_db/seeds/lookup_data.py`, `persona_db/seeds/probability_tables.py`,
  `persona_db/data/seed/**`.
- Read: `engines/constants.py`.
- Depends: agent1. Generates files only; does NOT write database.

## Agent 6 — DDL domains 00-03
- Own: `persona_db/sql/schema/{00_hub,01_identidade,02_genealogia,03_saude}.sql`.
- Depends: agent1.

## Agent 7 — DDL domains 04-06
- Own: `persona_db/sql/schema/{04_educacao,05_carreira,06_financas}.sql`.
- Depends: agent1.

## Agent 8 — DDL domains 07-25 + meta
- Own: `persona_db/sql/schema/07_residencia.sql` .. `persona_db/sql/schema/25_juncoes.sql`,
  `persona_db/sql/schema/26_metadata.sql`.
- Depends: agent1.

## Agent 9 — SQL functions, views, indexes
- Own: `persona_db/sql/schema/99_functions.sql`, `persona_db/sql/schema/98_indexes.sql`.
- Read: all DDL files.
- Depends: agents 6,7,8 (files present).

## Agent 10 — Core generators (pessoa, genealogia, identidade)
- Own: `persona_db/generators/gen_00_pessoa.py`, `persona_db/generators/gen_02_genealogia.py`,
  `persona_db/generators/gen_01_identidade.py`.
- Read: engines 2-4, seeds 5, DDL 6-9.
- Depends: agents 2,3,4,5,6,7,8,9.

## Agent 11 — Life domain generators (saude, educacao, carreira, financas)
- Own: `persona_db/generators/gen_03_saude.py`, `gen_04_educacao.py`,
  `gen_05_carreira.py`, `gen_06_financas.py`.
- Depends: agents 2-9 (reads), agent 10 (interface).

## Agent 12 — Related domain generators
- Own: `gen_11_juridico.py`, `gen_07_residencia.py`, `gen_08_relacionamentos.py`,
  `gen_12_eleitoral.py`, `gen_13_viagens.py`, `gen_10_digital.py`.
- Depends: agents 2-10 for base; interface model from agent 11.

## Agent 13 — Remaining domains, timeline, media
- Own: `gen_14_pets.py` .. `gen_23_midia.py`, `gen_16_timeline.py`.
- Depends: agents 2-12 outputs.

## Agent 14 — Orchestrator, insert, validators, tests, docs, CI
- Own: `persona_db/scripts/{generate.py,bulk_insert.py,export.py,benchmark.py}`,
  `persona_db/validators/*`, `persona_db/tests/integration/*`, `persona_db/docs/*`,
  `.github/workflows/ci.yml`, Makefile targets.
- Depends: all agents 2-13.

## Failure recovery
Coordinator re-runs failing agent alone. Downstream agents await new success entry.