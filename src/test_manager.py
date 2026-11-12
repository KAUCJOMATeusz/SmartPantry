from pathlib import Path
from menager import  PantryStockManager
from models import DryProduct, FoodProduct, PerishableProduct


def test_blokada_ABC() -> None:
    try:
        FoodProduct(1, "Test", 1, "szt", 5)  # type: ignore
        assert False, "Powinien wystąpić błąd TypeError"
    except TypeError:
        pass


def test_niezmienniki() -> None:
    try:
        PerishableProduct(1, "Mleko", 1, "l", 5, storage_temp=10.0)
        assert False, "Temperatura > 4.0°C powinna rzucić ValueError!"
    except ValueError:
        pass


def test_priorytet() -> None:
    mleko = PerishableProduct(1, "Mleko", 2, "l", expiry_days=5, storage_temp=2.0)
    makaron = DryProduct(2, "Makaron", 3, "kg", expiry_days=5, max_humidity=50)

    assert mleko.spoilage_urgency_score(5) > makaron.spoilage_urgency_score(5)

    mgr = PantryStockManager(Path("temp_test.json"))
    mgr.add_product(makaron)
    mgr.add_product(mleko)

    priorytety = mgr.get_priority_list()
    assert priorytety[0].product_id == 1  #


def test_json() -> None:
    test_file = Path("temp_pantry_test.json")
    mgr = PantryStockManager(test_file)
    mgr.add_product(PerishableProduct(1, "Jogurt", 4, "szt", expiry_days=3, storage_temp=3.5))
    mgr.add_product(DryProduct(2, "Ryż", 2, "kg", expiry_days=200, max_humidity=45))
    mgr.save_stock()

    mgr_loaded = PantryStockManager(test_file)
    mgr_loaded.load_stock()

    assert len(mgr_loaded.products) == 2
    assert isinstance(mgr_loaded.products[0], PerishableProduct)
    assert isinstance(mgr_loaded.products[1], DryProduct)
    assert mgr_loaded.products[0].storage_temp == 3.5
    assert mgr_loaded.products[1].max_humidity == 45

    if test_file.exists():
        test_file.unlink()


if __name__ == "__main__":
    test_blokada_ABC()
    print("[OK] Test 1: Blokada tworzenia obiektu klasy abstrakcyjnej FoodProduct.")

    test_niezmienniki()
    print("[OK] Test 2: Sprawdzanie temperatury przechowywania w PerishableProduct.")

    test_priorytet()
    print("[OK] Test 3: Oblicznie priorytetów.")

    test_json()
    print("[OK] Test 4: Zapis i odczyt JSON.")

    print("\n[SUKCES] Wszystkie  przeszły pomyślnie!")
