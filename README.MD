# PersonaDB

PersonaDB creates deterministic **fictional** Brazilian-style persona datasets.
It combines a PostgreSQL schema with probability engines and generators for the
implemented hub, identity, genealogy, and health domains. No generated record
represents a real person.

## Quick start

```bash
cp persona_db/.env.example .env
set -a
. ./.env
set +a
python -m pip install -e './persona_db[dev]'
make -C persona_db generate
make -C persona_db validate
make -C persona_db benchmark
python -m pytest persona_db/tests
```

Use `docker compose -f persona_db/docker-compose.yml up -d` to start PostgreSQL, then `make -C persona_db migrate` to apply the
ordered schema files. `make -C persona_db generate`, `make -C persona_db validate`,
and `make -C persona_db benchmark` provide repeatable local workflows.
The shell commands above load and export `.env`; reload it after editing.
`DATABASE_URL` configures migrations, `SEED` sets the generation seed,
`N_PESSOAS` sets the population for generate and benchmark (validate uses 100),
and `PERSONADB_TODAY` sets the simulation date. Generate and validate also pass
that date to validation. Make does not load `.env` automatically.

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
