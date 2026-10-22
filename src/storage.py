import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_PATH = DATA_DIR / "pantry_stock.json"

DEFAULT_STOCK = [
    {"id": 1, "name": "Makaron spaghetti", "exp_date": "2027-03-20", "quantity": 4, "weight": 500},
    {"id": 2, "name": "Mleko UHT",  "exp_date": "2026-12-15", "quantity": 6, "weight": 250},
    {"id": 3, "name": "Kawa ziarnista", "exp_date": "2027-10-28", "quantity": 2, "weight": 480},
]

def safe_load_pantry():
    try:
        with open(DATA_PATH, mode="r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(DATA_PATH, mode="w", encoding="utf-8") as f:
            json.dump(DEFAULT_STOCK, f, indent=4, ensure_ascii=False)
        return DEFAULT_STOCK


def save_pantry(items_list: list, new_item_data: dict):
    with open(DATA_PATH, mode="w", encoding="utf-8") as f:
        json.dump(items_list, f, indent=4, ensure_ascii=False)


