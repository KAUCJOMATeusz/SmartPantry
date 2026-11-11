from storage import load_shelf, save_shelf, export_shopping_list
from services import display_items, add_item
from validators import get_non_empty_string, get_int_input, get_float_input
from models import FoodProduct



def print_menu():
    print("\n" + "_" * 50)
    print("INTELIGENTNA SPIŻARNIA SMART-PANTRY")
    print("_" * 50)
    print("1.Wyświetl zawartość spiżarni(Posortowana wg daty)")
    print("2.Dodaj nowy produkt")
    print("3.Sprawdzenie ilości produktów")
    print("4.Eksportuj liste brakujących składników(csv)")
    print("5.Pokaż przeterminowane produkty")
    print("6.Wyjście z programu")

    print("_" * 50)

def main():
    shelf = load_shelf()

    running = True
    while running:
        print_menu()
        choice = input("Wybierz opcje [1-5]")
        match choice.strip():
            case "1":
                all_products = shelf.products
                display_items(all_products)


            case "2":
                print("\n--- DODAJ NOWY PRODUKT ---")
                name = get_non_empty_string("Podaj nazwę produktu: ")
                exp_date = get_non_empty_string("Podaj datę ważności: ")
                weight = get_float_input("Podaj masę w gramach: ")
                quantity = get_int_input("Podaj ilość: ")
                unit = get_non_empty_string("Podaj jednostkę: ")


                try:
                    new_id = shelf.next_id()

                    new_product = FoodProduct(
                        product_id=new_id,
                        name=name,
                        exp_date=exp_date,
                        weight=weight,
                        quantity=quantity,
                        unit=unit,
                        expiry_days=0
                    )

                    if add_item(shelf, new_product):
                        save_shelf(shelf)
                        print("\n[SUKCES] Pomyślnie dodano i zapisano produkt!\n")

                except ValueError as e:
                    print(f"\n[BŁĄD] Nie można dodać produktu: {e}\n")

            case "3":

                print("\n--- SPRAWDZANIE ILOŚCI PRODUKTÓW ---")
                max_qty = get_int_input("Pokaż produkty, których ilość jest mniejsza od ", min_value=0)

                filtered_list = [item for item in shelf.products if item.quantity < max_qty]
                low_qty = [item for item in shelf.products if item.quantity == 0]

                print(f"\nProdukty w ilości mniejszej od {max_qty}:")
                display_items(filtered_list)


                if low_qty:
                    print("\nUwaga! Następujące produkty się skończyły (ilość = 0):")
                    display_items(low_qty)
                else:
                    print("Brak produktów z wyczerpanym zapasem.")


            case "4":
                print("\n--- EKSPORT BRAKUJĄCYCH SKŁADNIKÓW DO CSV ---")

                export = export_shopping_list(shelf)

                if export:
                    print("[SUKCES] Wyeksportowano brakujące produkty do listy zakupów ( exports/shopping_list.csv )")
                else:
                    print("Wszystko jest na stanie, brak brakujących produktów (eksport pominięty)")


            case "5":
                print("\n--- PRODUKTY PRZETERMINOWANE ---")
                expired = shelf.expired_products()
                display_items(expired)


            case "6" | "q" | "exit":
                print("Zamykanie programu...")
                running = False
            case _:
                print("Nieznana opcja wybierz 1-5")
                running = True


if __name__ == "__main__":
    main()


