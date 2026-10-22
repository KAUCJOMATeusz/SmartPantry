import csv
from pathlib import Path
from storage import safe_load_pantry, save_pantry, BASE_DIR
from src.services import display_items
from src.services import add_item
from src.validators import get_non_empty_string, get_int_input
from src.validators import get_float_input


def print_menu():
    print("\n" + "_" * 40)
    print("INTELIGENTNA SPIŻARNIA SMART-PANTRY")
    print("_" * 40)
    print("1.Wyświetl zawartość spiżarni")
    print("2.Dodaj nowy produkt")
    print("3.Sprawdzenie ilości produktów")
    print("4.Eksportuj liste brakujących składników(csv)")
    print("5.Wyjście z programu")

    print("_" * 40)

def main():
    running = True
    while running:
        print_menu()
        choice = input("Wybierz opcje [1-5]")
        match choice.strip():
            case "1":
                display_items(safe_load_pantry)


            case "2":
                print("Dodaj nowy produkt")
                name = get_non_empty_string("Podaj nazwę produktu: ")
                exp_date = get_non_empty_string("Podaj datę ważności: ")
                weight = get_float_input("Podaj masę w gramach: ")
                quantity = get_int_input("Podaj ilość: ")

                new_item = {
                    "id": len(safe_load_pantry) + 1,
                    "name": name,
                    "exp_date": exp_date,
                    "weight": weight,
                    "quantity": quantity
                }
                if add_item(pantry_catalog, new_item):
                    save_pantry(pantry_catalog)
                    print("\n[SUKCES] Pomyślnie dodano i zapisano produkt!\n")

            case "3":
                print("Sprawdzanie ilości produkt")


                json_list = Path.json.load(f)(f"./data/produkt.json")

                print("\n--- SPRAWDDZANIE ILOŚCI PRODUKTÓW ---")
                max_qty = get_int_input("Pokaż produkty, których ilość jest <= ", min_value=0)

                filtered_list = [item for item in pantry_catalog if item["quantity"] <= max_qty]
                low_qty = [item for item in pantry_catalog if item["quantity"] == 0]

                print(f"\nProdukty w ilości <= {max_qty}:")
                display_items(filtered_list)

                print("\nUwaga! Następujące produkty się skończyły (ilość = 0):")
                if low_qty:
                    display_items(low_qty)
                else:
                    print("Brak produktów z wyczerpanym zapasem.")


            case "4":
                print("\n--- EKSPORT BRAKUJĄCYCH SKŁADNIKÓW DO CSV ---")
                # Filtrujemy produkty, których ilość wynosi 0
                missing_items = [item for item in pantry_catalog if item["quantity"] == 0]

                if not missing_items:
                    print("Brak brakujących produktów (wszystko jest na stanie). Eksport pominięty.")
                    continue

                # Tworzymy folder na eksporty, jeśli nie istnieje
                exports_dir = BASE_DIR / "exports"
                exports_dir.mkdir(parents=True, exist_ok=True)
                csv_path = exports_dir / "shopping_list.csv"

                fields = ["id", "name", "exp_date", "weight", "quantity"]

                with open(csv_path, mode="w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
                    writer.writeheader()
                    writer.writerows(missing_items)

                print(f"[SUKCES] Wyeksportowano brakujące produkty do pliku: {csv_path}")
            case "5" | "q" | "exit":
                print("Zamykanie programu...")
                running = False
            case _:
                print("Nieznana opcja wybierz 1-4")
                running = True


if __name__ == "__main__":
    main()


