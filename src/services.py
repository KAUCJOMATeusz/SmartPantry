from models import FoodProduct

def display_items(items_list: list[FoodProduct]):
    if not items_list:
        print("Spiżarnia jest pusta.")
        return

    print("\n" + "_" * 137)
    print(f"| {'ID':<4} | {'Nazwa produktu':<40} | {'Data ważności':<13} | {'Dni do końca':<20} | {'Pilność':<9} | {'Waga':<14} | {'Ilość':<15} |")
    print("_" * 137)


    for item in items_list:
        alert = "[!]" if item.quantity < 3 else ""
        p_id = str(item.product_id)
        p_name = item.get_display_name()
        p_date = str(item.exp_date)
        p_days = f"{item.expiry_days} dni" if item.expiry_days > 0 else "PRZETERMINOWANY"
        p_score = f"{item.spoilage_urgency_score(item.expiry_days)} pkt"
        p_weight = item.weight
        p_qty = f"{item.quantity}{alert}"

        print(f"| {p_id:<4} | {p_name:<40} | {p_date:<13} | {p_days:<20} |{p_score:<10} | {p_weight:<14} | {p_qty:<15} |")

    print("_" * 137)


