import sqlite3
from typing import List, Dict, Any

DB_PATH = "smartpantry.db"
JSON_PATH = "pantry.json"

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
    quantity REAL NOT NULL CHECK (quantity > 0.0),
    unit TEXT NOT NULL CHECK (unit IN ('g', 'kg', 'ml', 'l', 'szt')),
    expiry_date TEXT NOT NULL,
    FOREIGN KEY (shelf_id) REFERENCES pantry_shelves(shelf_id) ON DELETE CASCADE
);
"""

class PantryRepository:
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
            shelf_id: int = cur.lastrowid

            payload = [
                (
                    shelf_id,
                    p["name"],
                    p["quantity"],
                    p["unit"],
                    p["expiry_date"]
                )
                for p in products
            ]

            self._conn.executemany(
                """
                INSERT INTO food_products (shelf_id, name, quantity, unit, expiry_date)
                VALUES (?, ?, ?, ?, ?);
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



