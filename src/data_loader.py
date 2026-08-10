from pathlib import Path
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / name)


def load_json(name: str):
    with open(DATA_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def load_all():
    return {
        "clients": load_csv("clients.csv"),
        "financials": load_csv("client_financials.csv"),
        "accounts": load_csv("account_behavior.csv"),
        "products": load_csv("product_usage.csv"),
        "covenants": load_csv("covenants.csv"),
        "crm_notes": load_json("crm_notes.json"),
        "market_news": load_json("market_news.json"),
        "documents": load_json("client_documents.json"),
    }
