"""val_genealogia — validador de consistência genealógica e genética (TASK-070).

Regras verificadas:
- Nenhum pai/mãe mais jovem que o filho (margem mínima: 14 anos = 14 * 365 dias).
- Tipo sanguíneo (ABO + Rh) do filho compatível com os pais via Punnett.
- Cor dos olhos biologicamente possível dados os pais (ex.: dois pais de olhos
  azuis não geram filho de olhos castanhos ou verdes).
- Lateralidade com probabilidade não-zero dados os pais.
- Nenhum ciclo direcionado na árvore genealógica (verificado via `networkx`).
- Herança registrada apenas de pessoas marcadas como falecidas (`esta_vivo == False`).
"""
from __future__ import annotations

from datetime import date
from typing import Any

import networkx as nx
from persona_db.engines.genetics import GeneticEngine

Violation = dict[str, Any]

_EYE_GENOTYPES_BY_PHENOTYPE: dict[str, tuple[str, str]] = {
    "castanho": ("B", "b"),
    "ambar": ("B", "g"),
    "verde": ("G", "b"),
    "avela": ("g", "g"),
    "cinza": ("b", "b"),
    "azul": ("b", "b"),
}


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def validate_genealogia(
    dataset: dict[str, list[dict[str, Any]]],
    today: date | None = None,
) -> list[Violation]:
    """Executa todas as verificações de consistência genealógica e genética."""
    violations: list[Violation] = []
    people = {p["id"]: p for p in dataset.get("pessoa", []) if "id" in p}
    traits_by_person = {
        r["pessoa_id"]: r
        for r in dataset.get("pessoa_caracteristica_fisica", [])
        if "pessoa_id" in r
    }

    graph = nx.DiGraph()
    for pid in people:
        graph.add_node(pid)

    for child_id, child in people.items():
        child_born = _date(child.get("data_nascimento"))
        pai_id = child.get("pai_id")
        mae_id = child.get("mae_id")
        pai = people.get(pai_id) if pai_id else None
        mae = people.get(mae_id) if mae_id else None

        # 1. Idade mínima parental (>= 14 * 365 dias) e construção do grafo
        for key, parent in (("pai_id", pai), ("mae_id", mae)):
            if parent is None:
                continue
            par_id = parent["id"]
            if par_id == child_id:
                violations.append({
                    "domain": "genealogia",
                    "rule": "genealogy_no_cycles",
                    "person_id": child_id,
                })
            else:
                graph.add_edge(par_id, child_id)
            par_born = _date(parent.get("data_nascimento"))
            if child_born and par_born and (child_born - par_born).days < 14 * 365:
                violations.append({
                    "domain": "genealogia",
                    "rule": "parent_at_least_14",
                    "person_id": child_id,
                    "parent_id": par_id,
                    "parent_role": key,
                })

        # 2. Compatibilidade genética quando ambos os pais estão presentes no dataset
        if pai is not None and mae is not None:
            c_trait = traits_by_person.get(child_id, child)
            p_trait = traits_by_person.get(pai["id"], pai)
            m_trait = traits_by_person.get(mae["id"], mae)

            c_abo = c_trait.get("tipo_sanguineo") or child.get("tipo_sanguineo")
            c_rh = c_trait.get("fator_rh") or child.get("fator_rh")
            p_abo = p_trait.get("tipo_sanguineo") or pai.get("tipo_sanguineo")
            p_rh = p_trait.get("fator_rh") or pai.get("fator_rh")
            m_abo = m_trait.get("tipo_sanguineo") or mae.get("tipo_sanguineo")
            m_rh = m_trait.get("fator_rh") or mae.get("fator_rh")

            if c_abo and c_rh and p_abo and p_rh and m_abo and m_rh:
                filho_str = f"{c_abo}{'+' if c_rh == 'positivo' else '-'}"
                if not GeneticEngine.validate_child_blood(p_abo, m_abo, p_rh, m_rh, filho_str):
                    violations.append({
                        "domain": "genealogia",
                        "rule": "blood_type_punnett_compatible",
                        "person_id": child_id,
                        "child_blood": filho_str,
                        "father_blood": f"{p_abo}/{p_rh}",
                        "mother_blood": f"{m_abo}/{m_rh}",
                    })

            # 3. Cor dos olhos biologicamente possível
            c_eye = c_trait.get("cor_olhos") or child.get("cor_olhos")
            p_eye = p_trait.get("cor_olhos") or pai.get("cor_olhos")
            m_eye = m_trait.get("cor_olhos") or mae.get("cor_olhos")
            if c_eye and p_eye and m_eye:
                if p_eye == "azul" and m_eye == "azul" and c_eye not in ("azul", "cinza", "avela"):
                    violations.append({
                        "domain": "genealogia",
                        "rule": "eye_color_compatible",
                        "person_id": child_id,
                        "child_eye": c_eye,
                    })
                else:
                    gt_p = _EYE_GENOTYPES_BY_PHENOTYPE.get(p_eye, ("B", "b"))
                    gt_m = _EYE_GENOTYPES_BY_PHENOTYPE.get(m_eye, ("B", "b"))
                    chart = GeneticEngine.eye_color_chart(gt_p, gt_m)
                    if c_eye in ("castanho", "verde", "azul") and chart.get(c_eye, 0.0) <= 0.0:
                        violations.append({
                            "domain": "genealogia",
                            "rule": "eye_color_compatible",
                            "person_id": child_id,
                            "child_eye": c_eye,
                        })

            # 4. Lateralidade com probabilidade não-zero
            c_hand = c_trait.get("mao_dominante") or child.get("mao_dominante")
            p_canhoto = (p_trait.get("mao_dominante") or pai.get("mao_dominante")) in ("canhota", "esquerda")
            m_canhota = (m_trait.get("mao_dominante") or mae.get("mao_dominante")) in ("canhota", "esquerda")
            prob_left = GeneticEngine.handedness_prob(p_canhoto, m_canhota)
            if c_hand not in ("destra", "canhota", "ambidestra", "direita", "esquerda", "ambidestro") or prob_left <= 0.0:
                violations.append({
                    "domain": "genealogia",
                    "rule": "handedness_nonzero_probability",
                    "person_id": child_id,
                })

    # 5. Ciclos no grafo de parentesco
    for row in dataset.get("parentesco", []):
        if row.get("tipo_parentesco") in ("pai", "mae"):
            pa, pb = row.get("pessoa_id_a"), row.get("pessoa_id_b")
            if pa and pb:
                graph.add_edge(pa, pb)

    if not nx.is_directed_acyclic_graph(graph):
        for cycle in nx.simple_cycles(graph):
            violations.append({
                "domain": "genealogia",
                "rule": "genealogy_no_cycles",
                "cycle": cycle,
            })

    # 6. Herança apenas de pessoas falecidas
    for h in dataset.get("heranca", []):
        fal_id = h.get("pessoa_id_falecido")
        fal = people.get(fal_id) if fal_id else None
        if fal is None or fal.get("esta_vivo", True) or not fal.get("data_obito"):
            violations.append({
                "domain": "genealogia",
                "rule": "inheritance_from_deceased_only",
                "heranca_id": h.get("id"),
                "pessoa_id_falecido": fal_id,
            })

    return violations
