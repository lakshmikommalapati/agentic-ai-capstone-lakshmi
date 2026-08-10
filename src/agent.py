import json
from src.data_loader import load_all
from src.rag import build_rag_index
from src.tools import (
    scan_financials,
    scan_account_behavior,
    check_covenants,
    get_market_news,
    score_opportunities,
    classify_priority,
)
from src.llm import call_llm


class RelationshipManagerCopilot:
    def __init__(self):
        self.data = load_all()
        self.rag = build_rag_index(self.data["crm_notes"], self.data["documents"])

    def list_clients(self):
        return self.data["clients"].to_dict(orient="records")

    def run_scan(self, client_id: str):
        clients = self.data["clients"]
        client = clients[clients.client_id == client_id].iloc[0].to_dict()
        financial = scan_financials(self.data["financials"], client_id)
        account = scan_account_behavior(self.data["accounts"], client_id)
        covenant = check_covenants(self.data["covenants"], client_id)
        market = get_market_news(self.data["market_news"], client["industry"])
        evidence = self.rag.search(
            "risk opportunity covenant receivables balances product cross sell client meeting",
            client_id=client_id,
            top_k=4,
        )
        opportunities = score_opportunities(self.data["products"], client, financial, account, market)
        all_alerts = financial["alerts"] + account["alerts"] + covenant["alerts"] + market["alerts"]
        priority, action_theme = classify_priority(all_alerts, opportunities)
        next_actions = self._next_actions(priority, action_theme, opportunities, all_alerts)
        brief = self._meeting_brief(client, financial, account, covenant, market, evidence, opportunities, next_actions, priority)
        email = self._draft_email(client, priority, opportunities, all_alerts, next_actions)
        return {
            "client": client,
            "priority": priority,
            "action_theme": action_theme,
            "alerts": all_alerts,
            "financial": financial,
            "account": account,
            "covenant": covenant,
            "market": market,
            "evidence": evidence,
            "opportunities": opportunities,
            "next_actions": next_actions,
            "meeting_brief": brief,
            "draft_email": email,
        }

    def _next_actions(self, priority, action_theme, opportunities, alerts):
        actions = []
        if priority == "Critical":
            actions.append("Schedule urgent portfolio review with credit/risk team before proposing new exposure.")
            actions.append("Ask client for updated receivables ageing, collections plan, and covenant cure milestones.")
        if alerts:
            actions.append("Discuss early warning signals transparently and document agreed mitigants in CRM.")
        if opportunities:
            actions.append(f"Position {opportunities[0]['product']} because: {opportunities[0]['reason']}.")
        actions.append("Prepare follow-up email for RM approval only; do not auto-send client communication.")
        return actions

    def _meeting_brief(self, client, financial, account, covenant, market, evidence, opportunities, next_actions, priority):
        lines = [
            f"Client: {client['client_name']} ({client['industry']})",
            f"Priority: {priority}",
            f"Financial trend: revenue {financial['revenue_change_pct']}% QoQ, EBITDA {financial['ebitda_change_pct']}% QoQ, Debt/EBITDA {financial['debt_to_ebitda']}x.",
            f"Account behavior: average balance change {account['balance_change_pct']}%, latest utilization {account['latest_month']['credit_utilization_pct']}%.",
            "Key covenant position: " + ("; ".join(covenant['alerts']) if covenant['alerts'] else "All monitored covenants pass."),
            "Market context: " + (market['items'][0]['summary'] if market['items'] else "No market item available."),
            "Top opportunity: " + f"{opportunities[0]['product']} ({opportunities[0]['score']}/100) - {opportunities[0]['reason']}",
            "Suggested next actions: " + " ".join(next_actions),
            "Evidence used: " + " | ".join([f"{e['source']}: {e['text']}" for e in evidence]),
        ]
        return "\n".join(lines)

    def _draft_email(self, client, priority, opportunities, alerts, next_actions):
        system_prompt = (
            "You are a compliance-aware commercial banking relationship manager assistant. "
            "Draft concise client outreach. Do not promise credit approval, pricing, or guarantees. "
            "Suggest a discussion and mention that the RM will review details."
        )
        user_prompt = json.dumps({
            "client_name": client["client_name"],
            "contact": client["primary_contact"],
            "priority": priority,
            "top_opportunity": opportunities[0] if opportunities else None,
            "alerts_to_handle_carefully": alerts[:3],
            "next_actions": next_actions,
        }, indent=2)
        llm_text = call_llm(system_prompt, user_prompt)
        if llm_text and not llm_text.startswith("LLM unavailable"):
            return llm_text
        return (
            f"Subject: Follow-up discussion on your banking requirements\n\n"
            f"Dear {client['primary_contact']},\n\n"
            f"I hope you are doing well. Based on our latest relationship review for {client['client_name']}, "
            f"I would like to schedule a short discussion to understand your current priorities and explore whether "
            f"{opportunities[0]['product'] if opportunities else 'our banking solutions'} could support your plans.\n\n"
            "We can also review recent operating trends and agree on any information needed for a complete assessment. "
            "This note is only to propose a discussion and does not represent a credit approval or commitment.\n\n"
            "Regards,\nLakshmi Kommalapati"
        )
