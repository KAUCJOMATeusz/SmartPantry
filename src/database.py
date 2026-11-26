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
    exp_date TEXT NOT NULL,
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
                    p["exp_date"]
                )
                for p in products
            ]

            self._conn.executemany(
                """
                INSERT INTO food_products (shelf_id, name, quantity, unit, exp_date)
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

    def transaction_rollback(self, product_id: int, target_shelf_id: int, new_quantity: float) -> None:
        with self._conn:
            shelf_check = self._conn.execute(
                "SELECT COUNT(*) FROM pantry_shelves WHERE shelf_id = ?;",
                (target_shelf_id,)
            ).fetchone()[0]

            if shelf_check == 0:
                raise ValueError("Docelowa półka nie istnieje w bazie.")

            cursor = self._conn.execute(
                """
                UPDATE food_products 
                SET shelf_id = ?, quantity = ? 
                WHERE product_id = ?;
                """,
                (target_shelf_id, new_quantity, product_id)
            )

            if cursor.rowcount == 0:
                raise ValueError("Nie znaleziono produktu o podanym ID.")