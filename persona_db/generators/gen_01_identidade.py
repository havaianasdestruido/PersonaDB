"""gen_01_identidade — domínio 01: documentos, biometria, fenótipos, idiomas.

Owned by Agent 10. Consome o contrato de gen_00_pessoa:

    generate(persona, rng) -> dict[str, list[dict]]
    generate_all(personas)  -> dict[str, list[dict]]

Cada número de documento é 100% fictício e derivado deterministicamente da
persona (CPF com dígitos verificadores válidos e padrão oficial).
"""
from __future__ import annotations

import base64
import hashlib
import os
import sys
from datetime import date, timedelta
from uuid import NAMESPACE_URL, uuid5

try:  # pragma: no cover
    from persona_db.engines.rng import SeededRNG, new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.rng import SeededRNG, new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today

_ORGAOS = {
    "RG": "SSP Fictícia",
    "CPF": "Receita Federal Fictícia",
    "CNH": "DETRAN Fictício",
    "passaporte": "Polícia Federal Fictícia",
    "titulo de eleitor": "Justiça Eleitoral Fictícia",
}

_MARCA_TYPES = ["tatuagem", "cicatriz", "sinal", "pintinha", "protesis"]
_MARCA_LOC = [
    "antebraço esquerdo", "tornozelo direito", "costas", "panturrilha",
    "ombro", "mão direita", "pescoço", "braço direito", "coxa esquerda", "pulso",
]
_APELIDO_METADADOS = [
    ("apelido de infância", "casa"),
    ("apelido do trabalho", "trabalho"),
    ("redução do nome", "escola"),
    ("apelido esportivo", "amigos"),
]

_IDIOMAS_SEC = [
    "ingles", "espanhol", "frances", "mandarim", "alema", "italiano", "japones", "coreano",
]

_ORIGEM_IDIOMA = {
    "ingles": "escola",
    "espanhol": "curso livre",
    "frances": "curso livre",
    "mandarim": "intercâmbio",
    "alema": "intercâmbio",
    "italiano": "família",
    "japones": "família",
    "coreano": "intercâmbio",
}

_FLUENCIA_NIVEL = {
    "basico": 0.45, "intermediario": 0.32, "avancado": 0.15,
    "fluente": 0.06, "nativo": 0.02,
}


# ---------------------------------------------------------------------------
# Números de documento
# ---------------------------------------------------------------------------

def _cpf_digits(seed_digits: str) -> str:
    """Adiciona dígitos verificadores válidos a 9 dígitos-base."""
    cpf = [int(d) for d in seed_digits]

    def _dv(partial: list[int], weights: list[int]) -> int:
        total = sum(a * b for a, b in zip(partial, weights))
        resto = (total * 10) % 11
        return 0 if resto == 10 else resto

    cpf.append(_dv(cpf, [10, 9, 8, 7, 6, 5, 4, 3, 2]))
    cpf.append(_dv(cpf, [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]))
    return "".join(str(d) for d in cpf)


def _make_cpf(persona_id: str, idx: int) -> str:
    """Gera CPF fictício com prefixo 000 e dígitos verificadores válidos."""
    h = hashlib.sha256(persona_id.encode()).hexdigest()
    suffix = f"{idx % 1000:03d}"
    base9 = "000" + "".join(str(int(c, 16) % 10) for c in h[:3]) + suffix
    return _cpf_digits(base9)


def _fake_num(persona_id: str, idx: int, length: int, alphabet: str = "0123456789") -> str:
    h = hashlib.sha256(f"{persona_id}|{length}".encode()).hexdigest()
    out = [alphabet[int(h[i], 16) % len(alphabet)] for i in range(length)]
    feitos = "".join(out)
    return f"{idx % 10}" + feitos[1:]


def _doc_validade(tipo: str, idx: int, rng: SeededRNG, today: date) -> str | None:
    if tipo not in ("CNH", "passaporte", "titulo de eleitor"):
        return None
    emitido = today - timedelta(days=rng.integer(0, 1400))
    if tipo in ("CNH", "titulo de eleitor"):
        return (emitido + timedelta(days=3650)).isoformat()
    return (emitido + timedelta(days=3650)).isoformat()


def _life_date(persona: dict, rng: SeededRNG, today: date, min_age_years: int = 0) -> str:
    born = date.fromisoformat(persona["data_nascimento"])
    end = date.fromisoformat(persona["data_obito"]) if persona.get("data_obito") else today
    end = min(end, today)
    start = min(end, born + timedelta(days=min_age_years * 365))
    if start >= end:
        return end.isoformat()
    span = max(1, (end - start).days)
    return (start + timedelta(days=rng.integer(0, span - 1))).isoformat()


# ---------------------------------------------------------------------------
# Geração por pessoa
# ---------------------------------------------------------------------------

def _pessoa_documento(persona: dict, rng: SeededRNG, today: date, idx: int) -> list[dict]:
    ids = persona["id"]
    nasc = date.fromisoformat(persona["data_nascimento"])
    idade = (today - nasc).days / 365.25

    docs: list[dict] = []
    docs.append({
        "id": str(uuid5(NAMESPACE_URL, f"doc-{ids}-RG")),
        "tipo": "RG",
        "numero_ficticio": _fake_num(ids, idx, 9),
        "orgao_emissor": _ORGAOS["RG"],
        "validade": None,
    })
    docs.append({
        "id": str(uuid5(NAMESPACE_URL, f"doc-{ids}-CPF")),
        "tipo": "CPF",
        "numero_ficticio": _make_cpf(ids, idx),
        "orgao_emissor": _ORGAOS["CPF"],
        "validade": None,
    })
    if idade >= 18 and rng.bernoulli(0.78):
        docs.append({
            "id": str(uuid5(NAMESPACE_URL, f"doc-{ids}-CNH")),
            "tipo": "CNH",
            "numero_ficticio": _fake_num(ids, idx, 11),
            "orgao_emissor": _ORGAOS["CNH"],
            "validade": _doc_validade("CNH", idx, rng, today),
        })
    if idade >= 16:
        docs.append({
            "id": str(uuid5(NAMESPACE_URL, f"doc-{ids}-TE")),
            "tipo": "titulo de eleitor",
            "numero_ficticio": _fake_num(ids, idx, 12),
            "orgao_emissor": _ORGAOS["titulo de eleitor"],
            "validade": _doc_validade("titulo de eleitor", idx, rng, today),
        })
    p_pass = 0.45 if persona["classe_social"] in ("A", "B1") else (0.18 if persona["classe_social"] == "B2" else 0.05)
    if rng.bernoulli(p_pass):
        val = _doc_validade("passaporte", idx, rng, today)
        persona["passaporte_validade"] = val
        docs.append({
            "id": str(uuid5(NAMESPACE_URL, f"doc-{ids}-PASS")),
            "tipo": "passaporte",
            "numero_ficticio": _fake_num(ids, idx, 9, "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789"),
            "orgao_emissor": _ORGAOS["passaporte"],
            "validade": val,
        })
    return docs


def _pessoa_biometria(persona: dict, rng: SeededRNG) -> list[dict]:
    ids = persona["id"]
    seed = hashlib.sha256(ids.encode()).hexdigest()
    digit = seed[:40]
    iris = hashlib.sha256((seed + "|iris").encode()).digest()
    face = hashlib.sha256((seed + "|face").encode()).hexdigest()
    return [{
        "id": str(uuid5(NAMESPACE_URL, f"bio-{ids}")),
        "impressao_digital_ficticia": digit,
        "padrao_iris_ficticio": base64.b64encode(iris).decode(),
        "hash_facial_ficticio": face,
    }]


def _pessoa_foto(persona: dict, rng: SeededRNG, today: date) -> list[dict]:
    ids = persona["id"]
    qtd = 2 + rng.integer(0, 3)
    rows = []
    for k in range(qtd):
        data = _life_date(persona, rng, today)
        rows.append({
            "id": str(uuid5(NAMESPACE_URL, f"foto-{ids}-{k}")),
            "url_ficticia": f"https://fotos.personadb.test/{ids}/foto-{k}.jpg",
            "data": data,
            "contexto": str(rng.choice(["documento", "perfil", "evento", "registro"])),
        })
    return rows


def _pessoa_assinatura(persona: dict, rng: SeededRNG, today: date) -> list[dict]:
    ids = persona["id"]
    return [{
        "id": str(uuid5(NAMESPACE_URL, f"ass-{ids}")),
        "modelo_assinatura": f"https://assinaturas.personadb.test/{ids}/assinatura.svg",
        "data_registro": _life_date(persona, rng, today, min_age_years=10),
    }]


def _pessoa_caracteristica_fisica(persona: dict, rng: SeededRNG) -> list[dict]:
    return [{
        "id": str(uuid5(NAMESPACE_URL, f"fis-{persona['id']}")),
        "altura": persona["altura"],
        "peso": persona["peso"],
        "cor_olhos": persona["cor_olhos"],
        "cor_cabelo": persona["cor_cabelo"],
        "mao_dominante": persona["mao_dominante"],
        "tipo_sanguineo": persona["tipo_sanguineo"],
        "fator_rh": persona["fator_rh"],
    }]


def _pessoa_marca_distintiva(persona: dict, rng: SeededRNG, today: date) -> list[dict]:
    if not rng.bernoulli(0.32):
        return []
    qtd = rng.integer(1, 2)
    rows = []
    for k in range(qtd):
        tipo = str(rng.choice(_MARCA_TYPES))
        loc = str(rng.choice(_MARCA_LOC))
        rows.append({
            "id": str(uuid5(NAMESPACE_URL, f"marca-{persona['id']}-{k}")),
            "tipo": tipo,
            "localizacao_corporal": loc,
            "descricao": f"{tipo} em {loc}",
            "data_aquisicao": _life_date(persona, rng, today, min_age_years=5),
        })
    return rows


def _pessoa_idioma(persona: dict, rng: SeededRNG) -> list[dict]:
    ids = persona["id"]
    idiomas = [{
        "id": str(uuid5(NAMESPACE_URL, f"idioma-{ids}-pt")),
        "idioma": "portugues",
        "nivel_fluencia": "nativo",
        "forma_aprendizado": "família",
    }]
    prob = 0.18 + (0.12 if persona["education"] in ("superior", "pos") else 0.0)
    if persona["classe_social"] in ("A", "B1"):
        prob += 0.15
    if rng.bernoulli(min(0.95, prob)):
        nivel = str(rng.choice(list(_FLUENCIA_NIVEL.keys()),
                               weights=list(_FLUENCIA_NIVEL.values())))
        idioma = str(rng.choice(_IDIOMAS_SEC))
        idiomas.append({
            "id": str(uuid5(NAMESPACE_URL, f"idioma-{ids}-{idioma}")),
            "idioma": idioma,
            "nivel_fluencia": nivel,
            "forma_aprendizado": _ORIGEM_IDIOMA[idioma],
        })
    if rng.bernoulli(0.07) and not any(i["idioma"] == "espanhol" for i in idiomas):
        idiomas.append({
            "id": str(uuid5(NAMESPACE_URL, f"idioma-{ids}-espanhol-2")),
            "idioma": "espanhol",
            "nivel_fluencia": "basico",
            "forma_aprendizado": "viagens",
        })
    return idiomas


def _pessoa_nome_anterior(persona: dict, rng: SeededRNG, today: date) -> list[dict]:
    if not rng.bernoulli(0.03):
        return []
    from persona_db.seeds.lookup_data import SURNAMES
    nome_antigo = persona["nome_completo"].rsplit(" ", 1)[0] + " " + str(rng.choice(SURNAMES))
    return [{
        "id": str(uuid5(NAMESPACE_URL, f"nomeant-{persona['id']}")),
        "nome_antigo": nome_antigo,
        "motivo_mudanca": str(rng.choice(["casamento", "retificação civil", "adoção", "divórcio"])),
        "data_mudanca": _life_date(persona, rng, today, min_age_years=18),
    }]


def _pessoa_apelido(persona: dict, rng: SeededRNG) -> list[dict]:
    if not rng.bernoulli(0.28):
        return []
    nick = persona["nome_completo"].split()[0][:3].lower()
    qtd = rng.integer(1, 2)
    rows = []
    for k in range(qtd):
        apelido, contexto = rng.choice(_APELIDO_METADADOS)
        rows.append({
            "id": str(uuid5(NAMESPACE_URL, f"apelido-{persona['id']}-{k}")),
            "apelido": str(apelido),
            "origem": nick,
            "contexto_uso": str(contexto),
        })
    return rows


def generate_one(persona: dict, rng: SeededRNG, today: date | None = None) -> dict[str, list[dict]]:
    """Gera todas as tabelas de identidade e biometria para uma única persona."""
    today = today or simulation_today()
    idx = int(persona["idx"])
    return {
        "pessoa_nome_anterior": _pessoa_nome_anterior(persona, rng, today),
        "pessoa_apelido": _pessoa_apelido(persona, rng),
        "pessoa_documento": _pessoa_documento(persona, rng, today, idx),
        "pessoa_biometria": _pessoa_biometria(persona, rng),
        "pessoa_foto": _pessoa_foto(persona, rng, today),
        "pessoa_assinatura": _pessoa_assinatura(persona, rng, today),
        "pessoa_caracteristica_fisica": _pessoa_caracteristica_fisica(persona, rng),
        "pessoa_marca_distintiva": _pessoa_marca_distintiva(persona, rng, today),
        "pessoa_idioma": _pessoa_idioma(persona, rng),
    }


def generate_all(personas: list[dict], seed: int = 7, today: date | None = None) -> dict[str, list[dict]]:
    """Gera as tabelas do domínio 01 para todas as personas."""
    today = today or simulation_today()
    master = new_rng(seed)
    out: dict[str, list[dict]] = {k: [] for k in (
        "pessoa_nome_anterior", "pessoa_apelido", "pessoa_documento",
        "pessoa_biometria", "pessoa_foto", "pessoa_assinatura",
        "pessoa_caracteristica_fisica", "pessoa_marca_distintiva", "pessoa_idioma",
    )}
    for p in personas:
        rng = master.fork(p["id"], "id01")
        rows = generate_one(p, rng, today=today)
        for table, entries in rows.items():
            for e in entries:
                out[table].append({"pessoa_id": p["id"], **e})
    return out


def generate(
    persona_or_list: dict | list[dict],
    rng_or_seed: SeededRNG | int = 7,
    today: date | None = None,
    *,
    seed: int | None = None,
) -> dict[str, list[dict]]:
    """Aceita uma lista de personas (batch) ou uma única persona."""
    if isinstance(persona_or_list, list):
        eff_seed = seed if seed is not None else (int(rng_or_seed) if isinstance(rng_or_seed, int) else 7)
        return generate_all(persona_or_list, seed=eff_seed, today=today)
    rng = rng_or_seed if isinstance(rng_or_seed, SeededRNG) else new_rng(int(rng_or_seed))
    return generate_one(persona_or_list, rng, today=today)


if __name__ == "__main__":  # pragma: no cover
    from persona_db.generators.gen_00_pessoa import generate_personas
    ps = generate_personas(25, seed=11)
    docs = generate_all(ps)
    print("documentos:", len(docs["pessoa_documento"]), "| biometria:",
          len(docs["pessoa_biometria"]), "| idiomas:", len(docs["pessoa_idioma"]))
    cpf = docs["pessoa_documento"][0 if docs["pessoa_documento"][0]["tipo"] == "CPF" else 1]["numero_ficticio"]
    print("primeiro CPF:", cpf)
