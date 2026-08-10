import pandas as pd


def pct_change(first, last):
    if first == 0:
        return 0
    return round(((last - first) / first) * 100, 1)


def scan_financials(financials: pd.DataFrame, client_id: str):
    rows = financials[financials.client_id == client_id].sort_values("period")
    latest = rows.iloc[-1].to_dict()
    previous = rows.iloc[-2].to_dict() if len(rows) > 1 else latest
    revenue_change = pct_change(previous["revenue_mn"], latest["revenue_mn"])
    ebitda_change = pct_change(previous["ebitda_mn"], latest["ebitda_mn"])
    debt_ebitda = round(latest["debt_mn"] / max(latest["ebitda_mn"], 0.1), 2)
    alerts = []
    if revenue_change < -5:
        alerts.append(f"Revenue declined {abs(revenue_change)}% QoQ")
    if ebitda_change < -10:
        alerts.append(f"EBITDA declined {abs(ebitda_change)}% QoQ")
    if latest["dso_days"] > 65:
        alerts.append(f"DSO elevated at {latest['dso_days']} days")
    return {
        "latest": latest,
        "revenue_change_pct": revenue_change,
        "ebitda_change_pct": ebitda_change,
        "debt_to_ebitda": debt_ebitda,
        "alerts": alerts,
    }


def scan_account_behavior(accounts: pd.DataFrame, client_id: str):
    rows = accounts[accounts.client_id == client_id].sort_values("month")
    first = rows.iloc[0]
    last = rows.iloc[-1]
    balance_change = pct_change(first.avg_balance_mn, last.avg_balance_mn)
    alerts = []
    if balance_change < -20:
        alerts.append(f"Average balances dropped {abs(balance_change)}% over three months")
    if int(last.delayed_payments) >= 2:
        alerts.append(f"Delayed payments increased to {int(last.delayed_payments)} in latest month")
    if int(last.credit_utilization_pct) > 85:
        alerts.append(f"Credit utilization high at {int(last.credit_utilization_pct)}%")
    return {
        "latest_month": last.to_dict(),
        "balance_change_pct": balance_change,
        "alerts": alerts,
    }


def check_covenants(covenants: pd.DataFrame, client_id: str):
    rows = covenants[covenants.client_id == client_id]
    alerts = []
    for _, row in rows.iterrows():
        if row.status in ["Breach", "At Risk"]:
            alerts.append(f"{row.covenant_name}: {row.status} (current {row.current_value}, threshold {row.threshold})")
    return {"items": rows.to_dict(orient="records"), "alerts": alerts}


def get_market_news(news, industry: str):
    items = [n for n in news if n["industry"] == industry]
    alerts = []
    for n in items:
        if n["risk_level"] in ["High", "Medium"]:
            alerts.append(f"{n['risk_level']} market risk: {n['headline']}")
    return {"items": items, "alerts": alerts}


def score_opportunities(products: pd.DataFrame, client, financial_signal, account_signal, market_signal):
    p = products[products.client_id == client["client_id"]].iloc[0].to_dict()
    opportunities = []

    def add(product, score, reason):
        opportunities.append({"product": product, "score": min(score, 100), "reason": reason})

    if p["has_fx_hedging"] == "no" and client["industry"] in ["Auto Components", "Textiles"]:
        add("FX hedging", 84, "Client has import/export exposure and does not currently use FX hedging")
    if p["has_cash_management"] == "no" or account_signal["balance_change_pct"] < -20:
        add("Cash management and collections", 78, "Balance trend and receivable pressure indicate need for better liquidity visibility")
    if p["has_treasury_deposits"] == "no" and financial_signal["latest"]["cash_mn"] > 15:
        add("Treasury surplus deposits", 65, "Client holds cash balances that can be optimized")
    if p["has_trade_finance"] == "no" and client["industry"] in ["FMCG", "Textiles"]:
        add("Trade/channel finance", 72, "Growth/working-capital cycle can be supported with structured finance")
    if not opportunities:
        add("Relationship review", 55, "No immediate product gap, focus on retention and service quality")
    return sorted(opportunities, key=lambda x: x["score"], reverse=True)


def classify_priority(alerts, opportunities):
    critical_words = ["Breach", "dropped", "Delayed", "high", "High market"]
    risk_hits = sum(any(w in a for w in critical_words) for a in alerts)
    top_score = opportunities[0]["score"] if opportunities else 0
    if risk_hits >= 3:
        return "Critical", "Retention and risk containment"
    if risk_hits >= 1 and top_score >= 75:
        return "High", "Risk-aware cross-sell"
    if top_score >= 70:
        return "Medium", "Growth opportunity"
    return "Low", "Routine relationship management"
