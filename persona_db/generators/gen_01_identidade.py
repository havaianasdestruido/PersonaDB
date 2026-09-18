"""gen_01_identidade — domínio 01: documentos, biometria, fenótipos, idiomas.

Owned by Agent 10. Consome o contrato de gen_00_pessoa:

    generate(persona, rng) -> dict[str, list[dict]]
    generate_all(personas)  -> dict[str, list[dict]]

Cada número de documento é 100% fictício e derivado deterministicamente da
persona (CPF com dígitos verificadores válidos e padrão oficial).
"""
from __future__ import annotations

import hashlib
import os
import sys
from datetime import date, timedelta

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
    cpf = []
    for i, d in enumerate(seed_digits):
        cpf.append(int(d))

    def _dv(partial: list[int], weights: list[int]) -> int:
        total = sum(a * b for a, b in zip(partial, weights))
        resto = (total * 10) % 11
        return 0 if resto == 10 else resto

    cpf.append(_dv(cpf, [10, 9, 8, 7, 6, 5, 4, 3, 2]))
    cpf.append(_dv(cpf, [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]))
    return "".join(str(d) for d in cpf)


def _make_cpf(persona_id: str, idx: int) -> str:
    h = hashlib.sha256(persona_id.encode()).hexdigest()
    suffix = f"{idx % 1000:03d}"
    base9 = "".join(str(int(c, 16) % 10) for c in h[:6]) + suffix
    return _cpf_digits(base9)


def _fake_num(persona_id: str, idx: int, length: int, alphabet: str = "0123456789") -> str:
    h = hashlib.sha256(f"{persona_id}|{length}".encode()).hexdigest()
    out = []
    for i in range(length):
        out.append(alphabet[int(h[i], 16) % len(alphabet)])
    feitos = "".join(out)
    return f"{idx % 10}" + feitos[1:]


def _doc_validade(tipo: str, idx: int, rng: SeededRNG, today: date) -> date | None:
    if tipo not in ("CNH", "passaporte", "titulo de eleitor"):
        return None
    emitido = today - timedelta(days=rng.integer(0, 2200))
    if tipo == "CNH":
        return emitido + timedelta(days=3650)
    if tipo == "titulo de eleitor":
        return emitido + timedelta(days=3650)
    return emitido + timedelta(days=1825)


# ---------------------------------------------------------------------------
# Geração por pessoa
# ---------------------------------------------------------------------------

def _pessoa_documento(persona: dict, rng: SeededRNG, today: date, idx: int) -> list[dict]:
    ids = persona["id"]
    from datetime import datetime
    nasc = datetime.strptime(persona["data_nascimento"], "%Y-%m-%d").date()
    idade = (today - nasc).days / 365.25

    docs: list[dict] = []
    docs.append({"tipo": "RG", "numero_ficticio": _fake_num(ids, idx, 9),
                 "orgao_emissor": _ORGAOS["RG"], "validade": None})
    docs.append({"tipo": "CPF", "numero_ficticio": _make_cpf(ids, idx),
                 "orgao_emissor": _ORGAOS["CPF"], "validade": None})
    if idade >= 18 and rng.bernoulli(0.78):
        docs.append({"tipo": "CNH", "numero_ficticio": _fake_num(ids, idx, 11),
                     "orgao_emissor": _ORGAOS["CNH"],
                     "validade": _doc_validade("CNH", idx, rng, today)})
    if idade >= 16:
        docs.append({"tipo": "titulo de eleitor",
                     "numero_ficticio": _fake_num(ids, idx, 12),
                     "orgao_emissor": _ORGAOS["titulo de eleitor"],
                     "validade": _doc_validade("titulo de eleitor", idx, rng, today)})
    if rng.bernoulli(0.035):
        docs.append({"tipo": "passaporte",
                     "numero_ficticio": _fake_num(ids, idx, 9, "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789"),
                     "orgao_emissor": _ORGAOS["passaporte"],
                     "validade": _doc_validade("passaporte", idx, rng, today)})
    return docs


def _pessoa_biometria(persona: dict, rng: SeededRNG) -> list[dict]:
    ids = persona["id"]
    seed = hashlib.sha256(ids.encode()).hexdigest()
    digit = seed[:40]
    iris = hashlib.sha256((seed + "|iris").encode()).digest()
    import base64
    face = hashlib.sha256((seed + "|face").encode()).hexdigest()
    return [{
        "impressao_digital_ficticia": digit,
        "padrao_iris_ficticio": base64.b64encode(iris).decode(),
        "hash_facial_ficticio": face,
    }]


def _pessoa_foto(persona: dict, rng: SeededRNG, today: date) -> list[dict]:
    ids = persona["id"]
    qtd = 2 + rng.integer(0, 3)
    rows = []
    for k in range(qtd):
        data = (today - timedelta(days=rng.integer(0, 3650))).isoformat()
        rows.append({
            "url_ficticia": f"https://fotos.personadb.test/{ids}/foto-{k}.jpg",
            "data": data,
            "contexto": rng.choice(["documento", "perfil", "evento", "registro"]),
        })
    return rows


def _pessoa_assinatura(persona: dict, rng: SeededRNG, today: date) -> list[dict]:
    return [{
        "modelo_assinatura": f"https://assinaturas.personadb.test/{persona['id']}/assinatura.svg",
        "data_registro": (today - timedelta(days=rng.integer(0, 3650))).isoformat(),
    }]


def _pessoa_caracteristica_fisica(persona: dict, rng: SeededRNG) -> list[dict]:
    return [{
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
    for _ in range(qtd):
        tipo = str(rng.choice(_MARCA_TYPES))
        loc = str(rng.choice(_MARCA_LOC))
        rows.append({
            "tipo": tipo,
            "localizacao_corporal": loc,
            "descricao": f"{tipo} em {loc}",
            "data_aquisicao": (today - timedelta(days=rng.integer(120, 12000))).isoformat(),
        })
    return rows


def _pessoa_idioma(persona: dict, rng: SeededRNG) -> list[dict]:
    idiomas = [{"idioma": "portugues", "nivel_fluencia": "nativo",
                "forma_aprendizado": "família"}]
    prob = 0.18 + (0.12 if persona["education"] in ("superior", "pos") else 0.0)
    if persona["classe_social"] in ("A", "B1"):
        prob += 0.15
    if rng.bernoulli(min(0.95, prob)):
        nivel = str(rng.choice(list(_FLUENCIA_NIVEL.keys()),
                               weights=list(_FLUENCIA_NIVEL.values())))
        idioma = str(rng.choice(_IDIOMAS_SEC))
        idiomas.append({
            "idioma": idioma,
            "nivel_fluencia": nivel,
            "forma_aprendizado": _ORIGEM_IDIOMA[idioma],
        })
    if rng.bernoulli(0.07):
        idiomas.append({
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
        "nome_antigo": nome_antigo,
        "motivo_mudanca": rng.choice(["casamento", "retificação civil", "adoção", "divórcio"]),
        "data_mudanca": (today - timedelta(days=rng.integer(600, 9000))).isoformat(),
    }]


def _pessoa_apelido(persona: dict, rng: SeededRNG) -> list[dict]:
    if not rng.bernoulli(0.28):
        return []
    nick = persona["nome_completo"].split()[0][:3].lower()
    qtd = rng.integer(1, 2)
    rows = []
    for _ in range(qtd):
        apelido, contexto = rng.choice(_APELIDO_METADADOS)
        rows.append({
            "apelido": apelido,
            "origem": nick,
            "contexto_uso": contexto,
        })
    return rows


def generate(persona: dict, rng: SeededRNG, today: date | None = None) -> dict[str, list[dict]]:
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


def generate_all(personas: list[dict], seed: int = 7) -> dict[str, list[dict]]:
    master = new_rng(seed)
    out: dict[str, list[dict]] = {k: [] for k in (
        "pessoa_nome_anterior", "pessoa_apelido", "pessoa_documento",
        "pessoa_biometria", "pessoa_foto", "pessoa_assinatura",
        "pessoa_caracteristica_fisica", "pessoa_marca_distintiva", "pessoa_idioma",
    )}
    for p in personas:
        rng = master.fork(p["id"], "id01")
        rows = generate(p, rng)
        for table, entries in rows.items():
            for e in entries:
                out[table].append({"pessoa_id": p["id"], **e})
    return out


if __name__ == "__main__":  # pragma: no cover
    from persona_db.generators.gen_00_pessoa import generate_personas
    ps = generate_personas(25, seed=11)
    docs = generate_all(ps)
    print("documentos:", len(docs["pessoa_documento"]), "| biometria:",
          len(docs["pessoa_biometria"]), "| idiomas:", len(docs["pessoa_idioma"]))
    from persona_db.seeds.lookup_data import EMPRESAS
    cpf = docs["pessoa_documento"][0 if docs["pessoa_documento"][0]["tipo"] == "CPF" else 1]["numero_ficticio"]
    print("primeiro CPF:", cpf)