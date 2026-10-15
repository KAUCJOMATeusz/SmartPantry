def display_items(items_list: list):
    if not items_list:
        print("Spiżarnia jest pusta.")
        return

    print("\n" + "_" * 40)
    print(f"| {'ID':<2} | {'Nazwa produktu':<20} | {'Data ważności':<13} | {'Waga w gramach':<18} | {'Ilość':<8} |")



    for item in items_list:
        alert = "[!]" if item['quantity'] < 3 else ""
        print(f"| {item['id']:<2} | {item['name']:<20} | {item['exp_date']:<13} | {item['weight']:<18} | {item['quantity']:}{alert:<8}|")


def add_item(items_list: list, new_item_data: dict):

    if items_list:
        new_id = max(item['id'] for item in items_list) + 1 if items_list else 1

    new_item_data["id"] = new_id

    items_list.append(new_item_data)
    print(f"Pomyślnie dodano produkt: {new_item_data['name']} (przyznane ID: {new_id})")