"""gen_02_genealogia — domínio 02: família, parentesco, herança e ancestralidade.

Owned by Agent 10. Consome o contrato de gen_00_pessoa:

    generate(personas, seed=7) -> dict[str, list[dict]]

Também enriquece cada persona com 'pai_id'/'mae_id'/'familia_id' (in-place),
permitindo que os domínios posteriores usem a árvore familiar.

Tabelas: familia, membro_familia, parentesco, arvore_genealogica, heranca,
heranca_item, doacao_familiar, condicao_genetica, predisposicao_genetica,
ancestralidade_ficticia.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

try:  # pragma: no cover
    from persona_db.engines.rng import SeededRNG, new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.rng import SeededRNG, new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today

from uuid import NAMESPACE_URL, uuid5

# ---------------------------------------------------------------------------
# Catálogo de condições genéticas fictícias (determinístico)
# ---------------------------------------------------------------------------
_CATALOGO_CONDICOES = [
    ("Sensibilidade a Tempero Mendonça", "paterna", 34.0),
    ("Intolerância Simulada à Lactose", "materna", 68.0),
    ("Bom Humor Hereditário", "paterna", 82.0),
    ("Cabelo Ondulado Variação Norte", "materna", 45.0),
    ("Tolerância Elevada a Sesta", "paterna", 73.0),
    ("Proteção Solar Natural Aumentada", "materna", 28.0),
    ("Memória para Rostos Superficial", "paterna", 19.0),
    ("Ritmo Circadiano Noturno", "materna", 55.0),
]

_ESTATUTO_MEDIO = {
    "A": 1_500_000, "B1": 600_000, "B2": 280_000,
    "C1": 120_000, "C2": 60_000, "D_E": 25_000,
}
_BENS = [
    ("imovel", 0.38), ("veiculo", 0.22), ("aplicacao", 0.19),
    ("poupanca", 0.12), ("semovente", 0.06), ("terreno", 0.03),
]

_DOACOES = [
    "eletrodoméstico", "mobília", "veículo usado", "roupas", "livros",
    "eletrônicos", "ferramentas", "bicicleta",
]
_MOTIVOS = [
    "aniversário", "formatura", "nascimento", "ajuda familiar", "herança em vida",
    "casamento", "Natal",
]

_ORIGEM_HERANCA = ["inventário", "testamento", "partilha amigável"]


@dataclass
class Genealogia:
    rows: dict[str, list[dict]] = field(default_factory=lambda: {
        "familia": [], "membro_familia": [], "parentesco": [],
        "arvore_genealogica": [], "heranca": [], "heranca_item": [],
        "doacao_familiar": [], "condicao_genetica": [],
        "predisposicao_genetica": [], "ancestralidade_ficticia": [],
    })


def _birth(persona: dict) -> date:
    return datetime.strptime(persona["data_nascimento"], "%Y-%m-%d").date()


def generate(personas: list[dict], seed: int = 7, today: date | None = None) -> dict[str, list[dict]]:
    today = today or simulation_today()
    master = new_rng(seed)
    out = Genealogia()

    _condicoes(out, master)
    _parents(personas, out, master)
    _familias(personas, out, master)
    _geracao(personas, out)
    _ancestralidade(personas, out, master)
    _predisposicoes(personas, out, master)
    _heranca(personas, out, master, today)
    _doacoes(personas, out, master, today)
    return out.rows


# ---------------------------------------------------------------------------
# condicao_genetica
# ---------------------------------------------------------------------------
def _condicoes(out: Genealogia, master: SeededRNG) -> None:
    for i, (nome, linha, pct) in enumerate(_CATALOGO_CONDICOES):
        out.rows["condicao_genetica"].append({
            "id": str(uuid5(NAMESPACE_URL, f"condicao-{nome}")),
            "nome_condicao_ficticia": nome,
            "linha_familiar": linha,
            "percentual_manifestacao": round(pct, 2),
        })
    # mapeia nome -> id para predisposições
    out.rows["_cond_id_by_name"] = {
        c["nome_condicao_ficticia"]: c["id"] for c in out.rows["condicao_genetica"]
    }


# ---------------------------------------------------------------------------
# familia + membro_familia
# ---------------------------------------------------------------------------
def _familias(personas: list[dict], out: Genealogia, master: SeededRNG) -> None:
    rng = master.fork("familias", "split")
    sobrenomes: dict[str, list[dict]] = {}
    for p in personas:
        sobrenomes.setdefault(p["ultimo_sobrenome"], []).append(p)

    for sobrenome, membros in sobrenomes.items():
        fam_id = str(uuid5(NAMESPACE_URL, f"familia-{sobrenome.lower()}"))
        out.rows["familia"].append({
            "sobrenome_familiar": sobrenome,
            "origem_ficticia": _origem_do_sobrenome(sobrenome),
        })
        for membro in membros:
            papel = "membro"
            if membro.get("pai_id") or membro.get("mae_id"):
                papel = "filho(a)"
            elif any(c.get("pai_id") == membro["id"] or c.get("mae_id") == membro["id"]
                     for c in membros):
                papel = "pai" if membro["sexo"] == "masculino" else "mae"
            out.rows["membro_familia"].append({
                "pessoa_id": membro["id"],
                "familia_id": fam_id,
                "papel_familiar": papel,
            })
            membro["familia_id"] = fam_id


def _origem_do_sobrenome(sobrenome: str) -> str:
    oracle = sum(ord(c) for c in sobrenome)
    origens = [
        "portuguesa", "espanhola", "italiana", "alemã", "africana",
        "indígena", "japonesa", "libanesa", "polonesa", "ucraniana",
    ]
    return origens[oracle % len(origens)]


# ---------------------------------------------------------------------------
# parentesco: pais -> filhos
# ---------------------------------------------------------------------------
def _parents(personas: list[dict], out: Genealogia, master: SeededRNG) -> None:
    pool = sorted(personas, key=lambda p: p["data_nascimento"])
    for child in personas:
        rng = master.fork(child["id"], "gen02-parents")
        nasc_c = _birth(child)
        pai = mae = None
        if rng.bernoulli(0.86):
            pai = _pick_parent(pool, nasc_c, "masculino", child, rng)
        if rng.bernoulli(0.86):
            mae = _pick_parent(pool, nasc_c, "feminino", child, rng)
        child["pai_id"] = pai["id"] if pai else None
        child["mae_id"] = mae["id"] if mae else None
        _emit_parentesco(out, child, pai, "pai")
        _emit_parentesco(out, child, mae, "mae")


def _pick_parent(pool: list[dict], nasc_child: date, sexo: str,
                 child: dict, rng: SeededRNG) -> dict | None:
    candidates = [
        p for p in pool
        if p["sexo"] == sexo
        and p["id"] != child["id"]
        and _birth(p) <= nasc_child - timedelta(days=18 * 365)
        and _birth(p) >= nasc_child - timedelta(days=50 * 365)
    ]
    if not candidates:
        return None
    matched = [c for c in candidates if c["ultimo_sobrenome"] == child["ultimo_sobrenome"]]
    return rng.choice(matched if (matched and rng.bernoulli(0.55)) else candidates)


def _emit_parentesco(out: Genealogia, child: dict, parent: dict | None, tipo: str) -> None:
    if parent is None:
        return
    child_name = "filho" if child["sexo"] == "masculino" else "filha"
    out.rows["parentesco"].append(
        {"pessoa_id_a": parent["id"], "pessoa_id_b": child["id"],
         "tipo_parentesco": tipo, "grau": 1})
    out.rows["parentesco"].append(
        {"pessoa_id_a": child["id"], "pessoa_id_b": parent["id"],
         "tipo_parentesco": f"{child_name} de", "grau": 1})


# ---------------------------------------------------------------------------
# arvore_genealogica (geração por árvore parental)
# ---------------------------------------------------------------------------
def _geracao(personas: list[dict], out: Genealogia) -> None:
    ger: dict[str, int] = {}
    done = False
    while not done:
        done = True
        for p in personas:
            g_pai = ger.get(p["pai_id"]) if p.get("pai_id") else None
            g_mae = ger.get(p["mae_id"]) if p.get("mae_id") else None
            parents_g = [g for g in (g_pai, g_mae) if g is not None]
            if not parents_g:
                if p["id"] not in ger:
                    ger[p["id"]] = 0
            else:
                novo = max(parents_g) + 1
                if p["id"] not in ger or ger[p["id"]] < novo:
                    ger[p["id"]] = novo
                    done = False
    for p in personas:
        g = ger.get(p["id"], 0)
        out.rows["arvore_genealogica"].append(
            {"pessoa_id": p["id"], "geracao": g, "ramo": "paterno" if p.get("pai_id") else "materno"})
        out.rows["arvore_genealogica"].append(
            {"pessoa_id": p["id"], "geracao": g, "ramo": "materno" if p.get("mae_id") else "paterno"})


# ---------------------------------------------------------------------------
# ancestralidade_ficticia
# ---------------------------------------------------------------------------
def _ancestralidade(personas: list[dict], out: Genealogia, master: SeededRNG) -> None:
    for p in personas:
        for comp in p["ancestry_pcts"]:
            out.rows["ancestralidade_ficticia"].append({
                "pessoa_id": p["id"],
                "origem_percentual": comp["origem_percentual"],
                "regiao_ficticia": comp["regiao_ficticia"],
            })


# ---------------------------------------------------------------------------
# predisposicao_genetica
# ---------------------------------------------------------------------------
def _predisposicoes(personas: list[dict], out: Genealogia, master: SeededRNG) -> None:
    cond_ids = {c["nome_condicao_ficticia"]: i for i, c in enumerate(out.rows["condicao_genetica"])}
    n_cond = len(out.rows["condicao_genetica"])
    for p in personas:
        rng = master.fork(p["id"], "gen02-predispos")
        for _ in range(rng.integer(0, 2)):
            ci = rng.integer(0, n_cond - 1) if n_cond else -1
            if ci < 0:
                break
            grau = round(min(1.0, rng.beta_sample(2.0, 5.0)), 2)
            if grau <= 0.05:
                continue
            out.rows["predisposicao_genetica"].append({
                "pessoa_id": p["id"],
                "condicao_id": None,  # resolved for insert
                "grau_predisposicao": grau,
            })


# ---------------------------------------------------------------------------
# heranca + itens (personas falecidas com herdeiro na família)
# ---------------------------------------------------------------------------
def _heranca(personas: list[dict], out: Genealogia, master: SeededRNG, today: date) -> None:
    id_map = {p["id"]: p for p in personas}
    alive_pool = [p for p in personas if p["esta_vivo"]]
    for p in personas:
        if p["esta_vivo"] or not p.get("data_obito"):
            continue
        rng = master.fork(p["id"], "gen02-heranca")
        if not rng.bernoulli(0.55):
            continue
        heirs = [h for h in alive_pool
                 if h["familia_id"] == p.get("familia_id")
                 and h["id"] != p["id"]]
        if not heirs:
            continue
        heir = rng.choice(heirs)
        heranca_id = f"HERC-{len(out.rows['heranca']):07d}"
        data = max(_birth(p), datetime.strptime(p["data_obito"], "%Y-%m-%d").date())
        data = data + timedelta(days=rng.integer(20, 400))
        out.rows["heranca"].append({
            "pessoa_id_herdeiro": heir["id"],
            "pessoa_id_falecido": p["id"],
            "data": data.isoformat(),
            "origem": str(rng.choice(_ORIGEM_HERANCA)),
        })
        base = _ESTATUTO_MEDIO.get(p["classe_social"], 60_000)
        valor = max(1_000.0, round(base * rng.log_normal(0.0, 0.6), 2))
        n_itens = rng.integer(1, 3)
        for k in range(n_itens):
            tipo, w = rng.choice(_BENS)
            parcela = valor / n_itens
            out.rows["heranca_item"].append({
                "heranca_id": heranca_id,
                "tipo_bem": tipo,
                "valor_estimado": round(parcela, 2),
                "descricao": f"{tipo} herdado de {p['nome_completo']}",
            })


# ---------------------------------------------------------------------------
# doacao_familiar
# ---------------------------------------------------------------------------
def _doacoes(personas: list[dict], out: Genealogia, master: SeededRNG, today: date) -> None:
    for p in personas:
        rng = master.fork(p["id"], "gen02-doacao")
        if not rng.bernoulli(0.06):
            continue
        receptores = [q for q in personas
                      if q["familia_id"] == p.get("familia_id") and q["id"] != p["id"]]
        if not receptores:
            continue
        receptor = rng.choice(receptores)
        out.rows["doacao_familiar"].append({
            "pessoa_id_doador": p["id"],
            "pessoa_id_receptor": receptor["id"],
            "item": str(rng.choice(_DOACOES)),
            "data": (today - timedelta(days=rng.integer(10, 1600))).isoformat(),
            "motivo": str(rng.choice(_MOTIVOS)),
        })


if __name__ == "__main__":  # pragma: no cover
    from persona_db.generators.gen_00_pessoa import generate_personas
    ps = generate_personas(300, seed=5)
    rows = generate(ps)
    for tbl in ("familia", "membro_familia", "parentesco", "arvore_genealogica",
                "heranca", "heranca_item", "doacao_familiar", "condicao_genetica",
                "predisposicao_genetica", "ancestralidade_ficticia"):
        print(f"{tbl:26s} {len(rows[tbl])}")
    print("pai_id preenchido:", sum(1 for p in ps if p.get("pai_id")),
          "| mae_id preenchido:", sum(1 for p in ps if p.get("mae_id")))