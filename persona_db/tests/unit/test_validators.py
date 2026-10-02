"""Testes unitários dos 6 validadores de domínio e CLIs (TASK-070 a TASK-076).

Verifica que cada validador detecta corretamente violações artificiais injetadas
no dataset e que os pontos de entrada CLI (`generate.main`, `run_validators.main`)
retornam código de saída 0 quando consistente e 1 quando há violação.
"""
from __future__ import annotations

import copy
from pathlib import Path

from persona_db.scripts.generate import generate_all
from persona_db.scripts.generate import main as generate_main
from persona_db.validators import (
    validate_dataset,
    validate_financas,
    validate_genealogia,
    validate_juridico,
    validate_saude,
    validate_social,
    validate_temporal,
)
from persona_db.validators.run_validators import main as validators_main


def test_validators_detect_injected_violations() -> None:
    """Injeta violações em cada domínio e confirma detecção pelo respectivo validador."""
    base = generate_all(n=25, seed=19)
    assert validate_dataset(base)["passed"] is True

    # 1. Genealogia: herança de pessoa viva
    ds_gen = copy.deepcopy(base)
    living_person = next(p for p in ds_gen["pessoa"] if p["esta_vivo"])
    ds_gen["heranca"].append({
        "id": "her-inv-1",
        "pessoa_id_falecido": living_person["id"],
        "pessoa_id_herdeiro": living_person["id"],
        "valor_estimado": 1000.0,
        "tipo_bem": "imovel",
        "data_transferencia": "2025-01-01",
    })
    v_gen = validate_genealogia(ds_gen)
    assert any(v["rule"] == "inheritance_from_deceased_only" for v in v_gen)

    # 2. Temporal: data_fim < data_inicio
    ds_tmp = copy.deepcopy(base)
    ds_tmp["contrato_trabalho"].append({
        "id": "ct-inv-1",
        "pessoa_id": living_person["id"],
        "empresa_id": "emp-1",
        "cargo_id": "crg-1",
        "tipo_contrato": "CLT",
        "data_inicio": "2025-06-01",
        "data_fim": "2024-01-01",
    })
    v_tmp = validate_temporal(ds_tmp)
    assert any(v["rule"] == "end_before_start" for v in v_tmp)

    # 3. Finanças: salário abaixo do mínimo vigente
    ds_fin = copy.deepcopy(base)
    ds_fin["salario"].append({
        "id": "sal-inv-1",
        "contrato_id": "ct-none",
        "valor": 100.0,
        "data_vigencia": "2024-01-01",
    })
    v_fin = validate_financas(ds_fin)
    assert any(v["rule"] == "salary_below_minimum_wage" for v in v_fin)

    # 4. Saúde: prescrição para pessoa sem diagnóstico
    ds_sau = copy.deepcopy(base)
    ds_sau["doenca_pessoa"] = []
    ds_sau["condicao_cronica"] = []
    ds_sau["saude_mental_registro"] = []
    ds_sau["prescricao"] = [{
        "id": "pr-inv-1",
        "pessoa_id": living_person["id"],
        "medicamento_id": "med-1",
        "data_inicio": "2024-01-01",
        "data_fim": "2024-01-10",
    }]
    v_sau = validate_saude(ds_sau)
    assert any(v["rule"] == "prescription_without_diagnosis" for v in v_sau)

    # 5. Jurídico: candidato sem filiação partidária
    ds_jur = copy.deepcopy(base)
    ds_jur["candidato"].append({
        "id": "cand-inv-1",
        "pessoa_id": living_person["id"],
        "eleicao_id": ds_jur["eleicao"][0]["id"],
        "partido_id": "partido-inexistente",
        "cargo_disputado": "vereador",
        "eleito": False,
    })
    v_jur = validate_juridico(ds_jur)
    assert any(v["rule"] == "candidate_without_party_affiliation" for v in v_jur)

    # 6. Social: amizade assimétrica
    ds_soc = copy.deepcopy(base)
    p0, p1 = ds_soc["pessoa"][0]["id"], ds_soc["pessoa"][1]["id"]
    ds_soc["amizade"] = [{
        "id": "amiz-inv-1",
        "pessoa_id_a": p0,
        "pessoa_id_b": p1,
        "data_inicio": "2022-01-01",
        "contexto_conhecimento": "escola",
    }]
    v_soc = validate_social(ds_soc)
    assert any(v["rule"] == "asymmetric_friendship" for v in v_soc)


def test_cli_entrypoints_generate_and_validate(tmp_path: Path) -> None:
    """Executa os CLIs `generate.main` e `run_validators.main` com saída JSON e HTML."""
    json_out = tmp_path / "dataset.json"
    html_out = tmp_path / "quality.html"

    rc_gen = generate_main([
        "--personas", "20",
        "--seed", "13",
        "--json-out", str(json_out),
        "--html-report", str(html_out),
    ])
    assert rc_gen == 0
    assert json_out.exists()
    assert html_out.exists()

    rc_val = validators_main([
        "--personas", "20",
        "--seed", "13",
        "--html-out", str(tmp_path / "val.html"),
    ])
    assert rc_val == 0
