import json
from pathlib import Path
from datetime import datetime

STORE = Path(__file__).resolve().parents[1] / "approvals.json"


def _read():
    if not STORE.exists():
        return []
    with open(STORE, "r", encoding="utf-8") as f:
        return json.load(f)


def _write(items):
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


def record_decision(client_id, decision, reviewer, comment):
    items = _read()
    rec = {
        "client_id": client_id,
        "decision": decision,
        "reviewer": reviewer or "RM Reviewer",
        "comment": comment or "",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    items.append(rec)
    _write(items)
    return rec


def decisions_for(client_id):
    return [i for i in _read() if i["client_id"] == client_id]
