"""gen_10_digital — domínio 10: dispositivos, contas digitais, redes sociais e streaming.

Implementa TASK-052 de TODO.MD:
- Adoção de smartphones e dispositivos por idade e classe socioeconômica.
- Plataformas de redes sociais diferenciadas por faixa etária (TikTok/Instagram
  para jovens, Facebook/LinkedIn para adultos).
- Distribuição power-law (log-normal de cauda pesada) para número de seguidores.
- Força de senha correlacionada com o nível de escolaridade.
"""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta
from typing import Any
from uuid import NAMESPACE_URL, uuid5

try:  # pragma: no cover
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today

_JOGOS = [
    ("Crônicas de Alvorada Online", "PC", "RPG"),
    ("Futebol Brasileiro Virtual 2026", "Console", "Esporte"),
    ("Corrida Horizonte Turbo", "Mobile", "Corrida"),
    ("Estratégia Imperial Simulada", "PC", "Estratégia"),
]

_DOMINIOS_WEB = [
    "noticias.personadb.test",
    "videos.personadb.test",
    "esportes.personadb.test",
    "educacao.personadb.test",
    "financas.personadb.test",
]

_APPS = [
    ("Mensageiro Instantâneo Ficc.", "comunicacao"),
    ("Banco Digital Virtual", "financas"),
    ("Entrega Rápida Simulada", "consumo"),
    ("RedeFotos Inventada", "rede_social"),
]

_STREAMINGS = [
    ("CineStream Fictício", "padrão", 39.90),
    ("MúsicaViva Virtual", "individual", 21.90),
    ("EsportePlay Simulado", "premium", 54.90),
]


def _birth(p: dict[str, Any]) -> date:
    return date.fromisoformat(p["data_nascimento"])


def _end_date(p: dict[str, Any], today: date) -> date:
    if p.get("data_obito"):
        return min(today, date.fromisoformat(p["data_obito"]))
    return today


def generate(
    personas: list[dict[str, Any]],
    seed: int = 7,
    today: date | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Gera todas as tabelas do domínio 10 (Vida Digital)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "dispositivo": [],
        "conta_digital": [],
        "perfil_rede_social": [],
        "publicacao_rede_social": [],
        "historico_navegacao_ficticio": [],
        "jogo": [],
        "progresso_jogo": [],
        "assinatura_streaming": [],
        "senha_registro_ficticio": [],
        "dispositivo_troca_historico": [],
        "app_instalado": [],
        "provedor_internet": [],
    }

    jogos: list[dict[str, Any]] = []
    for nome, plat, gen in _JOGOS:
        jid = str(uuid5(NAMESPACE_URL, f"jogo-{nome}"))
        rec = {"id": jid, "nome": nome, "plataforma": plat, "genero": gen}
        rows["jogo"].append(rec)
        jogos.append(rec)

    for p in personas:
        rng = master.fork(p["id"], "gen10-digital")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)
        if age < 10:
            continue

        cls = p["classe_social"]
        p_phone = 0.96 if age <= 55 or cls in ("A", "B1", "B2") else 0.72
        if not rng.bernoulli(p_phone):
            continue

        min_dt = max(born + timedelta(days=10 * 365), end - timedelta(days=1460))
        min_dt = min(end, min_dt)

        disp_id = str(uuid5(NAMESPACE_URL, f"disp-{p['id']}-0"))
        so = "iOS Fictício" if cls in ("A", "B1") and rng.bernoulli(0.55) else "Android Simulado"
        rows["dispositivo"].append({
            "id": disp_id,
            "pessoa_id": p["id"],
            "tipo": "celular",
            "modelo": "Smartphone Pro Virtual" if cls in ("A", "B1") else "Smartphone Básico Ficc.",
            "sistema_operacional": so,
            "data_aquisicao": min_dt.isoformat(),
        })

        # Troca de dispositivo para parte dos usuários
        if (end - min_dt).days >= 365 and rng.bernoulli(0.28):
            disp_old_id = str(uuid5(NAMESPACE_URL, f"disp-{p['id']}-old"))
            old_dt = max(born + timedelta(days=10 * 365), min_dt - timedelta(days=365))
            rows["dispositivo"].append({
                "id": disp_old_id,
                "pessoa_id": p["id"],
                "tipo": "celular",
                "modelo": "Smartphone Geração Anterior",
                "sistema_operacional": so,
                "data_aquisicao": old_dt.isoformat(),
            })
            rows["dispositivo_troca_historico"].append({
                "id": str(uuid5(NAMESPACE_URL, f"disptroca-{p['id']}")),
                "pessoa_id": p["id"],
                "dispositivo_antigo_id": disp_old_id,
                "dispositivo_novo_id": disp_id,
                "data": min_dt.isoformat(),
                "motivo": "atualização tecnológica",
            })

        # Aplicativos instalados e histórico de navegação
        for a_idx, (app_nome, app_cat) in enumerate(_APPS[:2]):
            rows["app_instalado"].append({
                "id": str(uuid5(NAMESPACE_URL, f"app-{disp_id}-{a_idx}")),
                "dispositivo_id": disp_id,
                "nome_app": app_nome,
                "data_instalacao": min_dt.isoformat(),
                "categoria": app_cat,
            })

        rows["historico_navegacao_ficticio"].append({
            "id": str(uuid5(NAMESPACE_URL, f"nav-{disp_id}")),
            "dispositivo_id": disp_id,
            "dominio_visitado": str(rng.choice(_DOMINIOS_WEB)),
            "data": f"{end.isoformat()}T19:15:00+00:00",
            "duracao": "00:18:00",
        })

        # Plataforma por faixa etária e seguidores power-law
        if age < 26:
            plat = str(rng.choice(["TikTok Fictício", "InstaVirtual"], weights=[0.55, 0.45]))
        elif age < 45:
            plat = str(rng.choice(["InstaVirtual", "LinkedWork Ficc.", "FaceSimulado"], weights=[0.45, 0.30, 0.25]))
        else:
            plat = str(rng.choice(["FaceSimulado", "WhatsRede Ficc."], weights=[0.65, 0.35]))

        conta_id = str(uuid5(NAMESPACE_URL, f"contadig-{p['id']}"))
        uname = f"user_{p['nome_completo'].split()[0].lower()}_{p['idx']}"
        rows["conta_digital"].append({
            "id": conta_id,
            "pessoa_id": p["id"],
            "plataforma": plat,
            "username_ficticio": uname,
            "data_criacao": min_dt.isoformat(),
        })

        # Força de senha correlacionada com escolaridade
        edu = p.get("education", "fundamental")
        if edu in ("superior", "pos"):
            forca = str(rng.choice(["forte", "media", "fraca"], weights=[0.60, 0.32, 0.08]))
        elif edu == "medio":
            forca = str(rng.choice(["forte", "media", "fraca"], weights=[0.30, 0.50, 0.20]))
        else:
            forca = str(rng.choice(["forte", "media", "fraca"], weights=[0.12, 0.38, 0.50]))

        rows["senha_registro_ficticio"].append({
            "id": str(uuid5(NAMESPACE_URL, f"senha-{conta_id}")),
            "conta_digital_id": conta_id,
            "data_ultima_troca": end.isoformat(),
            "forca_senha": forca,
        })

        # Seguidores power-law (log-normal de cauda longa)
        seguidores = max(10, round(rng.log_normal(5.0, 1.35)))
        perfil_id = str(uuid5(NAMESPACE_URL, f"perfil-{conta_id}"))
        rows["perfil_rede_social"].append({
            "id": perfil_id,
            "conta_digital_id": conta_id,
            "seguidores_ficticios": seguidores,
            "bio_ficticia": f"Perfil fictício em {p.get('cidade_residencia', 'Brasil')}",
        })
        rows["publicacao_rede_social"].append({
            "id": str(uuid5(NAMESPACE_URL, f"pub-{perfil_id}")),
            "perfil_id": perfil_id,
            "data": f"{end.isoformat()}T18:00:00+00:00",
            "tipo_conteudo": str(rng.choice(["foto", "vídeo curto", "texto"])),
            "engajamento_ficticio": max(1, seguidores // 12),
        })

        # Jogos e streaming
        if age <= 40 and rng.bernoulli(0.45):
            jogo = rng.choice(jogos)
            rows["progresso_jogo"].append({
                "id": str(uuid5(NAMESPACE_URL, f"progjogo-{p['id']}")),
                "pessoa_id": p["id"],
                "jogo_id": jogo["id"],
                "horas_jogadas": rng.integer(5, 650),
                "nivel_atual": rng.integer(1, 80),
                "data_ultima_sessao": end.isoformat(),
            })

        if age >= 18 and rng.bernoulli(0.55):
            serv, plano, val_str = rng.choice(_STREAMINGS)
            rows["assinatura_streaming"].append({
                "id": str(uuid5(NAMESPACE_URL, f"stream-{p['id']}")),
                "pessoa_id": p["id"],
                "servico": str(serv),
                "plano": str(plano),
                "data_inicio": min_dt.isoformat(),
                "valor_mensal": float(val_str),
            })

        if p.get("residencia_atual_id") and rng.bernoulli(0.75):
            rows["provedor_internet"].append({
                "id": str(uuid5(NAMESPACE_URL, f"isp-{p['id']}")),
                "residencia_id": p["residencia_atual_id"],
                "operadora": str(rng.choice(["FibraNet Fictícia", "ConectaBrasil Simulado", "UltraWeb Virtual"])),
                "velocidade_contratada": str(rng.choice(["300 Mbps", "500 Mbps", "1 Gbps"])),
            })

    return rows
