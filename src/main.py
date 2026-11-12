from datetime import datetime
from pathlib import Path
from menager import PantryStockManager
from models import DryProduct, PerishableProduct
from services import display_items
from validators import get_float_input, get_int_input, get_non_empty_string

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "pantry_stock.json"
EXPORT_PATH = BASE_DIR / "exports" / "shopping_list.csv"


def print_menu() -> None:
    print("\n" + "_" * 55)
    print("INTELIGENTNA SPIŻARNIA SMART-PANTRY (OOP)")
    print("_" * 55)
    print("1. Wyświetl zawartość spiżarni (według daty)")
    print("2. Dodaj nowy produkt")
    print("3. Sprawdzenie ilości produktów")
    print("4. Eksportuj listę brakujących składników (csv)")
    print("5. Wyświetl produkty przeterminowane")
    print("6. Wyjście z programu")
    print("_" * 55)


def main() -> None:
    manager = PantryStockManager(DATA_PATH)
    manager.load_stock()
    running = True

    while running:
        print_menu()
        choice = input("Wybierz opcję [1-7]: ").strip()

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
                    manager.save_stock()
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

            case "6" | "q" | "exit":
                print("Zamykanie programu...")
                running = False

            case _:
                print("Nieznana opcja, wybierz 1-7.")


if __name__ == "__main__":
    main()
