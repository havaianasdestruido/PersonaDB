"""Teste de integração completo do pipeline de 25 domínios (TASK-094).

Verifica:
- Geração de `N = 200` personas completas em memória com todos os 25 domínios.
- Execução de todos os 6 validadores de consistência (`val_genealogia`,
  `val_temporal`, `val_financas`, `val_saude`, `val_juridico`, `val_social`)
  sem nenhuma violação crítica.
- Cobertura de todas as tabelas do modelo relacional (~246 tabelas).
- Determinismo estrito: rodar com `seed = 42` duas vezes produz exatamente os
  mesmos IDs e valores.
"""
from __future__ import annotations

from pathlib import Path

from persona_db.scripts.generate import generate_all
from persona_db.validators import (
    render_html_report,
    validate_dataset,
    validate_financas,
    validate_genealogia,
    validate_juridico,
    validate_saude,
    validate_social,
    validate_temporal,
)

# Eventos muito raros que podem ter 0 ocorrências em N=200
_RARE_EVENT_TABLES = {
    "deportacao_ficticia",
    "doacao_familiar",
    "uniao_estavel",
    "adocao_ficticia",
    "entrevista_ficticia",
}


def test_full_25_domain_generation_and_validators(tmp_path: Path) -> None:
    """Gera N = 200 personas em todos os 25 domínios e valida 0 violações críticas."""
    dataset = generate_all(n=200, seed=42)

    assert len(dataset["pessoa"]) == 200
    assert len(dataset) >= 240

    # Todos os 6 validadores de domínio retornam 0 violações
    assert validate_genealogia(dataset) == []
    assert validate_temporal(dataset) == []
    assert validate_financas(dataset) == []
    assert validate_saude(dataset) == []
    assert validate_juridico(dataset) == []
    assert validate_social(dataset) == []

    report = validate_dataset(dataset)
    assert report["passed"] is True
    assert report["violation_count"] == 0
    assert report["critical_violations"] == 0
    assert report["overall_consistency_pct"] == 100.0

    # Verifica que todas as tabelas esperadas possuem registros (exceto eventos raros)
    empty_non_rare = [
        tbl
        for tbl, rows in dataset.items()
        if len(rows) == 0 and tbl not in _RARE_EVENT_TABLES
    ]
    assert empty_non_rare == []

    # Verifica geração de relatório HTML
    html_file = render_html_report(report, tmp_path / "report.html")
    assert html_file.exists()
    assert "APROVADO (0 violações)" in html_file.read_text(encoding="utf-8")


def test_determinism_seed_42_twice() -> None:
    """Executar a geração completa duas vezes com seed=42 produz datasets idênticos."""
    run_1 = generate_all(n=60, seed=42)
    run_2 = generate_all(n=60, seed=42)
    assert run_1 == run_2
