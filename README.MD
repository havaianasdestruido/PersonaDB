# PersonaDB

PersonaDB creates deterministic **fictional** Brazilian-style persona datasets.
It combines a PostgreSQL schema with probability engines and generators for the
implemented hub, identity, genealogy, and health domains. No generated record
represents a real person.

## Quick start

```bash
cp persona_db/.env.example .env
python -m pip install -e persona_db
python -m persona_db.scripts.generate --people 100 --seed 7 --output dataset.json
python -m pytest
```

Use `docker compose -f persona_db/docker-compose.yml up -d` to start PostgreSQL, then `make -C persona_db migrate` to apply the
ordered schema files. `make generate`, `make validate`, and `make benchmark`
provide repeatable local workflows. Configuration is read from `.env` by shell
wrappers and uses `DATABASE_URL`, `SEED`, `N_PESSOAS`, and `PERSONADB_TODAY`.

## Architecture

`engines/` contains deterministic stochastic models, `seeds/` holds fictional
reference data, and `generators/` creates table-shaped records in dependency
order. `scripts/generate.py` orchestrates the available pipeline and writes a
portable JSON snapshot. `validators/` checks core birth/death, parentage, date
range, and physical-bound constraints before output is accepted.

## Extending

Add a generator that accepts personas plus a seed, returns `{table: rows}`, and
place it after its dependencies in `generate_dataset`. Add a pure validator and
an integration test alongside it. All randomness must use `SeededRNG` forks.

See [PERSONA.MD](PERSONA.MD) for the target relational model and
[TODO.MD](TODO.MD) for the full planned domain catalogue.
