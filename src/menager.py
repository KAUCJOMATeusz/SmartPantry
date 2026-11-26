import csv
import sqlite3
from pathlib import Path
from database import PantryRepository
from models import FoodProduct, deserialize_product


class PantryStockManager:

    def __init__(self, conn: sqlite3.Connection, default_shelf_id: int = 1) -> None:
        self._conn = conn
        self._repo = PantryRepository(conn)
        self.default_shelf_id = default_shelf_id

    @property
    def products(self) -> list[FoodProduct]:
        rows = self._conn.execute("SELECT * FROM food_products;").fetchall()
        return [deserialize_product(dict(r)) for r in rows]

    def next_id(self) -> int:
        row = self._conn.execute("SELECT MAX(product_id) AS max_id FROM food_products;").fetchone()
        max_id = dict(row)["max_id"] if row else None
        return (max_id or 0) + 1

    def add_product(self, product: FoodProduct) -> None:
        if not isinstance(product, FoodProduct):
            raise TypeError("Spiżarnia przyjmuje wyłącznie obiekty dziedziczące po FoodProduct.")

        shelves = self._repo.get_all_shelves()
        if not shelves:
            shelf_id = self._repo.save_shelf_with_products("Spiżarnia Główna", "Kuchnia", [])
        else:
            shelf_id = dict(shelves[0])["shelf_id"]

        with self._conn:
            self._conn.execute(
                """
                INSERT INTO food_products (
                    shelf_id, name, quantity, unit, exp_date, 
                    type, weight, storage_temp, max_humidity
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    shelf_id,
                    product.name,
                    product.quantity,
                    product.unit,
                    product.exp_date,
                    product.type,
                    product.weight,
                    product.storage_temp,
                    product.max_humidity,
                ),
            )

    def get_priority_list(self) -> list[FoodProduct]:
        return sorted(
            self.products,
            key=lambda p: p.spoilage_urgency_score(p.expiry_days),
            reverse=True,
        )

    def export_shopping_list(self, csv_path: Path) -> int:
        missing = [p for p in self.products if p.quantity == 0]

        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Lista brakujących produktów"])
            for p in missing:
                writer.writerow([p.name])
        return len(missing)
