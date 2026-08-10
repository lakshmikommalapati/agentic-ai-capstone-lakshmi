# Solution Architecture

## Business objective

Turn fragmented commercial banking relationship data into proactive, explainable relationship actions for an RM.

## Agent workflow

```text
Sample Inputs
  ├─ CRM client profile
  ├─ Financial statements
  ├─ Account behavior
  ├─ Product usage
  ├─ Covenant status
  ├─ Market news
  └─ CRM notes + credit documents
        ↓
Data ingestion tools
        ↓
Signal scanning tools
  ├─ Financial trend scanner
  ├─ Account behavior scanner
  ├─ Covenant checker
  ├─ Market risk scanner
  └─ Product usage gap scanner
        ↓
RAG evidence retrieval over CRM notes and client docs
        ↓
Next-best-action reasoning and opportunity scoring
        ↓
Meeting brief + draft outreach
        ↓
Human approval workflow
        ↓
Approved/rejected audit trail
```

## Agent tools implemented

- `scan_financials`: compares revenue, EBITDA, DSO, leverage, and rating trends.
- `scan_account_behavior`: detects declining balances, delayed payments, and high utilization.
- `check_covenants`: identifies covenant breaches or at-risk status.
- `get_market_news`: pulls industry-specific risk context.
- `SimpleRAGIndex.search`: retrieves relevant CRM notes and documents as evidence.
- `score_opportunities`: produces cross-sell and retention opportunity scoring.
- `call_llm`: drafts compliance-aware email using OpenAI when configured.
- `record_decision`: stores approval/rejection audit trail.

## Explainability design

Every recommendation includes:

1. Alert or opportunity source
2. Data point behind the signal
3. RAG evidence snippet where relevant
4. Recommended next action
5. Human approval step before communication

## Production extension ideas

- Replace CSV/JSON with CRM, core banking, data lake, covenant engine, and news APIs.
- Add a policy guardrail service for compliance checks.
- Add RBAC and maker-checker workflow using enterprise identity.
- Store every input, prompt, output, and approval in an immutable audit log.
- Deploy as a Teams app, CRM side panel, or internal web service.
