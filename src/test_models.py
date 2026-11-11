from models import FoodProduct, PantryShelf


def test_scenariusz_1_poprawne_instancjonowanie():
    produkt = FoodProduct(
        product_id=1,
        name="Mleko",
        quantity=2.5,
        unit="l",
        expiry_days=7
    )
    assert produkt.product_id == 1
    assert produkt.name == "Mleko"
    assert produkt.quantity == 2.5
    assert produkt.unit == "l"

    polka = PantryShelf(shelf_id=5, products=[produkt])
    assert polka.shelf_id == 5
    assert len(polka.products) == 1


def test_scenariusz_2_odrzucenie_blednych_danych():
    try:
        FoodProduct(
            product_id=2,
            name="Chleb",
            quantity=1,
            unit="sztuka",
            expiry_days=3
        )
        assert False
    except ValueError:
        pass

    polka = PantryShelf(shelf_id=1)
    p1 = FoodProduct(10, "Cukier", 1, "kg", 100)
    p2 = FoodProduct(10, "Mąka", 2, "kg", 50)

    polka.add_product(p1)
    try:
        polka.add_product(p2)
        assert False
    except ValueError:
        pass


def test_scenariusz_3_dzialanie_protokolu_porownan():
    p_wyszsze_id = FoodProduct(15, "Masło", 1, "szt", 10)
    p_nizsze_id = FoodProduct(3, "Ser", 2, "szt", 5)

    lista_produktow = [p_wyszsze_id, p_nizsze_id]
    lista_produktow.sort()

    assert lista_produktow[0].product_id == 3
    assert lista_produktow[1].product_id == 15


def test_scenariusz_4_serializacja():
    p1 = FoodProduct(1, "Kefir", 2, "ml", 4, "2026-11-10", weight=0.5)
    p2 = FoodProduct(2, "Sól", 0, "kg", 365)

    oryginalna_polka = PantryShelf(shelf_id=12, products=[p1, p2])

    slownik_danych = oryginalna_polka.to_dict()
    odtworzona_polka = PantryShelf.from_dict(slownik_danych)

    assert oryginalna_polka == odtworzona_polka


if __name__ == "__main__":
    test_scenariusz_1_poprawne_instancjonowanie()
    test_scenariusz_2_odrzucenie_blednych_danych()
    test_scenariusz_3_dzialanie_protokolu_porownan()
    test_scenariusz_4_serializacja()