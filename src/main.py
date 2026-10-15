from src.data import MENU_CATALOG
from src.services import display_items
from src.services import add_item
from src.validators import get_non_empty_string, get_int_input


def print_menu():
    print("\n" + "_" * 40)
    print("INTELIGENTNA SPIŻARNIA SMART-PANTRY")
    print("_" * 40)
    print("1.Wyświetl zawartość spiżarni")
    print("2.Dodaj nowy produkt")
    print("3.Sprawdzenie ilości produktów")
    print("4.Wypisanie tekstu w terminalu")
    print("5.Wyjście z programu")

    print("_" * 40)

def main():
    running = True
    while running:
        print_menu()
        choice = input("Wybierz opcje [1-4]")
        match choice.strip():
            case "1":
                display_items(MENU_CATALOG)

            case "2":
                print("Dodaj nowy produkt")
                name = get_non_empty_string("Podaj nazwę produktu:")
                exp_date = get_non_empty_string("Podaj datę ważności:")
                quantity = get_non_empty_string("Podaj ilość")

                new_item = {
                    "name": name,
                    "exp_date": exp_date,
                    "quantity": quantity
                }
                add_item(MENU_CATALOG, new_item)
            case "3":
                print("Sprawdzanie ilości produkt")

                max_qty = get_int_input("Pokaż produkty, których ilość jest <= ", min_value=1)
                filtered_list = [item for item in MENU_CATALOG if item["quantity"] <= max_qty]
                low_gty = [item for item in MENU_CATALOG if item["quantity"] == 0]
                display_items(filtered_list)
                print("Uwaga! Następujące produkty sie skonczyly:")
                display_items(low_gty)


            case "4":
                tekst = input("Podaj tekst: ")
                print(tekst)

            case "5" | "q" | "exit":
                print("Zamykanie programu...")
                running = False
            case _:
                print("Nieznana opcja wybierz 1-4")
                running = True


if __name__ == "__main__":
    main()

    