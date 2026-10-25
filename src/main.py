from storage import safe_load_pantry, save_pantry, export_shopping_list
from services import display_items, add_item
from validators import get_non_empty_string, get_int_input, get_float_input



def print_menu():
    print("\n" + "_" * 50)
    print("INTELIGENTNA SPIŻARNIA SMART-PANTRY")
    print("_" * 50)
    print("1.Wyświetl zawartość spiżarni")
    print("2.Dodaj nowy produkt")
    print("3.Sprawdzenie ilości produktów")
    print("4.Eksportuj liste brakujących składników(csv)")
    print("5.Wyjście z programu")

    print("_" * 50)

def main():
    running = True
    while running:
        print_menu()
        choice = input("Wybierz opcje [1-5]")
        match choice.strip():
            case "1":
                display_items(safe_load_pantry())


            case "2":
                print("\n--- DODAJ NOWY PRODUKT ---")
                name = get_non_empty_string("Podaj nazwę produktu: ")
                exp_date = get_non_empty_string("Podaj datę ważności: ")
                weight = get_float_input("Podaj masę w gramach: ")
                quantity = get_int_input("Podaj ilość: ")

                new_item = {
                    "name": name,
                    "exp_date": exp_date,
                    "weight": weight,
                    "quantity": quantity
                }
                items = safe_load_pantry()
                if add_item(items, new_item):
                    save_pantry(items)
                    print("\n[SUKCES] Pomyślnie dodano i zapisano produkt!\n")

            case "3":

                print("\n--- SPRAWDZANIE ILOŚCI PRODUKTÓW ---")
                max_qty = get_int_input("Pokaż produkty, których ilość jest mniejsza od ", min_value=0)

                filtered_list = [item for item in safe_load_pantry() if item["quantity"] < max_qty]
                low_qty = [item for item in safe_load_pantry() if item["quantity"] == 0]

                print(f"\nProdukty w ilości mniejszej od {max_qty}:")
                display_items(filtered_list)


                if low_qty:
                    print("\nUwaga! Następujące produkty się skończyły (ilość = 0):")
                    display_items(low_qty)
                else:
                    print("Brak produktów z wyczerpanym zapasem.")


            case "4":
                print("\n--- EKSPORT BRAKUJĄCYCH SKŁADNIKÓW DO CSV ---")

                export = export_shopping_list(safe_load_pantry())

                if export:
                    print("[SUKCES] Wyeksportowano brakujące produkty do listy zakupów ( exports/shopping_list.csv )")
                else:
                    print("Wszystko jest na stanie, brak brakujących produktów (eksport pominięty)")



            case "5" | "q" | "exit":
                print("Zamykanie programu...")
                running = False
            case _:
                print("Nieznana opcja wybierz 1-5")
                running = True


if __name__ == "__main__":
    main()


