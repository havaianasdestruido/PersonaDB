"""gen_06_financas — domínio 06: contas bancárias, transações, investimentos e patrimônio.

Implementa TASK-046 de TODO.MD:
- Simulação financeira determinística integrando salário (`gen_05_carreira`),
  herança recebida (`gen_02_genealogia`) e impactos de saúde (`gen_03_saude`).
- Investimentos diferenciados por classe social (`poupanca` D_E, `CDB` C1/C2,
  `fundos` B1/B2, `acoes` A) sempre limitados ao patrimônio total.
- Imóveis e veículos correlacionados com classe social, idade e renda, com
  financiamento imobiliário coerente com `valor_estimado` do imóvel.
- Snapshot de patrimônio estritamente coerente com o saldo das transações,
  investimentos e ativos físicos.
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
    from persona_db.seeds.lookup_data import BANCOS
except ImportError:  # pragma: no cover
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from persona_db.engines.rng import new_rng
    from persona_db.generators.gen_00_pessoa import simulation_today
    from persona_db.seeds.lookup_data import BANCOS

_CORRETORAS = [
    ("SimulaInvest Corretora", "independente"),
    ("Fictícia Valores DTVM", "bancária"),
    ("Horizonte Capital Virtual", "independente"),
    ("Alfa Broker Simulado", "digital"),
]

_MODELOS_VEICULO = [
    "Compacto Urbano 1.0 Fictício",
    "Hatch Econômico 1.4 Simulado",
    "Sedan Executivo 2.0 Virtual",
    "SUV Familiar Turbo Inventado",
    "Picape Cabine Dupla Fictícia",
]

_SEGURADORAS = [
    "Porto Fictício Seguros",
    "SulSimulada Seguradora",
    "Bradesco Virtual Seguros",
    "Aliança Inventada Seguros",
]

_INVEST_BY_CLASS: dict[str, str] = {
    "A": "acoes",
    "B1": "fundos",
    "B2": "fundos",
    "C1": "CDB",
    "C2": "CDB",
    "D_E": "poupanca",
}

_PROPERTY_BASE_BY_CLASS: dict[str, float] = {
    "A": 1_250_000.0,
    "B1": 680_000.0,
    "B2": 420_000.0,
    "C1": 260_000.0,
    "C2": 175_000.0,
    "D_E": 115_000.0,
}


def _birth(p: dict[str, Any]) -> date:
    return date.fromisoformat(p["data_nascimento"])


def _end_date(p: dict[str, Any], today: date) -> date:
    if p.get("data_obito"):
        return min(today, date.fromisoformat(p["data_obito"]))
    return today


def _build_catalogs(rows: dict[str, list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    bancos: list[dict[str, Any]] = []
    for b in BANCOS:
        bid = str(uuid5(NAMESPACE_URL, f"banco-{b['code']}"))
        rec = {"id": bid, "nome": b["name"], "codigo_ficticio": b["code"]}
        rows["banco"].append(rec)
        bancos.append(rec)

    corretoras: list[dict[str, Any]] = []
    for nome, tipo in _CORRETORAS:
        cid = str(uuid5(NAMESPACE_URL, f"corretora-{nome}"))
        rec = {"id": cid, "nome": nome, "tipo": tipo}
        rows["corretora"].append(rec)
        corretoras.append(rec)

    return bancos, corretoras


def generate(
    personas: list[dict[str, Any]],
    seed: int = 7,
    today: date | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Gera todas as tabelas do domínio 06 (Patrimônio & Finanças)."""
    today = today or simulation_today()
    master = new_rng(seed)

    rows: dict[str, list[dict[str, Any]]] = {
        "banco": [],
        "corretora": [],
        "conta_bancaria": [],
        "cartao_credito": [],
        "transacao": [],
        "fatura": [],
        "investimento": [],
        "carteira_investimento": [],
        "imovel": [],
        "imovel_historico": [],
        "veiculo": [],
        "veiculo_historico": [],
        "divida": [],
        "financiamento": [],
        "seguro": [],
        "patrimonio_snapshot": [],
        "imposto": [],
        "declaracao_imposto": [],
    }

    bancos, corretoras = _build_catalogs(rows)

    for p in personas:
        rng = master.fork(p["id"], "gen06-financas")
        born = _birth(p)
        end = _end_date(p, today)
        age = max(0, (end - born).days // 365)

        p["conta_bancaria_id"] = None
        p["imovel_proprio_id"] = None
        p["financiamento_imovel_id"] = None
        p["patrimonio_total"] = 0.0

        if age < 18:
            continue

        cls = p["classe_social"]
        sal_mensal = float(p.get("salario_mensal") or 1800.0)
        heranca_val = float(p.get("heranca_recebida") or 0.0)

        # 1. Conta bancária e cartão de crédito
        banco = rng.choice(bancos)
        conta_id = str(uuid5(NAMESPACE_URL, f"conta-{p['id']}"))
        tipo_conta = str(rng.choice(["corrente", "digital", "poupanca", "salario"], weights=[0.50, 0.30, 0.12, 0.08]))
        rows["conta_bancaria"].append({
            "id": conta_id,
            "pessoa_id": p["id"],
            "banco_id": banco["id"],
            "tipo_conta": tipo_conta,
            "agencia": f"{1000 + (p['idx'] * 7) % 8999:04d}",
            "numero_ficticio": f"{100000 + p['idx'] * 13:07d}-{p['idx'] % 10}",
        })
        p["conta_bancaria_id"] = conta_id

        # Transações mensais representativas (créditos e débitos coerentes com saldo >= 0)
        ref_dt = max(born + timedelta(days=18 * 365), end - timedelta(days=90))
        ref_dt = min(ref_dt, end)

        inflow_1 = round(sal_mensal, 2)
        inflow_2 = round(sal_mensal + heranca_val * 0.1, 2)
        outflow_1 = round(sal_mensal * rng.uniform(0.35, 0.65), 2)
        outflow_2 = round(sal_mensal * rng.uniform(0.15, 0.30), 2)

        tx_entries = [
            ("credito", inflow_1, ref_dt, "Crédito salarial mensal fictício"),
            ("debito", outflow_1, min(end, ref_dt + timedelta(days=5)), "Despesas fixas residenciais e alimentação"),
            ("credito", inflow_2, min(end, ref_dt + timedelta(days=30)), "Receita mensal e rendimentos"),
            ("pix", outflow_2, min(end, ref_dt + timedelta(days=35)), "Pagamentos diversos via PIX"),
        ]
        for t_idx, (ttipo, tval, tdt, tdesc) in enumerate(tx_entries):
            rows["transacao"].append({
                "id": str(uuid5(NAMESPACE_URL, f"tx-{conta_id}-{t_idx}")),
                "conta_id": conta_id,
                "tipo": ttipo,
                "valor": tval,
                "data": f"{tdt.isoformat()}T12:00:00+00:00",
                "descricao": tdesc,
            })

        saldo_conta = round((inflow_1 + inflow_2) - (outflow_1 + outflow_2), 2)

        # Cartão de crédito e fatura
        if rng.bernoulli(0.78):
            cartao_id = str(uuid5(NAMESPACE_URL, f"cartao-{conta_id}"))
            limite = round(sal_mensal * rng.uniform(1.5, 4.0), 2)
            rows["cartao_credito"].append({
                "id": cartao_id,
                "pessoa_id": p["id"],
                "conta_id": conta_id,
                "bandeira": str(rng.choice(["Visa Fictício", "Mastercard Simulado", "Elo Virtual"])),
                "limite": limite,
            })
            status_fat = "atrasado" if p.get("tem_doenca_cronica") and rng.bernoulli(0.25) else "pago"
            rows["fatura"].append({
                "id": str(uuid5(NAMESPACE_URL, f"fatura-{cartao_id}")),
                "cartao_id": cartao_id,
                "mes_referencia": date(end.year, end.month, 1).isoformat(),
                "valor_total": round(min(limite * 0.8, outflow_2), 2),
                "status_pagamento": status_fat,
            })

        # 2. Investimentos por classe social
        p_inv = {"A": 0.90, "B1": 0.75, "B2": 0.58, "C1": 0.40, "C2": 0.25, "D_E": 0.12}.get(cls, 0.30)
        total_investido = 0.0
        if rng.bernoulli(p_inv):
            corretora = rng.choice(corretoras)
            tipo_inv = _INVEST_BY_CLASS.get(cls, "poupanca")
            mult_inv = {"A": 18.0, "B1": 10.0, "B2": 6.0, "C1": 3.5, "C2": 2.0, "D_E": 1.0}.get(cls, 2.0)
            total_investido = round(sal_mensal * mult_inv * rng.uniform(0.6, 1.4) + heranca_val * 0.35, 2)
            rows["investimento"].append({
                "id": str(uuid5(NAMESPACE_URL, f"inv-{p['id']}")),
                "pessoa_id": p["id"],
                "tipo": tipo_inv,
                "valor_aplicado": total_investido,
                "data": ref_dt.isoformat(),
                "corretora_id": corretora["id"],
            })
            rows["carteira_investimento"].append({
                "id": str(uuid5(NAMESPACE_URL, f"cart-{p['id']}")),
                "pessoa_id": p["id"],
                "valor_total": total_investido,
                "data_snapshot": end.isoformat(),
            })

        # 3. Imóvel próprio e financiamento imobiliário
        p_imovel = {"A": 0.85, "B1": 0.72, "B2": 0.58, "C1": 0.46, "C2": 0.34, "D_E": 0.22}.get(cls, 0.35)
        if age >= 26:
            p_imovel = min(0.92, p_imovel + 0.12)
        valor_imovel = 0.0
        if rng.bernoulli(p_imovel):
            imovel_id = str(uuid5(NAMESPACE_URL, f"imovel-{p['id']}"))
            base_imv = _PROPERTY_BASE_BY_CLASS.get(cls, 200_000.0)
            valor_imovel = round(base_imv * rng.uniform(0.8, 1.35), 2)
            tipo_imv = str(rng.choice(["apartamento", "casa", "sobrado"]))
            rows["imovel"].append({
                "id": imovel_id,
                "endereco_id": None,
                "tipo": tipo_imv,
                "valor_estimado": valor_imovel,
                "proprietario_pessoa_id": p["id"],
            })
            p["imovel_proprio_id"] = imovel_id
            compra_dt = max(born + timedelta(days=21 * 365), end - timedelta(days=rng.integer(180, 3650)))
            compra_dt = min(compra_dt, end)
            rows["imovel_historico"].append({
                "id": str(uuid5(NAMESPACE_URL, f"imvhist-{imovel_id}")),
                "imovel_id": imovel_id,
                "evento": "compra",
                "data": compra_dt.isoformat(),
                "valor": valor_imovel,
            })

            # Financiamento imobiliário coerente com o valor do imóvel (entre 30% e 80% do valor)
            if heranca_val < valor_imovel and rng.bernoulli(0.55):
                fin_id = str(uuid5(NAMESPACE_URL, f"fin-imv-{p['id']}"))
                val_fin = round(valor_imovel * rng.uniform(0.35, 0.80), 2)
                rows["financiamento"].append({
                    "id": fin_id,
                    "pessoa_id": p["id"],
                    "tipo": "imovel",
                    "valor_total": val_fin,
                    "parcelas": int(rng.choice([120, 180, 240, 360])),
                    "taxa_juros": round(rng.uniform(7.5, 11.8), 2),
                })
                p["financiamento_imovel_id"] = fin_id

        # 4. Veículo próprio
        p_veic = {"A": 0.88, "B1": 0.78, "B2": 0.65, "C1": 0.48, "C2": 0.30, "D_E": 0.14}.get(cls, 0.35)
        valor_veiculo = 0.0
        if rng.bernoulli(p_veic):
            veic_id = str(uuid5(NAMESPACE_URL, f"veiculo-{p['id']}"))
            ano_fab = max(born.year + 18, min(end.year, end.year - rng.integer(0, 12)))
            valor_veiculo = round(rng.uniform(28_000.0, 145_000.0), 2)
            placa = f"PDB{p['idx'] % 10}{(p['idx'] // 10) % 26 + 65:c}{p['idx'] % 100:02d}"
            # Garante unicidade por índice
            placa = f"F{p['idx']:06d}"
            rows["veiculo"].append({
                "id": veic_id,
                "modelo": str(rng.choice(_MODELOS_VEICULO)),
                "ano": ano_fab,
                "placa_ficticia": placa,
                "proprietario_pessoa_id": p["id"],
            })
            rows["veiculo_historico"].append({
                "id": str(uuid5(NAMESPACE_URL, f"veichist-{veic_id}")),
                "veiculo_id": veic_id,
                "evento": "compra",
                "data": ref_dt.isoformat(),
                "valor": valor_veiculo,
            })

        # 5. Dívidas (maior propensão em caso de doença crônica ou desemprego)
        p_divida = 0.34 if p.get("tem_doenca_cronica") else (0.28 if p.get("desempregado") else 0.14)
        if rng.bernoulli(p_divida):
            rows["divida"].append({
                "id": str(uuid5(NAMESPACE_URL, f"divida-{p['id']}")),
                "pessoa_id": p["id"],
                "credor": banco["nome"],
                "valor": round(sal_mensal * rng.uniform(0.8, 3.5), 2),
                "data_vencimento": (end + timedelta(days=rng.integer(30, 365))).isoformat(),
                "status": str(rng.choice(["em_aberto", "negociada", "paga", "inadimplente"])),
            })

        # 6. Seguros
        if rng.bernoulli(0.42):
            tipo_seg = "veicular" if valor_veiculo > 0 else ("residencial" if valor_imovel > 0 else "vida")
            rows["seguro"].append({
                "id": str(uuid5(NAMESPACE_URL, f"seguro-{p['id']}")),
                "pessoa_id": p["id"],
                "tipo": tipo_seg,
                "seguradora": str(rng.choice(_SEGURADORAS)),
                "valor_cobertura": round(max(50_000.0, valor_imovel or valor_veiculo or 80_000.0), 2),
            })

        # 7. Impostos e Declaração IRPF
        if sal_mensal >= 2400.0:
            ano_ref = end.year - 1
            imp_val = round(sal_mensal * 12 * 0.09, 2)
            rows["imposto"].append({
                "id": str(uuid5(NAMESPACE_URL, f"imp-{p['id']}-{ano_ref}")),
                "pessoa_id": p["id"],
                "tipo": "IRPF",
                "ano_referencia": ano_ref,
                "valor": imp_val,
            })
            rows["declaracao_imposto"].append({
                "id": str(uuid5(NAMESPACE_URL, f"decl-{p['id']}-{ano_ref}")),
                "pessoa_id": p["id"],
                "ano": ano_ref,
                "status": str(rng.choice(["entregue", "restituida", "pendente"], weights=[0.6, 0.35, 0.05])),
                "valor_restituicao_ou_debito": round(imp_val * 0.12, 2),
            })

        # 8. Patrimônio snapshot (estritamente >= total_investido e coerente com saldo + ativos)
        patrimonio_total = round(
            saldo_conta + total_investido + valor_imovel + valor_veiculo + heranca_val,
            2,
        )
        p["patrimonio_total"] = patrimonio_total
        rows["patrimonio_snapshot"].append({
            "id": str(uuid5(NAMESPACE_URL, f"patsnap-{p['id']}")),
            "pessoa_id": p["id"],
            "data": end.isoformat(),
            "valor_total_estimado": patrimonio_total,
        })

    return rows
