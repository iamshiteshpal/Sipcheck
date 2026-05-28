import datetime
from datetime import date
from collections import Counter

from app.helpers import (
    calc_xirr,
    clean_name,
    next_due_date,
    ordinal,
    to_date,
    to_dict,
)


def process(raw):
    raw = to_dict(raw)
    info = raw.get("investor_info", {})

    result = {
        "investor_name": info.get("name", "Investor"),
        "investor_email": info.get("email", ""),
        "investor_pan": info.get("pan", "—"),
        "statement_date": str(date.today()),
        "total_value": 0.0,
        "total_invested": 0.0,
        "unrealized_pnl": 0.0,
        "realized_pnl": 0.0,
        "alloc_values": {},
        "alloc_pct": {},
        "holdings": [],
        "live_sips": [],
        "dead_sips": [],
        "redeemed": [],
        "recent_redemptions": [],
        "tx_map": {},
        "agg_map": {},
        "duplicate_alerts": [],
    }

    total_val = 0.0
    total_inv = 0.0
    type_map = {}

    for folio in raw.get("folios", []):
        for scheme in folio.get("schemes", []):
            valuation = scheme.get("valuation", {})
            scheme_name = scheme.get("scheme", "Unknown")
            valuation_date = str(valuation.get("date", result["statement_date"]))
            result["statement_date"] = valuation_date

            cost = float(valuation.get("cost", 0.0))
            value = float(valuation.get("value", 0.0))
            units = float(scheme.get("close", 0.0))
            scheme_type = str(scheme.get("type", "EQUITY")).upper()
            category = "Equity Funds" if scheme_type == "EQUITY" else "Debt Funds"

            transactions = scheme.get("transactions", [])
            result["tx_map"][scheme_name] = transactions

            invested = 0.0
            redeemed_amount = 0.0
            for tx in transactions:
                amount = abs(float(tx.get("amount", 0.0)))
                txn_type = str(tx.get("type", "")).upper()
                description = str(tx.get("description", "")).upper()
                is_buy = any(k in txn_type or k in description for k in ["PURCHASE", "REINVEST", "SIP", "STP-IN"])
                is_sell = any(k in txn_type or k in description for k in ["REDEMPTION", "PAYOUT", "WITHDRAWAL", "STP-OUT"])

                if is_buy:
                    invested += amount
                if is_sell:
                    redeemed_amount += amount
                    try:
                        redemption_date = to_date(tx.get("date"))
                        result["recent_redemptions"].append({
                            "date_obj": redemption_date,
                            "Date": redemption_date.strftime("%d %b %Y"),
                            "Scheme": clean_name(scheme_name),
                            "Payout": amount,
                        })
                    except Exception:
                        pass

            if units < 0.001 and invested > 0 and redeemed_amount > 0:
                profit = redeemed_amount - invested
                result["redeemed"].append({
                    "scheme": scheme_name,
                    "invested": invested,
                    "redeemed": redeemed_amount,
                    "profit": profit,
                })
                result["realized_pnl"] += profit
                result["agg_map"][scheme_name] = {"cost": cost, "units": units, "value": value}
                continue

            total_val += value
            total_inv += cost
            type_map[category] = type_map.get(category, 0.0) + value
            result["agg_map"][scheme_name] = {"cost": cost, "units": units, "value": value}

            pnl = value - cost
            xirr_value = calc_xirr(transactions, value, valuation_date)
            cas_nav = float(valuation.get("nav", 0.0))
            if cas_nav == 0.0 and units > 0:
                cas_nav = value / units

            result["holdings"].append({
                "scheme": scheme_name,
                "amfi": scheme.get("amfi"),
                "units": units,
                "invested": cost,
                "value": value,
                "pnl": pnl,
                "xirr": xirr_value,
                "category": category,
                "cas_nav": cas_nav,
                "cas_date": valuation_date,
            })

            sip_keywords = ["SIP", "SYSTEMATIC", "RECURRING", "AUTO", "DEBIT", "E-DEBIT", "ECS", "MANDATE"]
            sip_transactions = [
                t for t in transactions
                if any(k in str(t.get("description", "")).upper() or k in str(t.get("type", "")).upper() for k in sip_keywords)
            ]

            if sip_transactions:
                days = [to_date(t.get("date")).day for t in sip_transactions]
                dom = Counter(days).most_common(1)[0][0] if days else 1

                sorted_sip = sorted(sip_transactions, key=lambda x: to_date(x.get("date")))
                latest_tx = sorted_sip[-1]
                amount_sip = float(latest_tx.get("amount", 0.0))

                if amount_sip > 0:
                    last_date = to_date(latest_tx.get("date"))
                    statement_date_obj = to_date(valuation_date)
                    cutoff = statement_date_obj - datetime.timedelta(days=90)
                    next_due = next_due_date(dom)
                    next_due_label = next_due.strftime("%d %b %Y")
                    next_due_iso = next_due.isoformat()

                    sip_record = {
                        "scheme": scheme_name,
                        "amount": amount_sip,
                        "day_label": ordinal(dom),
                        "last_date": last_date.strftime("%d %b %Y"),
                        "next_date": next_due_label,
                        "next_iso": next_due_iso,
                        "status": "Live" if last_date >= cutoff and units > 0.01 else "Inactive",
                    }

                    if sip_record["status"] == "Live":
                        result["live_sips"].append(sip_record)
                    else:
                        result["dead_sips"].append(sip_record)

    result["total_value"] = total_val
    result["total_invested"] = total_inv
    result["unrealized_pnl"] = total_val - total_inv
    result["alloc_values"] = type_map
    result["alloc_pct"] = {k: (v / total_val) * 100 for k, v in type_map.items()} if total_val else {}

    result["recent_redemptions"] = sorted(
        result["recent_redemptions"], key=lambda x: x["date_obj"], reverse=True
    )

    return result
