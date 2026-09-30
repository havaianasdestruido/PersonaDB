"""val_social — validador de consistência social e relacional (TASK-075).

Regras verificadas:
- Nenhum casamento ativo simultaneamente com outro casamento ativo da mesma pessoa.
- Filhos (`filho`) com pai e mãe biológicos distintos e no máximo um registro por `pessoa_id_filho`.
- Ausência de auto-referência (`pessoa_id_a != pessoa_id_b`) em `relacionamento`,
  `casamento`, `uniao_estavel`, `amizade` e `inimizade_ficticia`.
- Guarda compartilhada (`guarda_compartilhada`) referenciando registro existente em `filho`.
- Pensão alimentícia (`pensao_alimenticia`) referenciando relação parental válida.
- Simetria estrita de `amizade`: se A é amigo de B, B é amigo de A.
"""
from __future__ import annotations

from datetime import date
from typing import Any

Violation = dict[str, Any]


def validate_social(
    dataset: dict[str, list[dict[str, Any]]],
    today: date | None = None,
) -> list[Violation]:
    """Executa todas as verificações de consistência social e relacional."""
    violations: list[Violation] = []
    people = {p["id"]: p for p in dataset.get("pessoa", []) if "id" in p}
    divorced_marriages = {d.get("casamento_id") for d in dataset.get("divorcio", []) if d.get("casamento_id")}

    # 1. Casamentos ativos simultâneos
    active_marriages_count: dict[str, int] = {}
    for cas in dataset.get("casamento", []):
        cid = cas.get("id")
        if cid in divorced_marriages:
            continue
        pa = cas.get("pessoa_id_a")
        pb = cas.get("pessoa_id_b")
        for pid in (pa, pb):
            if pid:
                active_marriages_count[pid] = active_marriages_count.get(pid, 0) + 1
                if active_marriages_count[pid] > 1:
                    violations.append({
                        "domain": "social",
                        "rule": "simultaneous_active_marriages",
                        "person_id": pid,
                    })

    # 2. Ausência de auto-referência em tabelas relacionais
    for tbl in ("relacionamento", "casamento", "uniao_estavel", "amizade", "inimizade_ficticia"):
        for row in dataset.get(tbl, []):
            pa = row.get("pessoa_id_a")
            pb = row.get("pessoa_id_b")
            if pa and pb and pa == pb:
                violations.append({
                    "domain": "social",
                    "rule": "self_reference_relationship",
                    "table": tbl,
                    "person_id": pa,
                })

    # 3. Filhos: pais distintos e unicidade por filho
    seen_filho_persons: set[str] = set()
    filho_ids: set[str] = set()
    parent_pairs: set[tuple[str, str]] = set()
    for p in people.values():
        if p.get("pai_id"):
            parent_pairs.add((p["pai_id"], p["id"]))
        if p.get("mae_id"):
            parent_pairs.add((p["mae_id"], p["id"]))

    for f in dataset.get("filho", []):
        fid = f.get("id")
        if fid:
            filho_ids.add(fid)
        pf = f.get("pessoa_id_filho")
        pp = f.get("pessoa_id_pai")
        pm = f.get("pessoa_id_mae")
        if pp and pf:
            parent_pairs.add((pp, pf))
        if pm and pf:
            parent_pairs.add((pm, pf))
        if pp and pm and pp == pm:
            violations.append({
                "domain": "social",
                "rule": "identical_parents_on_child",
                "filho_id": fid,
            })
        if pf in seen_filho_persons:
            violations.append({
                "domain": "social",
                "rule": "duplicate_child_record",
                "person_id": pf,
            })
        if pf:
            seen_filho_persons.add(pf)

    # 4. Guarda compartilhada refere a filho existente
    for gc in dataset.get("guarda_compartilhada", []):
        if gc.get("filho_id") not in filho_ids:
            violations.append({
                "domain": "social",
                "rule": "custody_without_child_record",
                "guarda_id": gc.get("id"),
                "filho_id": gc.get("filho_id"),
            })

    # 5. Pensão alimentícia refere a relação parental válida
    for pa in dataset.get("pensao_alimenticia", []):
        pag = pa.get("pessoa_id_pagador")
        ben = pa.get("pessoa_id_beneficiario")
        if (pag, ben) not in parent_pairs:
            violations.append({
                "domain": "social",
                "rule": "alimony_without_parental_link",
                "pensao_id": pa.get("id"),
                "pagador_id": pag,
                "beneficiario_id": ben,
            })

    # 6. Amizade simétrica (se (A, B) em amizade, então (B, A) em amizade)
    friend_edges = {
        (a.get("pessoa_id_a"), a.get("pessoa_id_b"))
        for a in dataset.get("amizade", [])
        if a.get("pessoa_id_a") and a.get("pessoa_id_b")
    }
    for pa, pb in friend_edges:
        if (pb, pa) not in friend_edges:
            violations.append({
                "domain": "social",
                "rule": "asymmetric_friendship",
                "pessoa_id_a": pa,
                "pessoa_id_b": pb,
            })

    return violations
