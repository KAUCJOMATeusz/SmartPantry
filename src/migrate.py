import json
import sqlite3
from pathlib import Path
from database import PantryRepository
from models import deserialize_product


def migrate_from_json(conn: sqlite3.Connection, json_path: Path) -> int:
    count = conn.execute("SELECT COUNT(*) FROM pantry_shelves;").fetchone()[0]
    if count > 0 or not json_path.exists():
        return 0

    with open(json_path, mode="r", encoding="utf-8") as f:
        raw_data = json.load(f)

    item_list = raw_data.get("products", []) if isinstance(raw_data, dict) else raw_data
    item_dict = []

    for row in item_list:
        item = deserialize_product(row)
        if item.quantity > 0:
            item_dict.append(item.to_dict())

    if not item_dict:
        return 0


    repo = PantryRepository(conn)
    repo.save_shelf_with_products("Spiżarnia Główna", "Kuchnia", item_dict)

    json_path.rename(json_path.with_suffix(".json.bak"))
    return len(item_dict)