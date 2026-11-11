import csv
import json, os, tempfile, shutil
from datetime import datetime
from pathlib import Path
from models import PantryShelf
from typing import Any, cast

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_PATH = DATA_DIR / "pantry_stock.json"

EXPORT_DIR = BASE_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_PATH = EXPORT_DIR / "shopping_list.csv"

BACKUP_DIR = DATA_DIR / "backups"

DEFAULT_STOCK = [
    {"product_id": 1,"name": "Makaron spaghetti","quantity": 4, "unit": "szt", "expiry_days": 0, "exp_date": "2027-03-20", "weight": 500},
    {"product_id": 2,"name": "Mleko UHT","quantity": 6, "unit": "szt", "expiry_days": 0, "exp_date": "2026-12-15", "weight": 250},
    {"product_id": 3,"name": "Kawa ziarnista","quantity": 1, "unit": "szt", "expiry_days": 0, "exp_date": "2027-10-28", "weight": 400}
]


def create_backup(max_backups: int = 3):
    if not DATA_PATH.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"pantry_stock_{stamp}.bak"
    shutil.copy2(DATA_PATH, backup_path)

    existing = sorted(BACKUP_DIR.glob("pantry_stock_*.bak"))
    while len(existing) > max_backups:
        oldest = existing.pop(0)
        oldest.unlink(missing_ok=True)
    return backup_path


def atomic_save(items_list: list[dict] | dict):
    create_backup()
    with tempfile.NamedTemporaryFile(
            mode="w",
            dir=DATA_DIR,
            prefix="pantry_stock_TMP",
            suffix=".json",
            delete=False,
            encoding="utf-8",
    ) as tmp:
        json.dump(items_list, tmp, indent=4, ensure_ascii=False)
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_path = Path(tmp.name)
    os.replace(temp_path, DATA_PATH)


def load_default():
    atomic_save(DEFAULT_STOCK)
    return DEFAULT_STOCK


def safe_load_pantry():
    try:
        with open(DATA_PATH, mode="r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return load_default()
    except json.JSONDecodeError:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.move(DATA_PATH, DATA_DIR / f"corrupted_{stamp}.json")

        backups = sorted(BACKUP_DIR.glob("pantry_stock_*.bak"))
        if backups:
            with open(backups[-1], mode="r", encoding="utf-8") as f:
                data = json.load(f)
                atomic_save(data)
            return data


def save_pantry(items_list: list[dict]):
    atomic_save(items_list)


def load_shelf() -> PantryShelf:
    data = safe_load_pantry()
    if isinstance(data, list):
        data = {"shelf_id": 1, "products": data}
    return PantryShelf.from_dict(cast(dict[str, Any], data))


def save_shelf(shelf: PantryShelf) -> None:
    atomic_save(shelf.to_dict())


def export_shopping_list(shelf: PantryShelf) -> int:
    shortages = shelf.generate_shopping_list()

    if not shortages:
        return 0

    csv_headers = ["Lista zakupów"]

    with open(EXPORT_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()

        for item in shortages:
            writer.writerow({"Lista zakupów": item.name})

    return len(shortages)
