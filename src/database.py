import sqlite3
from typing import List, Dict, Any

DB_PATH = "data/smartpantry.db"

ALLOWED_PRODUCT_SORT_COLS = {"product_id", "name", "quantity", "exp_date", "weight"}


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


DDL_SHELVES = """
CREATE TABLE IF NOT EXISTS pantry_shelves (
    shelf_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shelf_name TEXT NOT NULL,
    location TEXT NOT NULL
);
"""

DDL_PRODUCTS = """
CREATE TABLE IF NOT EXISTS food_products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    shelf_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    quantity REAL NOT NULL CHECK (quantity > 0),
    unit TEXT NOT NULL CHECK (unit IN ('g', 'kg', 'ml', 'l', 'szt')),
    exp_date TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'dry',
    weight REAL NOT NULL DEFAULT 0.0,
    storage_temp REAL,
    max_humidity INTEGER,
    FOREIGN KEY (shelf_id) REFERENCES pantry_shelves(shelf_id) ON DELETE CASCADE
);
"""

class PantryRepository:
    ALLOWED_SORT_COLS = {"product_id", "name", "quantity", "unit", "exp_date"}

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._create_tables()

    def _create_tables(self) -> None:
        with self._conn:
            self._conn.execute(DDL_SHELVES)
            self._conn.execute(DDL_PRODUCTS)

    def save_shelf_with_products(self, shelf_name: str, location: str, products: List[Dict[str, Any]]) -> int:
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO pantry_shelves (shelf_name, location) VALUES (?, ?);",
                (shelf_name, location)
            )
            shelf_id: int = int(cur.lastrowid or 0)

            payload = [
                (
                    shelf_id,
                    p["name"],
                    p["quantity"],
                    p["unit"],
                    p["exp_date"],
                    p.get("type", "dry"),
                    p.get("weight", 0.0),
                    p.get("storage_temp"),
                    p.get("max_humidity"),
                )
                for p in products
            ]

            self._conn.executemany(
                """
                                INSERT INTO food_products (
                                    shelf_id, name, quantity, unit, exp_date,
                                    type, weight, storage_temp, max_humidity
                                )
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                                """,
                payload
            )
            return shelf_id

    def get_all_shelves(self) -> List[sqlite3.Row]:
        cursor = self._conn.execute("SELECT * FROM pantry_shelves;")
        return cursor.fetchall()

    def get_products_for_shelf(self, shelf_id: int) -> List[sqlite3.Row]:
        cursor = self._conn.execute(
            "SELECT * FROM food_products WHERE shelf_id = ?;",
            (shelf_id,)
        )
        return cursor.fetchall()

    def search_products (
            self,
            phrase: str,
            unit: str | None = None,
            max_exp_date: str | None = None,
            sort_by: str = "exp_date",
    ) -> List[Dict[str, Any]]:
        if sort_by not in ALLOWED_PRODUCT_SORT_COLS:
            raise ValueError("Niedozwolona kolumna sortowania: {sort_by}")

        sql = (
            "SELECT product_id, shelf_id, name, quantity, unit, exp_date, type, weight "
            "FROM food_products "
            "WHERE name LIKE :pattern "
            "AND (:unit IS NULL OR unit = :unit) "
            "AND (:max_exp_date IS NULL OR exp_date <= :max_exp_date) "
            f"ORDER BY {sort_by} ASC;"
        )
        params = {
            "pattern": f"%{phrase}%",
            "unit": unit,
            "max_exp_date": max_exp_date,
        }
        rows = self._conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


    def get_shelves_occupancy_report(self, min_total_quantity: float = 0.0) -> List[Dict[str, Any]]:
        sql = """
            SELECT 
                s.shelf_id,
                s.shelf_name,
                COUNT(p.product_id) AS products_count,
                COALESCE(SUM(p.quantity), 0.0) AS total_quantity
            FROM pantry_shelves AS s
            LEFT JOIN food_products AS p ON s.shelf_id = p.shelf_id
            GROUP BY s.shelf_id, s.shelf_name
            HAVING total_quantity >= ?
            ORDER BY total_quantity DESC;
        """
        rows = self._conn.execute(sql, (min_total_quantity,)).fetchall()
        return [dict(r) for r in rows]



    def get_expired_summary_report(self, max_date: str) -> List[Dict[str, Any]]:
        sql = """
            SELECT 
                COALESCE(s.shelf_name, 'Brak półki') AS shelf_name,
                COUNT(p.product_id) AS expired_count,
                COALESCE(SUM(p.quantity), 0.0) AS expired_quantity
            FROM food_products AS p
            LEFT JOIN pantry_shelves AS s ON p.shelf_id = s.shelf_id
            WHERE p.exp_date <= ?
            GROUP BY s.shelf_id, s.shelf_name
            HAVING expired_count > 0
            ORDER BY expired_count DESC;
        """
        rows = self._conn.execute(sql, (max_date,)).fetchall()
        return [dict(r) for r in rows]

