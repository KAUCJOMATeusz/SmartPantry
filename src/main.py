from datetime import datetime
from fileinput import close
from pathlib import Path
from menager import PantryStockManager
from models import DryProduct, PerishableProduct
from services import display_items
from validators import get_float_input, get_int_input, get_non_empty_string
from database import get_connection
from migrate import migrate_from_json

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "pantry_stock.json"
DB_PATH = BASE_DIR / "data" / "smartpantry.db"
EXPORT_PATH = BASE_DIR / "exports" / "shopping_list.csv"


def print_menu() -> None:
    print("\n" + "_" * 55)
    print("INTELIGENTNA SPIŻARNIA SMART-PANTRY")
    print("_" * 55)
    print("1. Wyświetl zawartość spiżarni (według daty)")
    print("2. Dodaj nowy produkt")
    print("3. Sprawdzenie ilości produktów")
    print("4. Eksportuj listę brakujących składników (csv)")
    print("5. Wyświetl produkty przeterminowane")
    print("6. Wyszukaj produkty (filtr wielokryterialny)")
    print("7. Raport obłożenia półek")
    print("8. Przenieś produkty między półkami")
    print("9. Dodawanie półki")
    print("10. Wyjście z programu ['9' 'q' 'exit']")
    print("_" * 55)


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(str(DB_PATH))
    manager = PantryStockManager(conn)
    migrated_count = migrate_from_json(conn, DATA_PATH)
    if migrated_count > 0:
        print(f"[INFO] Zmigrowano {migrated_count} produktów z pliku JSON do bazy danych.")

    running = True

    while running:
        print_menu()
        choice = input("Wybierz opcję [1-9]: ").strip()

        match choice:
            case "1":
                products = manager.products
                products.sort()
                display_items(products)


            case "2":
                print("\n--- DODAJ NOWY PRODUKT ---")
                print("Wybierz kategorię: [1] Świeży / Nabiał (chłodnia)  |  [2] Sypki / Trwały")
                cat_choice = input("Kategoria [1-2]: ").strip()

                name = get_non_empty_string("Podaj nazwę produktu: ")
                while True:
                    exp_date = get_non_empty_string("Podaj datę ważności (RRRR-MM-DD): ")
                    try:
                        datetime.strptime(exp_date.strip(), "%Y-%m-%d")
                        break
                    except ValueError:
                        print("[!] Niepoprawny format daty! Użyj RRRR-MM-DD.")

                weight = get_float_input("Podaj masę/wagę: ")
                quantity = get_int_input("Podaj ilość: ")
                unit = get_non_empty_string("Podaj jednostkę (g, kg, ml, l, szt): ")

                try:
                    new_id = manager.next_id()
                    if cat_choice == "1":
                        temp = get_float_input("Podaj temperaturę przechowywania (°C, max 4.0): ")
                        product = PerishableProduct(
                            product_id=new_id,
                            name=name,
                            quantity=quantity,
                            unit=unit,
                            exp_date=exp_date,
                            weight=weight,
                            storage_temp=temp,
                        )
                    elif cat_choice == "2":
                        humidity = get_int_input("Podaj max wilgotność (0-100%): ")
                        product = DryProduct(
                            product_id=new_id,
                            name=name,
                            quantity=quantity,
                            unit=unit,
                            exp_date=exp_date,
                            weight=weight,
                            max_humidity=humidity,
                        )
                    else:
                        print("[!] Nieznana kategoria produktu.")
                        continue

                    manager.add_product(product)
                    print(f"\n[SUKCES] Dodano produkt '{product.name}' (ID: {product.product_id})!\n")

                except ValueError as e:
                    print(f"\n[BŁĄD NIEZMIENNIKA] Nie można dodać produktu: {e}\n")

            case "3":
                max_qty = get_int_input("Pokaż produkty, których ilość jest mniejsza od: ", min_value=0)
                filtered = [p for p in manager.products if p.quantity < max_qty]
                display_items(filtered)

            case "4":
                count = manager.export_shopping_list(EXPORT_PATH)
                if count > 0:
                    print(f"[SUKCES] Wyeksportowano {count} brakujących produktów do {EXPORT_PATH}")
                else:
                    print("Wszystko jest na stanie, brak brakujących produktów.")

            case "5":
                print("\n--- PRODUKTY PRZETERMINOWANE ---")
                display_items(manager.get_expired_products())

            case "6":
                print("\n--- WYSZUKIWANIE WIELOPARAMETROWE ---")
                print("(Jeśli chcesz aby dany parametr był dowolny naciśnij przy nim enter")
                phrase = input("Nazwa: ").strip()
                unit_in = input("Jednostka [g, kg, ml, l, szt]: ").strip() or None
                max_date = input("Data ważności do RRRR-MM-DD: ").strip() or None
                sort_col = input("Sortuj po [product_id, name, quantity, weight] (domyślnie: exp_date): ").strip() or "exp_date"

                try:
                    results = manager._repo.search_products(
                        phrase=phrase,
                        unit=unit_in,
                        max_exp_date=max_date,
                        sort_by=sort_col,
                    )
                    if not results:
                        print("Brak produktów spełniających kryteria.")
                    for r in results:
                        print(
                            f"[{r['product_id']}] {r['name']} | {r['quantity']} {r['unit']} | ważność: {r['exp_date']}")
                except ValueError as e:
                    print(f"[BŁĄD WALIDACJI] {e}")

            case "7":
                print("\n--- RAPORT OBŁOŻENIA PÓŁEK ---")
                min_qty = get_float_input("Minimalna łączna ilość na półce (0 = wszystkie): ", min_value=0.0)
                report = manager._repo.get_shelves_occupancy_report(min_total_quantity=min_qty)
                if not report:
                    print("Brak półek spełniających kryterium.")
                for row in report:
                    print(
                        f"Półka #{row['shelf_id']} '{row['shelf_name']}': "
                        f"{row['products_count']} prod. | łączna ilość: {row['total_quantity']}"
                    )

            case "8":
                print("\n--- PRZENIEŚ PRODUKT NA INNĄ PÓŁKĘ ---")
                prod_id = get_int_input("Podaj ID produktu: ", min_value=1)
                target_id = get_int_input("Podaj ID półki docelowej: ", min_value=1)
                qty = get_float_input("Podaj ilość do przeniesienia: ", min_value=0.01)
                try:
                    manager._repo.transaction_rollback(prod_id, target_id, qty)
                    print("[SUKCES] Produkt przeniesiony.")
                except Exception as e:
                    print(f"[ROLLBACK / BŁĄD] Operacja wycofana: {e}")


            case "9":
                print("\n--- DODAJ NOWĄ PÓŁKĘ ---")
                s_name = get_non_empty_string("Nazwa półki: ")
                s_loc = get_non_empty_string("Lokalizacja: ")
                new_shelf_id = manager._repo.save_shelf_with_products(s_name, s_loc, [])
                print(f"[SUKCES] Utworzono półkę '{s_name}' o ID: {new_shelf_id}")\

            case "10" | "q" | "exit":

                conn.close()

            case _:
                print("Nieznana opcja, wybierz 1-7.")


if __name__ == "__main__":
    main()
