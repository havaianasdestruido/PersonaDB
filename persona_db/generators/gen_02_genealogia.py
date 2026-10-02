"""gen_02_genealogia — domínio 02: família, parentesco, herança e ancestralidade.

Owned by Agent 10. Consome o contrato de gen_00_pessoa:

    generate(personas, seed=7) -> dict[str, list[dict]]

Também enriquece cada persona com 'pai_id'/'mae_id'/'familia_id' (in-place)
e propaga a herança genética de traços físicos (tipo sanguíneo, fator Rh,
cor dos olhos, cor do cabelo, lateralidade, altura e peso) em ordem
topológica geracional, permitindo que os domínios posteriores usem a árvore
familiar com 100% de consistência mendeliana e poligênica.

Tabelas: familia, membro_familia, parentesco, arvore_genealogica, heranca,
heranca_item, doacao_familiar, condicao_genetica, predisposicao_genetica,
ancestralidade_ficticia.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from uuid import NAMESPACE_URL, uuid5

try:  # pragma: no cover
    from persona_db.engines.constants import BLOOD_GROUP_PRIORS
    from persona_db.engines.genetics import GeneticEngine
    from persona_db.engines.rng import SeededRNG, new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.constants import BLOOD_GROUP_PRIORS
    from persona_db.engines.genetics import GeneticEngine
    from persona_db.engines.rng import SeededRNG, new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today

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

_EYE_GENOTYPES_BY_PHENOTYPE: dict[str, tuple[str, str]] = {
    "castanho": ("B", "b"),
    "ambar": ("B", "g"),
    "verde": ("G", "b"),
    "avela": ("g", "g"),
    "cinza": ("b", "b"),
    "azul": ("b", "b"),
}

_MAO_MAP = {"direita": "destra", "esquerda": "canhota", "ambidestro": "ambidestra"}


@dataclass
class Genealogia:
    """Container acumulador para as tabelas do domínio 02."""

    rows: dict[str, list[dict]] = field(default_factory=lambda: {
        "familia": [], "membro_familia": [], "parentesco": [],
        "arvore_genealogica": [], "heranca": [], "heranca_item": [],
        "doacao_familiar": [], "condicao_genetica": [],
        "predisposicao_genetica": [], "ancestralidade_ficticia": [],
    })


def _birth(persona: dict) -> date:
    """Retorna a data de nascimento da persona como objeto `date`."""
    return date.fromisoformat(persona["data_nascimento"])


def _death(persona: dict) -> date | None:
    """Retorna a data de óbito da persona ou `None` se estiver viva."""
    if persona.get("data_obito"):
        return date.fromisoformat(persona["data_obito"])
    return None


def generate(personas: list[dict], seed: int = 7, today: date | None = None) -> dict[str, list[dict]]:
    """Gera todas as tabelas de genealogia e propaga traços genéticos aos filhos."""
    today = today or simulation_today()
    master = new_rng(seed)
    out = Genealogia()

    _condicoes(out, master)
    _parents(personas, out, master)
    _familias(personas, out, master)
    ger = _geracao(personas, out)
    _herdar_tracos(personas, ger, master)
    _ancestralidade(personas, out, master)
    _predisposicoes(personas, out, master)
    _heranca(personas, out, master, today)
    _doacoes(personas, out, master, today)
    out.rows.pop("_cond_id_by_name", None)
    return out.rows


# ---------------------------------------------------------------------------
# condicao_genetica
# ---------------------------------------------------------------------------
def _condicoes(out: Genealogia, master: SeededRNG) -> None:
    for _i, (nome, linha, pct) in enumerate(_CATALOGO_CONDICOES):
        out.rows["condicao_genetica"].append({
            "id": str(uuid5(NAMESPACE_URL, f"condicao-{nome}")),
            "nome_condicao_ficticia": nome,
            "linha_familiar": linha,
            "percentual_manifestacao": round(pct, 2),
        })
    out.rows["_cond_id_by_name"] = {
        c["nome_condicao_ficticia"]: c["id"] for c in out.rows["condicao_genetica"]
    }


# ---------------------------------------------------------------------------
# familia + membro_familia
# ---------------------------------------------------------------------------
def _familias(personas: list[dict], out: Genealogia, master: SeededRNG) -> None:
    master.fork("familias", "split")
    sobrenomes: dict[str, list[dict]] = {}
    for p in personas:
        sobrenomes.setdefault(p["ultimo_sobrenome"], []).append(p)

    for sobrenome, membros in sobrenomes.items():
        fam_id = str(uuid5(NAMESPACE_URL, f"familia-{sobrenome.lower()}"))
        out.rows["familia"].append({
            "id": fam_id,
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
                "id": str(uuid5(NAMESPACE_URL, f"membro-fam-{membro['id']}-{fam_id}")),
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
        and _birth(p) >= nasc_child - timedelta(days=48 * 365)
        and (_death(p) is None or _death(p) >= nasc_child)
    ]
    if not candidates:
        return None
    matched = [c for c in candidates if c["ultimo_sobrenome"] == child["ultimo_sobrenome"]]
    return rng.choice(matched if (matched and rng.bernoulli(0.55)) else candidates)


def _emit_parentesco(out: Genealogia, child: dict, parent: dict | None, tipo: str) -> None:
    if parent is None:
        return
    child_name = "filho" if child["sexo"] == "masculino" else "filha"
    out.rows["parentesco"].append({
        "id": str(uuid5(NAMESPACE_URL, f"par-{parent['id']}-{child['id']}-{tipo}")),
        "pessoa_id_a": parent["id"],
        "pessoa_id_b": child["id"],
        "tipo_parentesco": tipo,
        "grau": 1,
    })
    out.rows["parentesco"].append({
        "id": str(uuid5(NAMESPACE_URL, f"par-{child['id']}-{parent['id']}-{child_name}")),
        "pessoa_id_a": child["id"],
        "pessoa_id_b": parent["id"],
        "tipo_parentesco": f"{child_name} de",
        "grau": 1,
    })


# ---------------------------------------------------------------------------
# arvore_genealogica (geração por árvore parental)
# ---------------------------------------------------------------------------
def _geracao(personas: list[dict], out: Genealogia) -> dict[str, int]:
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
        p["geracao"] = g
        out.rows["arvore_genealogica"].append({
            "id": str(uuid5(NAMESPACE_URL, f"arv-{p['id']}-0")),
            "pessoa_id": p["id"],
            "geracao": g,
            "ramo": "paterno" if p.get("pai_id") else "materno",
        })
        out.rows["arvore_genealogica"].append({
            "id": str(uuid5(NAMESPACE_URL, f"arv-{p['id']}-1")),
            "pessoa_id": p["id"],
            "geracao": g,
            "ramo": "materno" if p.get("mae_id") else "paterno",
        })
    return ger


# ---------------------------------------------------------------------------
# Herança mendeliana e poligênica de traços físicos
# ---------------------------------------------------------------------------
def _herdar_tracos(personas: list[dict], ger: dict[str, int], master: SeededRNG) -> None:
    """Atualiza traços físicos dos filhos em ordem topológica de geração."""
    by_id = {p["id"]: p for p in personas}
    ordered = sorted(personas, key=lambda p: (ger.get(p["id"], 0), p["idx"]))

    for p in ordered:
        pai = by_id.get(p.get("pai_id")) if p.get("pai_id") else None
        mae = by_id.get(p.get("mae_id")) if p.get("mae_id") else None
        if pai is None and mae is None:
            continue

        rng = master.fork(p["id"], "gen02-genetics")
        gen = GeneticEngine(rng)

        # Tipo sanguíneo e Rh compatíveis com Punnett
        abo_pai = pai["tipo_sanguineo"] if pai else str(
            rng.choice(list(BLOOD_GROUP_PRIORS.keys()), weights=list(BLOOD_GROUP_PRIORS.values()))
        )
        abo_mae = mae["tipo_sanguineo"] if mae else str(
            rng.choice(list(BLOOD_GROUP_PRIORS.keys()), weights=list(BLOOD_GROUP_PRIORS.values()))
        )
        rh_pai = pai["fator_rh"] if pai else ("negativo" if rng.bernoulli(0.13) else "positivo")
        rh_mae = mae["fator_rh"] if mae else ("negativo" if rng.bernoulli(0.13) else "positivo")

        blood_full = gen.herdar_tipo_sanguineo(abo_pai, abo_mae, rh_pai, rh_mae)
        p["tipo_sanguineo"] = blood_full[:-1]
        p["fator_rh"] = "positivo" if blood_full.endswith("+") else "negativo"

        # Cor dos olhos (dois pais de olhos claros recessivos só geram filhos compatíveis)
        olhos_pai = pai["cor_olhos"] if pai else p["cor_olhos"]
        olhos_mae = mae["cor_olhos"] if mae else p["cor_olhos"]
        if olhos_pai == "azul" and olhos_mae == "azul":
            p["cor_olhos"] = "azul"
        else:
            gt_pai = _EYE_GENOTYPES_BY_PHENOTYPE.get(olhos_pai, ("B", "b"))
            gt_mae = _EYE_GENOTYPES_BY_PHENOTYPE.get(olhos_mae, ("B", "b"))
            chart = gen.eye_color_chart(gt_pai, gt_mae)
            p["cor_olhos"] = str(rng.choice(list(chart.keys()), weights=list(chart.values())))

        # Cor do cabelo
        cabelo_pai = pai["cor_cabelo"] if pai else p["cor_cabelo"]
        cabelo_mae = mae["cor_cabelo"] if mae else p["cor_cabelo"]
        eur_pct = sum(
            c["origem_percentual"] / 100.0
            for c in p.get("ancestry_pcts", [])
            if c["regiao_ficticia"] == "europeia"
        )
        p["cor_cabelo"] = gen.hair_color(cabelo_pai, cabelo_mae, eur_pct)

        # Lateralidade (modelo logístico familiar)
        pai_canhoto = bool(pai and pai["mao_dominante"] in ("canhota", "esquerda"))
        mae_canhota = bool(mae and mae["mao_dominante"] in ("canhota", "esquerda"))
        mao = gen.handedness(pai_canhoto, mae_canhota)
        p["mao_dominante"] = _MAO_MAP.get(mao, "destra")

        # Altura (mid-parent height) e peso correlacionado
        alt_pai = float(pai["altura"]) if pai else 172.0
        alt_mae = float(mae["altura"]) if mae else 160.0
        sex_code = "M" if p["sexo"] == "masculino" else "F"
        nova_altura = max(55.0, min(220.0, gen.expected_child_height(alt_pai, alt_mae, sex_code)))
        p["altura"] = round(nova_altura, 2)
        p["peso"] = round(max(3.0, min(280.0, gen.peso_from_height(nova_altura, p["sexo"]))), 2)


# ---------------------------------------------------------------------------
# ancestralidade_ficticia
# ---------------------------------------------------------------------------
def _ancestralidade(personas: list[dict], out: Genealogia, master: SeededRNG) -> None:
    for p in personas:
        for i, comp in enumerate(p["ancestry_pcts"]):
            out.rows["ancestralidade_ficticia"].append({
                "id": str(uuid5(NAMESPACE_URL, f"anc-{p['id']}-{i}")),
                "pessoa_id": p["id"],
                "origem_percentual": comp["origem_percentual"],
                "regiao_ficticia": comp["regiao_ficticia"],
            })


# ---------------------------------------------------------------------------
# predisposicao_genetica
# ---------------------------------------------------------------------------
def _predisposicoes(personas: list[dict], out: Genealogia, master: SeededRNG) -> None:
    n_cond = len(out.rows["condicao_genetica"])
    for p in personas:
        rng = master.fork(p["id"], "gen02-predispos")
        seen_conds: set[str] = set()
        for k in range(rng.integer(0, 2)):
            ci = rng.integer(0, n_cond - 1) if n_cond else -1
            if ci < 0:
                break
            cond_id = out.rows["condicao_genetica"][ci]["id"]
            if cond_id in seen_conds:
                continue
            grau = round(min(1.0, rng.beta_sample(2.0, 5.0)), 2)
            if grau <= 0.05:
                continue
            seen_conds.add(cond_id)
            out.rows["predisposicao_genetica"].append({
                "id": str(uuid5(NAMESPACE_URL, f"pred-{p['id']}-{k}")),
                "pessoa_id": p["id"],
                "condicao_id": cond_id,
                "grau_predisposicao": grau,
            })


# ---------------------------------------------------------------------------
# heranca + itens (personas falecidas com herdeiro na família)
# ---------------------------------------------------------------------------
def _heranca(personas: list[dict], out: Genealogia, master: SeededRNG, today: date) -> None:
    alive_pool = [p for p in personas if p["esta_vivo"]]
    for p in personas:
        p.setdefault("heranca_recebida", 0.0)
    for p in personas:
        if p["esta_vivo"] or not p.get("data_obito"):
            continue
        rng = master.fork(p["id"], "gen02-heranca")
        if not rng.bernoulli(0.55):
            continue
        obito_dt = date.fromisoformat(p["data_obito"])
        heirs = [
            h for h in alive_pool
            if h["familia_id"] == p.get("familia_id")
            and h["id"] != p["id"]
            and _birth(h) <= obito_dt
        ]
        if not heirs:
            continue
        heir = rng.choice(heirs)
        heranca_id = str(uuid5(NAMESPACE_URL, f"heranca-{p['id']}"))
        data = max(_birth(p), obito_dt) + timedelta(days=rng.integer(20, 400))
        if data > today:
            data = obito_dt
        out.rows["heranca"].append({
            "id": heranca_id,
            "pessoa_id_herdeiro": heir["id"],
            "pessoa_id_falecido": p["id"],
            "data": data.isoformat(),
            "origem": str(rng.choice(_ORIGEM_HERANCA)),
        })
        base = _ESTATUTO_MEDIO.get(p["classe_social"], 60_000)
        valor = max(1_000.0, round(base * rng.log_normal(0.0, 0.6), 2))
        heir["heranca_recebida"] = round(float(heir.get("heranca_recebida", 0.0)) + valor, 2)
        n_itens = rng.integer(1, 3)
        for k in range(n_itens):
            tipo, _w = rng.choice(_BENS)
            parcela = round(valor / n_itens, 2)
            out.rows["heranca_item"].append({
                "id": str(uuid5(NAMESPACE_URL, f"heranca-item-{heranca_id}-{k}")),
                "heranca_id": heranca_id,
                "tipo_bem": tipo,
                "valor_estimado": parcela,
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
        receptores = [
            q for q in personas
            if q["familia_id"] == p.get("familia_id") and q["id"] != p["id"]
        ]
        if not receptores:
            continue
        receptor = rng.choice(receptores)
        min_dt = max(_birth(p), _birth(receptor)) + timedelta(days=30)
        max_dt = min(_death(p) or today, _death(receptor) or today, today)
        if min_dt >= max_dt:
            continue
        span = max(1, (max_dt - min_dt).days)
        data_doacao = min_dt + timedelta(days=rng.integer(0, span - 1))
        out.rows["doacao_familiar"].append({
            "id": str(uuid5(NAMESPACE_URL, f"doacao-{p['id']}-{receptor['id']}")),
            "pessoa_id_doador": p["id"],
            "pessoa_id_receptor": receptor["id"],
            "item": str(rng.choice(_DOACOES)),
            "data": data_doacao.isoformat(),
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
