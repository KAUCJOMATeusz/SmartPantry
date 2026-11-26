        import json
        import sqlite3
        import tempfile
        from pathlib import Path

        from database import PantryRepository, get_connection
        from migrate import migrate_from_json


        def test_all() -> None:
            print("=== START AUTOTESTÓW BAZY DANYCH (SMARTPANTRY) ===\n")

            conn = get_connection(":memory:")
            repo = PantryRepository(conn)

            # 1. Poprawność schematu DDL
            tables = [
                dict(r)["name"]
                for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            ]
            assert "pantry_shelves" in tables and "food_products" in tables, f"Brak tabel! Znaleziono: {tables}"
            print("[OK] 1. Poprawność schematu DDL: tabele 'pantry_shelves' i 'food_products' istnieją.")

            # 2. Aktywność kluczy obcych (IntegrityError przy braku rodzica)
            fk_error_caught = False
            try:
                with conn:
                    conn.execute(
                        """INSERT INTO food_products (shelf_id, name, quantity, unit, exp_date)
                           VALUES (9999, 'Mleko', 1.0, 'l', '2026-12-31');"""
                    )
            except sqlite3.IntegrityError:
                fk_error_caught = True
            assert fk_error_caught, "PRAGMA foreign_keys = ON nie działa! Nie rzucono IntegrityError."
            print("[OK] 2. Aktywność kluczy obcych: rzucono sqlite3.IntegrityError dla nieistniejącego shelf_id.")

            # 3. Działanie warstwy Repozytorium (zapis 1:N i odczyt)
            sample_products = [
                {"name": "Makaron", "quantity": 2, "unit": "szt", "exp_date": "2027-03-20"},
                {"name": "Ryż", "quantity": 1.5, "unit": "kg", "exp_date": "2027-08-15"},
            ]
            shelf_id = repo.save_shelf_with_products("Regał Główny", "Spiżarnia", sample_products)

            rows = repo.get_products_for_shelf(shelf_id)
            assert len(rows) == 2, f"Oczekiwano 2 produktów, znaleziono {len(rows)}!"
            assert dict(rows[0])["name"] == "Makaron"
            print("[OK] 3. Działanie warstwy Repozytorium: zapisano agregat 1:N i poprawnie odczytano pozycje.")

            # 4. Integralność kaskadowa (ON DELETE CASCADE)
            with conn:
                conn.execute("DELETE FROM pantry_shelves WHERE shelf_id = ?;", (shelf_id,))
            count_row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM food_products WHERE shelf_id = ?;", (shelf_id,)
            ).fetchone()
            count_after_delete = dict(count_row)["cnt"]
            assert count_after_delete == 0, f"ON DELETE CASCADE nie zadziałało! Pozostało: {count_after_delete}"
            print("[OK] 4. Integralność kaskadowa: usunięcie półki wyczyściło powiązane produkty (COUNT == 0).")

            # 5. Pomyślna migracja danych z pliku JSON do bazy SQLite
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_json = Path(tmp_dir) / "pantry_stock.json"
                tmp_json.write_text(
                    json.dumps([
                        {
                            "product_id": 1,
                            "name": "Kawa ziarnista",
                            "quantity": 1,
                            "unit": "szt",
                            "exp_date": "2027-10-28",
                            "weight": 400,
                        }
                    ]),
                    encoding="utf-8",
                )
                migrated_count = migrate_from_json(conn, tmp_json)
                assert migrated_count >= 1, "Skrypt migracyjny nie przeniósł żadnego rekordu z JSON!"
            print(f"[OK] 5. Pomyślna migracja danych: przeniesiono {migrated_count} rekord(y) z JSON do SQLite.")

            conn.close()
            print("\n=== WSZYSTKIE 5 PUNKTÓW KONTROLNYCH ZALICZONE! ===")


        if __name__ == "__main__":
            test_all()
