"""val_financas — validador de consistência financeira e patrimonial (TASK-072).

Regras verificadas:
- Soma de transações (`credito` - `debito`) coerente com o saldo e o perfil de dívida.
- Financiamento imobiliário coerente com o valor do imóvel (`0 < valor_total <= imovel.valor_estimado`)
  e taxa de juros em `[0, 500]`.
- Salário registrado acima ou igual ao salário mínimo vigente no ano (`MIN_WAGE_HISTORY`).
- Total de investimentos aplicados não excede o patrimônio total estimado (`patrimonio_snapshot`).
- `patrimonio_snapshot` coerente com histórico de transações, investimentos e ativos.
- Herança recebida somente de pessoa marcada como falecida.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from persona_db.generators.gen_05_carreira import min_wage_for_year

Violation = dict[str, Any]


def _year(value: str | None) -> int:
    if not value:
        return 2026
    return int(value[:4])


def validate_financas(
    dataset: dict[str, list[dict[str, Any]]],
    today: date | None = None,
) -> list[Violation]:
    """Executa todas as verificações de consistência financeira."""
    violations: list[Violation] = []
    people = {p["id"]: p for p in dataset.get("pessoa", []) if "id" in p}
    contratos = {c["id"]: c for c in dataset.get("contrato_trabalho", []) if "id" in c}
    contas_person = {c["id"]: c.get("pessoa_id") for c in dataset.get("conta_bancaria", []) if "id" in c}
    imoveis = {im["id"]: im for im in dataset.get("imovel", []) if "id" in im}
    financiamentos = {f["id"]: f for f in dataset.get("financiamento", []) if "id" in f}

    # 1. Salário >= salário mínimo vigente no período
    for sal in dataset.get("salario", []):
        val = float(sal.get("valor") or 0.0)
        yr = _year(sal.get("data_vigencia"))
        ct = contratos.get(sal.get("contrato_id"))
        tipo_ct = ct.get("tipo_contrato", "CLT") if ct else "CLT"
        floor = min_wage_for_year(yr) * (0.5 if tipo_ct == "estagio" else 1.0)
        if val + 1e-6 < floor:
            violations.append({
                "domain": "financas",
                "rule": "salary_below_minimum_wage",
                "salario_id": sal.get("id"),
                "valor": val,
                "floor": floor,
                "year": yr,
            })

    # 2. Financiamento imobiliário coerente com valor do imóvel e taxa de juros
    for f in dataset.get("financiamento", []):
        vt = float(f.get("valor_total") or 0.0)
        tj = float(f.get("taxa_juros") or 0.0)
        if vt <= 0.0 or tj < 0.0 or tj > 500.0:
            violations.append({
                "domain": "financas",
                "rule": "invalid_financing_parameters",
                "financiamento_id": f.get("id"),
            })

    for fi in dataset.get("financiamento_imobiliario", []):
        im = imoveis.get(fi.get("imovel_id"))
        fin = financiamentos.get(fi.get("financiamento_id"))
        if im is None or fin is None:
            violations.append({
                "domain": "financas",
                "rule": "mortgage_missing_property_or_financing",
                "id": fi.get("id"),
            })
        elif float(fin.get("valor_total") or 0.0) > float(im.get("valor_estimado") or 0.0) + 1e-2:
            violations.append({
                "domain": "financas",
                "rule": "mortgage_exceeds_property_value",
                "financiamento_id": fin.get("id"),
                "imovel_id": im.get("id"),
            })

    # 3. Transações, investimentos e patrimônio líquido por pessoa
    net_tx_by_person: dict[str, float] = {}
    for tx in dataset.get("transacao", []) + dataset.get("transacao_financeira", []):
        pid = contas_person.get(tx.get("conta_id"))
        if not pid:
            continue
        val = float(tx.get("valor") or 0.0)
        sign = 1.0 if tx.get("tipo") in ("credito", "transferencia") else -1.0
        net_tx_by_person[pid] = net_tx_by_person.get(pid, 0.0) + sign * val

    inv_by_person: dict[str, float] = {}
    for inv in dataset.get("investimento", []):
        pid = inv.get("pessoa_id")
        if pid:
            inv_by_person[pid] = inv_by_person.get(pid, 0.0) + float(inv.get("valor_aplicado") or 0.0)

    has_debt_person = {d.get("pessoa_id") for d in dataset.get("divida", []) if d.get("pessoa_id")}
    snap_by_person = {
        s["pessoa_id"]: float(s.get("valor_total_estimado") or 0.0)
        for s in dataset.get("patrimonio_snapshot", [])
        if "pessoa_id" in s
    }

    for pid, net_tx in net_tx_by_person.items():
        if net_tx < -1e-2 and pid not in has_debt_person:
            violations.append({
                "domain": "financas",
                "rule": "negative_balance_without_debt",
                "person_id": pid,
                "net_balance": round(net_tx, 2),
            })

    for pid, inv_total in inv_by_person.items():
        pat = snap_by_person.get(pid, 0.0)
        if inv_total > pat + 1e-2:
            violations.append({
                "domain": "financas",
                "rule": "investments_exceed_net_worth",
                "person_id": pid,
                "investments": round(inv_total, 2),
                "net_worth": round(pat, 2),
            })

    for pid, pat in snap_by_person.items():
        liquid_min = max(0.0, net_tx_by_person.get(pid, 0.0)) + inv_by_person.get(pid, 0.0)
        if pat + 1e-2 < liquid_min:
            violations.append({
                "domain": "financas",
                "rule": "patrimony_inconsistent_with_liquid_assets",
                "person_id": pid,
                "net_worth": round(pat, 2),
                "liquid_min": round(liquid_min, 2),
            })

    # 4. Herança apenas de pessoa falecida
    for h in dataset.get("heranca", []):
        fal = people.get(h.get("pessoa_id_falecido"))
        if fal is None or fal.get("esta_vivo", True):
            violations.append({
                "domain": "financas",
                "rule": "inheritance_from_living_person",
                "heranca_id": h.get("id"),
            })

    return violations
