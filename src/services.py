from models import FoodProduct, PantryShelf

def display_items(items_list: list[FoodProduct]):
    if not items_list:
        print("Spiżarnia jest pusta.")
        return

    print("\n" + "_" * 77)
    print(f"| {'ID':<2} | {'Nazwa produktu':<20} | {'Data ważności':<13} | {'Waga w gramach':<18} | {'Ilość':<8} |")
    print("_" * 77)


    for item in items_list:
        alert = "[!]" if item['quantity'] < 3 else ""
        print(f"| {item.product_id:<2} | {item.name:<20} | {item.exp_date:<13} | {item.weight:<18} | {item.quantity:}{alert:<8}|")
    print("_" * 77)

def add_item(shelf: PantryShelf, product: FoodProduct):
    shelf.add_product(product)
    print(f"Pomyślnie dodano produkt: {product.name} (przyznane ID: {product.product_id})")
    return True
