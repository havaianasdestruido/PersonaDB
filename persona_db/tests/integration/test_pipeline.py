from persona_db.scripts.generate import generate_dataset
from persona_db.validators import validate_dataset


def test_pipeline_is_deterministic_and_consistent():
    first = generate_dataset(25, seed=314)
    second = generate_dataset(25, seed=314)
    assert first == second
    assert len(first["pessoa"]) == 25
    assert validate_dataset(first)["critical_violations"] == 0
