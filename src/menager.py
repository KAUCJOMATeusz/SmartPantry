import csv
import json
from pathlib import Path
from models import FoodProduct, deserialize_product

class PantryStockManager:

    def __init__(self, data_path: Path) -> None:
        self.data_path: Path = data_path
        self._products: list[FoodProduct] = []

    @property
    def products(self) -> list[FoodProduct]:
        return list(self._products)

    def next_id(self) -> int:
        return max((p.product_id for p in self._products), default=0) + 1

    def add_product(self, product: FoodProduct) -> None:
        if not isinstance(product, FoodProduct):
            raise TypeError("Spiżarnia przyjmuje wyłącznie obiekty dziedziczące po FoodProduct.")
        if any(p.product_id == product.product_id for p in self._products):
            raise ValueError(f"Produkt o ID {product.product_id} już istnieje.")
        self._products.append(product)

    def get_priority_list(self) -> list[FoodProduct]:
        return sorted(
            self._products,
            key=lambda p: p.spoilage_urgency_score(p.expiry_days),
            reverse=True,
        )

    def get_expired_products(self) -> list[FoodProduct]:
        return [p for p in self._products if p.is_expired()]

    def save_stock(self) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [p.to_dict() for p in self._products]
        with open(self.data_path, mode="w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)

    def load_stock(self) -> None:
        if not self.data_path.exists():
            self._products = []
            return
        try:
            with open(self.data_path, mode="r", encoding="utf-8") as f:
                raw_data = json.load(f)
                # Obsługa zarówno listy słowników, jak i starego formatu ze słownikiem PantryShelf
                items_list = raw_data.get("products", []) if isinstance(raw_data, dict) else raw_data
                self._products = [deserialize_product(row) for row in items_list]
        except (json.JSONDecodeError, ValueError):
            self._products = []

    def export_shopping_list(self, csv_path: Path) -> int:
        missing = [p for p in self._products if p.quantity == 0]
        if not missing:
            return 0
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Nazwa", "Jednostka", "Data ważności"])
            for p in missing:
                writer.writerow([p.product_id, p.name, p.unit, p.exp_date])
        return len(missing)


