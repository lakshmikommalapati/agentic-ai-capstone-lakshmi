# Commercial Banking Relationship Manager Copilot

Agentic capstone project for relationship managers. It scans fragmented commercial banking data and produces explainable next-best-actions, meeting briefs, early warning alerts, cross-sell suggestions, retention actions, and draft client outreach with a human approval workflow.

## What this demo shows

- CRM and client profile integration from sample CSV/JSON files
- Account behavior monitoring: balances, payments, utilization, product usage
- Covenant stress detection and early warning signals
- Market/news risk ingestion from a sample news feed
- Lightweight RAG over client documents and CRM notes using TF-IDF retrieval
- Opportunity scoring and next-best-action reasoning
- Compliance-aware outreach drafting using OpenAI when an API key is available, with deterministic fallback when not
- Human-in-the-loop approval before any client email can be marked as ready to send
- Browser-based demo page for presenting to your team lead

## Folder structure

```text
capstone_ey/
  app.py                         # Flask web app
  requirements.txt               # Python dependencies
  .env.example                   # API-key template
  data/                          # Sample input data
  src/                           # Agent tools and orchestration
  templates/                     # HTML pages
  static/                        # CSS
```

## Setup

```bash
cd capstone_ey
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env` and paste your key:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
USE_OPENAI=true
```

If you do not want to call OpenAI during the demo, set:

```text
USE_OPENAI=false
```

## Run the web demo

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Suggested demo flow for your team lead

1. Open the dashboard and explain that each row is a commercial banking client.
2. Click **Run Agent Scan** for each client.
3. Show the generated meeting brief, alerts, evidence snippets, product opportunity score, and next-best-actions.
4. Show the drafted outreach email.
5. Click **Approve** or **Reject**. Emphasize that no communication is sent without human approval.
6. Open `data/` to show the sample inputs and explain how the same schema can map to real CRM and core-banking feeds.

## Capstone mapping

- Client financials: `data/client_financials.csv`
- Account behavior: `data/account_behavior.csv`
- Product usage: `data/product_usage.csv`
- Covenant status: `data/covenants.csv`
- Market news: `data/market_news.json`
- CRM notes and client documents: `data/crm_notes.json`, `data/client_documents.json`
- Next-best-action agent: `src/agent.py`
- Agent tools: `src/tools.py`
- RAG retrieval: `src/rag.py`
- Human approval: `src/approval_store.py`

## Important note

This is a capstone demo using synthetic sample data. It is not a production banking system. In production, add identity controls, audit logs, model risk governance, data lineage, PII masking, policy checks, secure secrets, integration with CRM/core banking APIs, and maker-checker approval controls.
