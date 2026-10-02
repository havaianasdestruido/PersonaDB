"""Regression coverage for generator, validator and schema review findings."""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import date
from uuid import NAMESPACE_URL, uuid5

import pytest
from persona_db.engines.genetics import GeneticEngine
from persona_db.engines.rng import SeededRNG
from persona_db.generators import gen_00_pessoa, gen_08_relacionamentos
from persona_db.generators.gen_01_identidade import _make_cpf
from persona_db.generators.gen_11_juridico import _terminate_overlapping_contracts
from persona_db.scripts.document_schema import _parse_sql_file, render_from_sql_dir
from persona_db.scripts.generate import _build_junction_tables
from persona_db.validators.run_validators import build_validation_table_rows, validate_dataset
from persona_db.validators.val_juridico import validate_juridico
from persona_db.validators.val_temporal import validate_temporal


def test_height_corrects_father_for_daughters(monkeypatch):
    monkeypatch.setattr(SeededRNG, "normal", lambda *args: 0.0)
    engine = GeneticEngine(SeededRNG(7))
    assert engine.expected_child_height(190, 160, "F") == 167.7
    assert engine.expected_child_height(190, 160, "M") == 181.4


def test_cpf_unique_across_thousand_boundary_and_valid_checksums():
    cpfs = [_make_cpf(f"person-{i}", i) for i in range(3000)]
    assert len(set(cpfs)) == 3000
    assert _make_cpf("a", 999999)[:9] == "000999999"
    assert _make_cpf("b", 1000000) == _make_cpf("a", 0)
    for cpf in cpfs:
        assert cpf.startswith("000") and len(cpf) == 11
        for length in (9, 10):
            remainder = sum(int(cpf[i]) * (length + 1 - i) for i in range(length)) % 11
            assert int(cpf[length]) == (0 if remainder < 2 else 11 - remainder)


def test_ceps_stable_across_processes():
    script = '''
import json
from persona_db.generators.gen_00_pessoa import generate_personas
from persona_db.generators.gen_07_residencia import generate
print(json.dumps(generate(generate_personas(5, seed=91), seed=91)["endereco"], sort_keys=True))
'''
    outputs = [subprocess.check_output(
        [sys.executable, "-c", script], env={**os.environ, "PYTHONHASHSEED": seed}, text=True,
    ) for seed in ("1", "2")]
    assert outputs[0] == outputs[1]


@pytest.mark.parametrize("m_parents,f_parents", [
    ({"pai_id": "dad"}, {"pai_id": "dad"}),
    ({"mae_id": "mom"}, {"mae_id": "mom"}),
    ({"pai_id": "parent"}, {"mae_id": "parent"}),
    ({}, {"pai_id": "m"}), ({}, {"mae_id": "m"}),
    ({"pai_id": "f"}, {}), ({"mae_id": "f"}, {}),
    ({}, {}),
])
def test_marriage_excludes_relatives_but_allows_unknown_parents(monkeypatch, m_parents, f_parents):
    people = gen_00_pessoa.generate_personas(2, seed=7)
    for p, pid, sex in zip(people, ("m", "f"), ("masculino", "feminino")):
        p.update(id=pid, sexo=sex, data_nascimento="1970-01-01", data_obito=None,
                 pai_id=None, mae_id=None)
    people[0].update(m_parents)
    people[1].update(f_parents)
    monkeypatch.setattr(gen_08_relacionamentos.FamilyEngine, "first_marriage_age", lambda *a: 20)
    marriages = gen_08_relacionamentos.generate(people, today=date(2026, 1, 1))["casamento"]
    assert bool(marriages) == (not m_parents and not f_parents)


def test_contract_cleanup_cascades_and_updates_current_job():
    person = {"id": "p", "salario_mensal": 9999, "empresa_atual_id": "old"}
    contracts = [
        {"id": "short", "pessoa_id": "p", "empresa_id": "old",
         "data_inicio": "2010-01-01", "data_fim": None},
        {"id": "drop", "pessoa_id": "p", "empresa_id": "prison",
         "data_inicio": "2021-01-01", "data_fim": "2022-01-01"},
        {"id": "later", "pessoa_id": "p", "empresa_id": "new",
         "data_inicio": "2023-01-01", "data_fim": None},
        {"id": "other", "pessoa_id": "q", "empresa_id": "other",
         "data_inicio": "2010-01-01", "data_fim": None},
    ]
    data = {"contrato_trabalho": contracts, "pessoa": [person], "salario": [
        {"contrato_id": c["id"], "valor": 2000, "data_vigencia": c["data_inicio"]}
        for c in contracts
    ]}
    for table in ("beneficio", "demissao", "holerite", "ferias"):
        data[table] = [{"contrato_id": "drop"}]
    data["ferias"].append({"contrato_id": "short", "data_inicio": "2019-12-20",
                           "data_fim": "2020-01-10", "dias": 21})
    data["holerite"].append({"contrato_id": "short", "mes_referencia": "2025-01-01"})
    for table, prefix in (("historico_emprego", "histemp"), ("licenca_trabalho", "lic"),
                          ("promocao", "promo"), ("avaliacao_desempenho", "aval")):
        data[table] = [{"id": str(uuid5(NAMESPACE_URL, f"{prefix}-{cid}")),
                        "inicio": "2010-01-01", "fim": "2025-01-01"}
                       for cid in ("short", "drop")]
    _terminate_overlapping_contracts("p", date(2020, 1, 1), date(2022, 12, 31), data,
                                     today=date(2025, 1, 1))
    assert {c["id"] for c in data["contrato_trabalho"]} == {"short", "later", "other"}
    assert contracts[0]["data_fim"] == "2019-12-31"
    assert contracts[3]["data_fim"] is None
    assert not any(r.get("contrato_id") == "drop" for rows in data.values() for r in rows)
    assert data["ferias"][0]["dias"] == 11
    assert data["holerite"][0]["mes_referencia"] == "2019-12-01"
    assert data["demissao"][0]["data"] == "2019-12-31"
    assert data["demissao"][0]["contrato_id"] == "short"
    for table in ("historico_emprego", "licenca_trabalho", "promocao", "avaliacao_desempenho"):
        assert len(data[table]) == 1
        assert data[table][0]["fim"] == "2019-12-31"
    assert person["empresa_atual_id"] == "new" and not person["desempregado"]
    assert person["salario_mensal"] == 2000 and person["renda_anual"] == 26600
    _terminate_overlapping_contracts("p", date(2024, 1, 1), date(2026, 1, 1), data,
                                     today=date(2025, 1, 1))
    assert person["empresa_atual_id"] is None and person["desempregado"]
    assert person["salario_mensal"] == person["renda_anual"] == 0
    _terminate_overlapping_contracts("p", date(2024, 1, 1), date(2026, 1, 1), data,
                                     today=date(2025, 1, 1))
    assert len(data["demissao"]) == 2


def test_schema_parser_preserves_types_and_table_constraints(tmp_path):
    path = tmp_path / "00_test.sql"
    path.write_text('''CREATE TABLE IF NOT EXISTS child (
        a UUID, b UUID, amount NUMERIC(10, 2) DEFAULT 0,
        measured DOUBLE PRECISION NOT NULL,
        moment TIMESTAMP(3) WITH TIME ZONE,
        label CHARACTER VARYING(50) DEFAULT 'a,b',
        CONSTRAINT child_pk PRIMARY KEY (a, b),
        CONSTRAINT child_fk FOREIGN KEY (a, b) REFERENCES parent (x, y),
        CHECK (
            amount >= 0 AND measured > amount
        )
    );''')
    table = _parse_sql_file(path)["tables"][0]
    cols = {c["name"]: c for c in table["columns"]}
    assert len(cols) == 6
    assert cols["amount"]["type"] == "NUMERIC(10, 2)"
    assert cols["measured"]["type"] == "DOUBLE PRECISION"
    assert cols["moment"]["type"] == "TIMESTAMP(3) WITH TIME ZONE"
    assert cols["label"]["type"] == "CHARACTER VARYING(50)"
    for key in ("a", "b"):
        assert cols[key]["nullable"] == "NO" and "PK" in cols[key]["constraints"]
    assert cols["b"]["fk"] == "`parent(y)`"
    assert "CHECK" in cols["amount"]["constraints"]
    rendered = render_from_sql_dir(tmp_path)
    assert 'parent ||--o{ child : "a"' in rendered
    assert 'parent ||--o{ child : "b"' in rendered
    assert "child_pk PRIMARY KEY (a, b)" in rendered
    assert "NUMERIC(10, 2)" in rendered


def test_junctions_use_generator_fields_and_preserve_process_links():
    data = {"pessoa_idioma": [{"id": "lang", "pessoa_id": "p", "nivel_fluencia": "nativo"}],
            "pessoa_documento": [{"id": "doc", "pessoa_id": "p", "validade": "2030-01-01"}],
            "pessoa_processo": [{"pessoa_id": "p", "processo_id": "proc", "papel": "reu"}],
            "processo": [{"id": "proc", "pessoa_id_reu": "p"}]}
    junctions = _build_junction_tables(data, date(2026, 1, 1))
    assert junctions["pessoa_idioma_nivel"][0]["nivel_fala"] == "nativo"
    assert junctions["pessoa_idioma_nivel"][0]["nivel_leitura"] == "nativo"
    assert junctions["pessoa_documento_historico"][0]["data_expiracao"] == "2030-01-01"
    assert "pessoa_processo" not in junctions


def test_validation_defaults_to_simulation_date_and_preserves_explicit_date(monkeypatch):
    monkeypatch.setenv("PERSONADB_TODAY", "2030-01-01")
    data = {"pessoa": [{"id": "p", "data_nascimento": "2029-01-01"}]}
    assert validate_dataset(data)["passed"]
    assert not validate_dataset(data, today=date(2028, 1, 1))["passed"]
    assert build_validation_table_rows(data)[0]["data"].startswith("2030-01-01")
    assert build_validation_table_rows(data, today=date(2028, 1, 1))[0]["data"].startswith("2028-01-01")


def test_legal_checks_use_election_year_defendant_links_and_sentence_months():
    data = {
        "pessoa": [{"id": "minor", "data_nascimento": "2010-01-01"}],
        "eleicao": [{"id": "e", "ano": 2024}],
        "voto": [{"pessoa_id": "minor", "eleicao_id": "e"}],
        "processo": [{"id": "pr", "tipo": "criminal_furto"}],
        "pessoa_processo": [{"processo_id": "pr", "pessoa_id": "p", "papel": "reu"},
                            {"processo_id": "pr", "pessoa_id": "witness", "papel": "testemunha"}],
        "julgamento": [{"id": "j", "processo_id": "pr", "data": "2020-01-01"}],
        "sentenca": [{"id": "s", "julgamento_id": "j"}],
        "pena": [{"id": "pn", "sentenca_id": "s", "tipo": "prisao", "duracao_ou_valor": "24 meses"}],
        "contrato_trabalho": [
            {"id": "overlap", "pessoa_id": "p", "data_inicio": "2021-12-21", "data_fim": None},
            {"id": "after", "pessoa_id": "p", "data_inicio": "2021-12-22", "data_fim": None},
            {"id": "witness", "pessoa_id": "witness", "data_inicio": "2020-01-01"},
        ],
    }
    violations = validate_juridico(data)
    assert any(v["rule"] == "voter_under_16" for v in violations)
    assert [v["contrato_id"] for v in violations if v["rule"] == "active_employment_during_imprisonment"] == ["overlap"]
    data["eleicao"][0]["data"] = "2028-01-01"
    assert not any(v["rule"] == "voter_under_16" for v in validate_juridico(data))


def test_temporal_checks_use_generated_process_and_passport_fields():
    data = {
        "pessoa": [{"id": "p", "data_nascimento": "2010-01-01"}],
        "processo": [{"id": "pr", "tipo": "criminal_furto"}],
        "pessoa_processo": [{"processo_id": "pr", "pessoa_id": "p", "papel": "reu"}],
        "julgamento": [{"id": "j", "processo_id": "pr", "data": "2025-01-01"}],
        "pessoa_documento": [{"pessoa_id": "p", "tipo": "passaporte", "validade": "2025-01-02"}],
        "destino": [{"id": "d", "pais_ficticio": "Portugal"}],
        "viagem": [{"id": "v", "pessoa_id": "p", "destino_id": "d", "data_volta": "2025-01-03"}],
    }
    assert {v["rule"] for v in validate_temporal(data)} == {
        "criminal_process_under_18", "international_trip_without_valid_passport",
    }
    data["pessoa_documento"][0]["validade"] = "2025-01-03"
    data["julgamento"][0]["data"] = "2030-01-01"
    assert validate_temporal(data) == []
    data["pessoa_documento"] = []
    data["destino"][0] = {"id": "d", "pais": "Portugal"}
    assert validate_temporal(data)[0]["rule"] == "international_trip_without_valid_passport"
    data["destino"][0]["pais_ficticio"] = "Brasil"
    assert validate_temporal(data) == []
    data["destino"][0]["pais_ficticio"] = "Brasil Fictício"
    assert validate_temporal(data) == []
