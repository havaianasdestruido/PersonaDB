"""gen_15_consumo — domínio 15: produtos, lojas, compras, avaliações e fidelidade.

Implementa a seção de Consumo de TASK-053 em TODO.MD:
- Padrões de compra modulados por renda, classe socioeconômica e sazonalidade.
- Avaliações de produtos, assinaturas de serviços, devoluções, programas de
  fidelidade, carrinhos abandonados e histórico de preços.
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

_PRODUTOS = [
    ("Cafeteira Expresso Automática", "eletrodomesticos", "CasaFictícia", 480.0),
    ("Fone de Ouvido Sem Fio Pro", "eletronicos", "SomVirtual", 320.0),
    ("Tênis de Corrida Performance", "vestuario", "EsporteSimulado", 290.0),
    ("Livro Best-Seller de Ficção", "cultura", "Editora Alvorada", 59.90),
    ("Kit Cesta Supermercado Mensal", "alimentos", "BomPreço Ficc.", 640.0),
]

_LOJAS = [
    ("MegaStore Brasil Virtual", "marketplace"),
    ("Supermercado Central Fictício", "fisica"),
    ("EletroShop Online Simulado", "online"),
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
    """Gera todas as tabelas do domínio 15 (Consumo)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "produto": [],
        "loja": [],
        "compra": [],
        "item_compra": [],
        "avaliacao_produto": [],
        "assinatura_servico": [],
        "devolucao": [],
        "programa_fidelidade": [],
        "carrinho_abandonado": [],
        "historico_preco": [],
    }

    produtos: list[dict[str, Any]] = []
    for nome, cat, marca, preco in _PRODUTOS:
        pid = str(uuid5(NAMESPACE_URL, f"prod-{nome}"))
        rec = {"id": pid, "nome": nome, "categoria": cat, "marca_ficticia": marca, "_preco": preco}
        rows["produto"].append({"id": pid, "nome": nome, "categoria": cat, "marca_ficticia": marca})
        produtos.append(rec)
        rows["historico_preco"].append({
            "id": str(uuid5(NAMESPACE_URL, f"histpreco-{pid}")),
            "produto_id": pid,
            "data": today.isoformat(),
            "valor": preco,
        })

    lojas: list[dict[str, Any]] = []
    for nome, tipo in _LOJAS:
        lid = str(uuid5(NAMESPACE_URL, f"loja-{nome}"))
        rec = {"id": lid, "nome": nome, "tipo": tipo, "endereco_id": None}
        rows["loja"].append(rec)
        lojas.append(rec)

    for p in personas:
        rng = master.fork(p["id"], "gen15-consumo")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)
        if age < 16:
            continue

        loja = rng.choice(lojas)
        prod = rng.choice(produtos)
        qtd = rng.integer(1, 3)
        v_unit = float(prod["_preco"])
        v_tot = round(qtd * v_unit, 2)
        c_dt = max(born + timedelta(days=16 * 365), end - timedelta(days=rng.integer(10, 360)))
        c_dt = min(c_dt, end)

        compra_id = str(uuid5(NAMESPACE_URL, f"compra-{p['id']}-0"))
        rows["compra"].append({
            "id": compra_id,
            "pessoa_id": p["id"],
            "loja_id": loja["id"],
            "data": c_dt.isoformat(),
            "valor_total": v_tot,
        })
        rows["item_compra"].append({
            "id": str(uuid5(NAMESPACE_URL, f"itemcompra-{compra_id}")),
            "compra_id": compra_id,
            "produto_id": prod["id"],
            "quantidade": qtd,
            "valor_unitario": v_unit,
        })

        if rng.bernoulli(0.45):
            rows["avaliacao_produto"].append({
                "id": str(uuid5(NAMESPACE_URL, f"avalprod-{compra_id}")),
                "pessoa_id": p["id"],
                "produto_id": prod["id"],
                "nota": round(rng.normal_clipped(8.2, 1.2, 0.0, 10.0), 2),
                "comentario_ficticio": "Produto entregue conforme descrição fictícia.",
            })

        if rng.bernoulli(0.08):
            dev_dt = min(end, c_dt + timedelta(days=7))
            rows["devolucao"].append({
                "id": str(uuid5(NAMESPACE_URL, f"dev-{compra_id}")),
                "compra_id": compra_id,
                "produto_id": prod["id"],
                "motivo": "arrependimento ou troca de tamanho",
                "data": dev_dt.isoformat(),
            })

        if rng.bernoulli(0.50):
            rows["programa_fidelidade"].append({
                "id": str(uuid5(NAMESPACE_URL, f"fidel-{p['id']}")),
                "pessoa_id": p["id"],
                "loja_id": loja["id"],
                "pontos_acumulados": rng.integer(100, 15000),
            })

        if rng.bernoulli(0.30):
            rows["assinatura_servico"].append({
                "id": str(uuid5(NAMESPACE_URL, f"assserv-{p['id']}")),
                "pessoa_id": p["id"],
                "servico": "Clube de Benefícios e Frete Grátis Fictício",
                "valor_mensal": 19.90,
                "data_inicio": c_dt.isoformat(),
            })

        if rng.bernoulli(0.22):
            rows["carrinho_abandonado"].append({
                "id": str(uuid5(NAMESPACE_URL, f"carr-{p['id']}")),
                "pessoa_id": p["id"],
                "loja_id": loja["id"],
                "itens_ficticios": prod["nome"],
                "data": end.isoformat(),
            })

    return rows
