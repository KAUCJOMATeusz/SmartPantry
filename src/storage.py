import csv
import json, os, tempfile, shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_PATH = DATA_DIR / "pantry_stock.json"

EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_PATH = EXPORT_DIR / "shopping_list.csv"

BACKUP_DIR = DATA_DIR /     "backups"

DEFAULT_STOCK = [
    {"id": 1, "name": "Makaron spaghetti", "exp_date": "2027-03-20", "quantity": 4, "weight": 500},
    {"id": 2, "name": "Mleko UHT", "exp_date": "2026-12-15", "quantity": 6, "weight": 250},
    {"id": 3, "name": "Kawa ziarnista", "exp_date": "2027-10-28", "quantity": 1, "weight": 480},
]
def create_backup(max_backups: int = 3):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    BACKUP_PATH = BACKUP_DIR / f"pantry_stock_{stamp}.bak"
    shutil.copy2(DATA_PATH, BACKUP_PATH)

    existing = sorted(BACKUP_DIR.glob("pantry_stock_*.bak"))
    while len(existing) > max_backups:
        oldest = existing.pop(0)
        oldest.unlink(missing_ok=True)
    return BACKUP_PATH

def atomic_save(items_list: list[dict]):
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir= DATA_DIR,
        prefix="pantry_stock_TMP",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        json.dump(items_list, tmp, indent=4, ensure_ascii=False)
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_path = Path(tmp.name)
        os.rename(temp_path, DATA_PATH)


def safe_load_pantry():
    try:
        with open(DATA_PATH, mode="r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(DATA_PATH, mode="w", encoding="utf-8") as f:
            json.dump(DEFAULT_STOCK, f, indent=4, ensure_ascii=False)
        return DEFAULT_STOCK


def save_pantry(items_list: list[dict]):
    with open(DATA_PATH, mode="w", encoding="utf-8") as f:
        json.dump(items_list, f, indent=8, ensure_ascii=False)


def export_shopping_list(items_list: list[dict]) -> int:
    shortages = [i for i in items_list if i["quantity"] ==  0]

    if not shortages:
        return 0

    csv_headers = ["Lista zakupów"]

    with open(EXPORT_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()

        for item in shortages:
            writer.writerow({"Lista zakupów": item["name"]})

    return len(shortages)