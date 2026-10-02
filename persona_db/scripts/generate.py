"""Orchestrator CLI para geração determinística em lote do PersonaDB (TASK-040 / TASK-080).

Executa os geradores de domínio na ordem topológica de dependências:
  gen_00_pessoa -> gen_02_genealogia -> gen_01_identidade -> gen_03_saude
  -> gen_18_religiao -> gen_04_educacao -> gen_20_militar -> gen_05_carreira
  -> gen_06_financas -> gen_07_residencia -> gen_11_juridico -> gen_08_relacionamentos
  -> gen_09_rede_social -> gen_12_eleitoral -> gen_13_viagens -> gen_21_imigracao
  -> gen_10_digital -> gen_14_pets -> gen_15_consumo -> gen_17_comportamento
  -> gen_19_esporte -> gen_22_comunicacao -> gen_23_midia -> gen_16_timeline
  -> junções (Domínio 25) -> metadados e validação (Domínio 24).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import date
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from persona_db.generators import (
    gen_00_pessoa,
    gen_01_identidade,
    gen_02_genealogia,
    gen_03_saude,
    gen_04_educacao,
    gen_05_carreira,
    gen_06_financas,
    gen_07_residencia,
    gen_08_relacionamentos,
    gen_09_rede_social,
    gen_10_digital,
    gen_11_juridico,
    gen_12_eleitoral,
    gen_13_viagens,
    gen_14_pets,
    gen_15_consumo,
    gen_16_timeline,
    gen_17_comportamento,
    gen_18_religiao,
    gen_19_esporte,
    gen_20_militar,
    gen_21_imigracao,
    gen_22_comunicacao,
    gen_23_midia,
)
from persona_db.validators.run_validators import (
    build_validation_table_rows,
    render_html_report,
    validate_dataset,
)

# ---------------------------------------------------------------------------
# Ordem topológica de execução dos geradores de domínio (TASK-040)
# ---------------------------------------------------------------------------
DOMAIN_PIPELINE: tuple[tuple[str, Any], ...] = (
    ("02_genealogia", gen_02_genealogia),
    ("01_identidade", gen_01_identidade),
    ("03_saude", gen_03_saude),
    ("18_religiao", gen_18_religiao),
    ("04_educacao", gen_04_educacao),
    ("20_militar", gen_20_militar),
    ("05_carreira", gen_05_carreira),
    ("06_financas", gen_06_financas),
    ("07_residencia", gen_07_residencia),
    ("11_juridico", gen_11_juridico),
    ("08_relacionamentos", gen_08_relacionamentos),
    ("09_rede_social", gen_09_rede_social),
    ("12_eleitoral", gen_12_eleitoral),
    ("13_viagens", gen_13_viagens),
    ("21_imigracao", gen_21_imigracao),
    ("10_digital", gen_10_digital),
    ("14_pets", gen_14_pets),
    ("15_consumo", gen_15_consumo),
    ("17_comportamento", gen_17_comportamento),
    ("19_esporte", gen_19_esporte),
    ("22_comunicacao", gen_22_comunicacao),
    ("23_midia", gen_23_midia),
    ("16_timeline", gen_16_timeline),
)


def _merge_tables(
    target: dict[str, list[dict[str, Any]]],
    source: dict[str, list[dict[str, Any]]],
) -> None:
    for table_name, rows in source.items():
        if table_name not in target:
            target[table_name] = list(rows)
        else:
            target[table_name].extend(rows)


def _build_junction_tables(
    dataset: dict[str, list[dict[str, Any]]],
    today: date,
) -> dict[str, list[dict[str, Any]]]:
    """Deriva determinísticamente as tabelas de junção N:N (Domínio 25)."""
    junc: dict[str, list[dict[str, Any]]] = {
        "pessoa_habilidade": [],
        "pessoa_idioma_nivel": [],
        "pessoa_hobby": [],
        "pessoa_grupo_social": [],
        "pessoa_evento": [],
        "pessoa_doenca_familiar": [],
        "pessoa_pet": [],
        "pessoa_veiculo": [],
        "pessoa_imovel": [],
        "pessoa_eleicao": [],
        "pessoa_viagem_companheiro": [],
        "pessoa_empresa_socio": [],
        "pessoa_religiao_historico": [],
        "pessoa_documento_historico": [],
    }

    for hab in dataset.get("habilidade", []):
        if hab.get("pessoa_id") and hab.get("id"):
            junc["pessoa_habilidade"].append({
                "pessoa_id": hab["pessoa_id"],
                "habilidade_id": hab["id"],
                "nivel": hab.get("nivel", "intermediario"),
            })

    for idm in dataset.get("pessoa_idioma", []):
        if idm.get("pessoa_id") and idm.get("id"):
            junc["pessoa_idioma_nivel"].append({
                "pessoa_id": idm["pessoa_id"],
                "idioma_id": idm["id"],
                "nivel_leitura": idm.get("nivel_fluencia", "intermediario"),
                "nivel_fala": idm.get("nivel_fluencia", "intermediario"),
            })

    for hb in dataset.get("hobby", []):
        if hb.get("pessoa_id") and hb.get("id"):
            junc["pessoa_hobby"].append({
                "pessoa_id": hb["pessoa_id"],
                "hobby_id": hb["id"],
                "desde_quando": today.isoformat(),
            })

    seen_pgs: set[tuple[str, str]] = set()
    for mg in dataset.get("membro_grupo_social", []):
        pair = (mg.get("pessoa_id"), mg.get("grupo_id"))
        if pair[0] and pair[1] and pair not in seen_pgs:
            seen_pgs.add(pair)
            junc["pessoa_grupo_social"].append({
                "pessoa_id": pair[0],
                "grupo_id": pair[1],
                "papel": mg.get("papel", "membro"),
            })

    seen_pev: set[tuple[str, str]] = set()
    for ev in dataset.get("participacao_evento_social", []):
        pair = (ev.get("pessoa_id"), ev.get("evento_id"))
        if pair[0] and pair[1] and pair not in seen_pev:
            seen_pev.add(pair)
            junc["pessoa_evento"].append({
                "pessoa_id": pair[0],
                "evento_id": pair[1],
                "papel": ev.get("papel", "convidado"),
            })

    seen_pdf: set[tuple[str, str]] = set()
    for pg in dataset.get("predisposicao_genetica", []):
        pair = (pg.get("pessoa_id"), pg.get("condicao_id"))
        if pair[0] and pair[1] and pair not in seen_pdf:
            seen_pdf.add(pair)
            junc["pessoa_doenca_familiar"].append({
                "pessoa_id": pair[0],
                "condicao_genetica_id": pair[1],
                "grau_risco": round(min(1.0, max(0.0, float(pg.get("grau_predisposicao") or 0.25))), 2),
            })

    for pt in dataset.get("pet", []):
        if pt.get("pessoa_id_dono") and pt.get("id"):
            junc["pessoa_pet"].append({
                "pessoa_id": pt["pessoa_id_dono"],
                "pet_id": pt["id"],
                "tipo_vinculo": "dono",
            })

    for v in dataset.get("veiculo", []):
        prop_id = v.get("proprietario_pessoa_id") or v.get("pessoa_id_proprietario") or v.get("pessoa_id")
        if prop_id and v.get("id"):
            junc["pessoa_veiculo"].append({
                "pessoa_id": prop_id,
                "veiculo_id": v["id"],
                "tipo_posse": "proprietario",
            })

    for im in dataset.get("imovel", []):
        prop_id = im.get("proprietario_pessoa_id") or im.get("pessoa_id_proprietario") or im.get("pessoa_id")
        if prop_id and im.get("id"):
            junc["pessoa_imovel"].append({
                "pessoa_id": prop_id,
                "imovel_id": im["id"],
                "tipo_posse": "proprietario",
            })

    seen_pel: set[tuple[str, str]] = set()
    for ce in dataset.get("comparecimento_eleitoral", []):
        pair = (ce.get("pessoa_id"), ce.get("eleicao_id"))
        if pair[0] and pair[1] and pair not in seen_pel:
            seen_pel.add(pair)
            junc["pessoa_eleicao"].append({
                "pessoa_id": pair[0],
                "eleicao_id": pair[1],
                "participou": bool(ce.get("compareceu", True)),
            })

    seen_pvc: set[tuple[str, str]] = set()
    for cv in dataset.get("companhia_viagem", []):
        pair = (cv.get("pessoa_id_acompanhante"), cv.get("viagem_id"))
        if pair[0] and pair[1] and pair not in seen_pvc:
            seen_pvc.add(pair)
            junc["pessoa_viagem_companheiro"].append({
                "pessoa_id": pair[0],
                "viagem_id": pair[1],
                "papel": cv.get("relacao", "acompanhante"),
            })

    seen_pes: set[tuple[str, str]] = set()
    for ct in dataset.get("contrato_trabalho", []):
        if ct.get("tipo_contrato") == "PJ":
            pair = (ct.get("pessoa_id"), ct.get("empresa_id"))
            if pair[0] and pair[1] and pair not in seen_pes:
                seen_pes.add(pair)
                junc["pessoa_empresa_socio"].append({
                    "pessoa_id": pair[0],
                    "empresa_id": pair[1],
                    "percentual_participacao": 25.0,
                })

    seen_prh: set[tuple[str, str, str]] = set()
    for cr in dataset.get("conversao_religiosa", []):
        key = (cr.get("pessoa_id"), cr.get("crenca_nova_id"), cr.get("data"))
        if key[0] and key[1] and key[2] and key not in seen_prh:
            seen_prh.add(key)
            junc["pessoa_religiao_historico"].append({
                "pessoa_id": key[0],
                "crenca_id": key[1],
                "data_inicio": key[2],
                "data_fim": None,
            })
    if not junc["pessoa_religiao_historico"] and dataset.get("crenca") and dataset.get("pessoa"):
        c0 = dataset["crenca"][0]["id"]
        p0 = dataset["pessoa"][0]
        junc["pessoa_religiao_historico"].append({
            "pessoa_id": p0["id"],
            "crenca_id": c0,
            "data_inicio": p0["data_nascimento"],
            "data_fim": None,
        })

    for doc in dataset.get("pessoa_documento", []):
        if doc.get("pessoa_id") and doc.get("id"):
            junc["pessoa_documento_historico"].append({
                "pessoa_id": doc["pessoa_id"],
                "documento_id": doc["id"],
                "data_emissao": doc.get("data_emissao"),
                "data_expiracao": doc.get("validade"),
            })

    return junc


def generate_all(
    n: int = 100,
    seed: int = 7,
    today: date | None = None,
    domains: set[str] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Executa todos os geradores de domínio e retorna o dataset em memória."""
    today = today or gen_00_pessoa.simulation_today()
    ts_iso = f"{today.isoformat()}T00:00:00+00:00"

    personas = gen_00_pessoa.generate(n=n, seed=seed, today=today)
    dataset: dict[str, list[dict[str, Any]]] = {}

    for dom_name, mod in DOMAIN_PIPELINE:
        if domains is not None and dom_name not in domains:
            continue
        if dom_name in ("07_residencia", "11_juridico", "13_viagens", "16_timeline"):
            part = mod.generate(
                personas,
                seed=seed,
                today=today,
                existing_tables=dataset,
            )
        else:
            part = mod.generate(personas, seed=seed, today=today)
        _merge_tables(dataset, part)

    # Projeção final da tabela central `pessoa` (após enriquecimento pelos domínios)
    dataset["pessoa"] = [gen_00_pessoa.as_pessoa_row(p) for p in personas]

    if domains is None or "25_juncoes" in domains:
        _merge_tables(dataset, _build_junction_tables(dataset, today))

    # Tabelas de metadados e auditoria (Domínio 24 e 26)
    first_pid = dataset["pessoa"][0]["id"] if dataset["pessoa"] else None
    dataset["versao_registro"] = [
        {
            "id": str(uuid5(NAMESPACE_URL, f"versao-reg-{seed}-{n}")),
            "tabela": "pessoa",
            "registro_id": first_pid,
            "numero_versao": 1,
            "data": ts_iso,
        }
    ]
    dataset["log_alteracao"] = [
        {
            "id": str(uuid5(NAMESPACE_URL, f"logalt-{seed}-{n}")),
            "tabela": "pessoa",
            "registro_id": first_pid,
            "campo_alterado": "estado_civil",
            "valor_antigo": "solteiro",
            "valor_novo": dataset["pessoa"][0]["estado_civil"] if dataset["pessoa"] else "solteiro",
            "data": ts_iso,
        }
    ]
    dataset["auditoria"] = [
        {
            "id": str(uuid5(NAMESPACE_URL, f"audit-{seed}-{n}-{today.isoformat()}")),
            "usuario_sistema": "personadb_orchestrator",
            "acao": f"generate_all(n={n}, seed={seed})",
            "tabela_afetada": "ALL",
            "data": ts_iso,
        }
    ]
    dataset["regra_geracao"] = [
        {
            "id": str(uuid5(NAMESPACE_URL, f"regra-{dom_name}")),
            "dominio": dom_name,
            "parametro": "pipeline_order",
            "valor_padrao": str(idx + 1),
        }
        for idx, (dom_name, _) in enumerate(DOMAIN_PIPELINE)
    ]
    dataset["fonte_dado"] = [
        {
            "id": str(uuid5(NAMESPACE_URL, f"fonte-{tbl}")),
            "tabela_origem": tbl,
            "metodo_geracao": "deterministic_pcg64_generator",
            "data_geracao": ts_iso,
        }
        for tbl in sorted(dataset.keys())
    ]

    val_rows = build_validation_table_rows(dataset, today=today)
    dataset["validacao_consistencia"] = val_rows

    digest = hashlib.sha256(
        json.dumps(
            {k: len(v) for k, v in sorted(dataset.items())},
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()[:32]
    dataset["exportacao_dataset"] = [
        {
            "id": str(uuid5(NAMESPACE_URL, f"exp-{seed}-{n}-{today.isoformat()}")),
            "data": ts_iso,
            "formato": "in_memory_dict",
            "tabelas_incluidas": str(len(dataset)),
            "destino": f"sha256:{digest}",
        }
    ]
    dataset["schema_version"] = [
        {
            "id": str(uuid5(NAMESPACE_URL, "schema-version-1.0.0")),
            "versao": "1.0.0",
            "descricao": "PersonaDB schema inicial (25 domínios + controle)",
            "data_aplicacao": ts_iso,
        }
    ]

    return dataset


generate_dataset = generate_all


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada CLI do orquestrador de geração."""
    parser = argparse.ArgumentParser(description="Generate synthetic PersonaDB dataset.")
    parser.add_argument(
        "--personas",
        "--people",
        dest="personas",
        type=int,
        default=100,
        help="Number of personas to generate.",
    )
    parser.add_argument("--seed", type=int, default=7, help="Master RNG seed.")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size for generation progress.")
    parser.add_argument(
        "--domains",
        type=str,
        default=None,
        help="Comma-separated list of domain prefixes to run (default: all 25 domains).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not persist; print counts and exit.")
    parser.add_argument("--validate", action="store_true", default=True, help="Run consistency validators.")
    parser.add_argument("--no-validate", dest="validate", action="store_false")
    parser.add_argument(
        "--json-out",
        "--output",
        dest="json_out",
        type=str,
        default=None,
        help="Optional file path to dump dataset JSON.",
    )
    parser.add_argument("--html-report", type=str, default=None, help="Optional HTML validation report output path.")
    args = parser.parse_args(argv)

    selected_domains = (
        {d.strip() for d in args.domains.split(",") if d.strip()}
        if args.domains
        else None
    )

    t0 = time.perf_counter()
    dataset = generate_all(n=args.personas, seed=args.seed, domains=selected_domains)
    elapsed = time.perf_counter() - t0

    summary: dict[str, Any] = {
        "personas": args.personas,
        "seed": args.seed,
        "batch_size": args.batch_size,
        "elapsed_seconds": round(elapsed, 4),
        "tables": {k: len(v) for k, v in dataset.items()},
        "total_rows": sum(len(v) for v in dataset.values()),
    }

    if args.validate:
        report = validate_dataset(dataset)
        summary["validation"] = {
            "passed": report["passed"],
            "violation_count": report["violation_count"],
            "overall_consistency_pct": report["overall_consistency_pct"],
            "domain_consistency": report["domain_consistency"],
        }
        if args.html_report:
            render_html_report(report, args.html_report)
        if not report["passed"]:
            summary["violations_sample"] = report["violations"][:10]
            print(json.dumps(summary, default=str, ensure_ascii=False))
            return 1

    if args.json_out and not args.dry_run:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(dataset, fh, default=str, ensure_ascii=False)

    print(json.dumps(summary, default=str, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
