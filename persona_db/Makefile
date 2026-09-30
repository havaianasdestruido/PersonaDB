PYTHON ?= python3
PYTHONPATH := ..$(if $(PYTHONPATH),:$(PYTHONPATH))
DATABASE_URL ?= postgresql://persona:persona@localhost:5432/personadb
SCHEMA := $(sort $(wildcard sql/schema/*.sql))

.PHONY: setup migrate generate validate benchmark reset test load export-csv export-parquet docs-schema
setup:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m pip install -e '.[dev,parquet]'
migrate:
	@for file in $(SCHEMA); do echo "Applying $$file"; psql "$(DATABASE_URL)" -v ON_ERROR_STOP=1 -f "$$file"; done
generate:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m persona_db.scripts.generate --people $${N_PESSOAS:-10000} --seed $${SEED:-7} --output dataset.json
validate:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m persona_db.validators.run_validators --personas $${N_PESSOAS:-100} --seed $${SEED:-7}
benchmark:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m persona_db.scripts.benchmark --people $${N_PESSOAS:-1000} --seed $${SEED:-7}
load:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m persona_db.scripts.bulk_insert dataset.json --database-url "$(DATABASE_URL)"
export-csv:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m persona_db.scripts.export dataset.json --format csv --output dataset-csv.tar.gz
export-parquet:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m persona_db.scripts.export dataset.json --format parquet --output dataset-parquet
docs-schema:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m persona_db.scripts.document_schema
reset:
	psql "$(DATABASE_URL)" -v ON_ERROR_STOP=1 -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
test:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m pytest
