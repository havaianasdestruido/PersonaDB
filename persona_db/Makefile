PYTHON ?= python
PYTHONPATH := ..$(if $(PYTHONPATH),:$(PYTHONPATH))
DATABASE_URL ?= postgresql://persona:persona@localhost:5432/personadb
SCHEMA := $(sort $(wildcard sql/schema/*.sql))

.PHONY: setup migrate generate validate benchmark reset test
setup:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m pip install -e '.[dev]'
migrate:
	@for file in $(SCHEMA); do echo "Applying $$file"; psql "$(DATABASE_URL)" -v ON_ERROR_STOP=1 -f "$$file"; done
generate:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m persona_db.scripts.generate --people $${N_PESSOAS:-10000} --seed $${SEED:-7} --output dataset.json
validate:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m persona_db.scripts.generate --people 100 --seed $${SEED:-7} --output /tmp/personadb-validation.json
benchmark:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m persona_db.scripts.benchmark --people $${N_PESSOAS:-1000} --seed $${SEED:-7}
reset:
	psql "$(DATABASE_URL)" -v ON_ERROR_STOP=1 -c 'DROP SCHEMA public CASCADE; CREATE SCHEMA public;'
test:
	PYTHONPATH="$(PYTHONPATH)" $(PYTHON) -m pytest
