import json
import tarfile

from persona_db.scripts.export import export_csv, export_people


def test_csv_archive_and_person_aggregation(tmp_path):
    data = {"pessoa": [{"id": "p1", "nome": "Ana"}], "pessoa_idade": [{"pessoa_id": "p1", "idade": 20}]}
    archive = tmp_path / "data.tar.gz"
    export_csv(data, archive)
    with tarfile.open(archive) as tar:
        assert set(tar.getnames()) == {"pessoa.csv", "pessoa_idade.csv"}
        assert b"Ana" in tar.extractfile("pessoa.csv").read()
    out = tmp_path / "people"
    export_people(data, out)
    payload = json.loads((out / "p1.json").read_text())
    assert payload["pessoa"]["nome"] == "Ana"
    assert payload["pessoa_idade"][0]["idade"] == 20
