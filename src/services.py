from models import FoodProduct, PantryShelf

def display_items(items_list: list[FoodProduct]):
    if not items_list:
        print("Spiżarnia jest pusta.")
        return

    print("\n" + "_" * 105)
    print(f"| {'ID':<4} | {'Nazwa produktu':<20} | {'Data ważności':<13} | {'Dni do końca':<20} | {'Waga':<14} | {'Ilość':<15} |")
    print("_" * 105)


    for item in items_list:
        alert = "[!]" if item.quantity < 3 else ""
        p_id = str(item.product_id)
        p_name = str(item.name)
        p_date = str(item.exp_date)
        p_days = f"{item.expiry_days} dni" if item.expiry_days > 0 else "PRZETERMINOWANY"
        p_weight = item.weight
        p_qty = f"{item.quantity}{alert}"

        print(f"| {p_id:<4} | {p_name:<20} | {p_date:<13} | {p_days:<20} | {p_weight:<14} | {p_qty:<15} |")

    print("_" * 105)


def add_item(shelf: PantryShelf, product: FoodProduct):
    shelf.add_product(product)
    print(f"Pomyślnie dodano produkt: {product.name} (przyznane ID: {product.product_id})")
    return True
