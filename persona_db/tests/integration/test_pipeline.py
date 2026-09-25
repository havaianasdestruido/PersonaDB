import sys

import pytest

from persona_db.scripts import generate
from persona_db.scripts.generate import generate_dataset
from persona_db.validators import validate_dataset


def test_pipeline_is_deterministic_and_consistent():
    first = generate_dataset(25, seed=314)
    second = generate_dataset(25, seed=314)
    assert first == second
    assert len(first["pessoa"]) == 25
    assert validate_dataset(first)["critical_violations"] == 0


def test_cli_rejects_future_death_before_writing(monkeypatch, tmp_path):
    dataset = {"pessoa": [{
        "id": 1, "data_nascimento": "2000-01-01", "data_obito": "2030-01-02",
    }]}
    monkeypatch.setattr(generate, "generate_dataset", lambda *args: dataset)
    output = tmp_path / "dataset.json"
    monkeypatch.setattr(sys, "argv", [
        "generate", "--people", "1", "--today", "2030-01-01", "--output", str(output),
    ])
    with pytest.raises(SystemExit, match="1 critical violations"):
        generate.main()
    assert not output.exists()
