from typing import Any, Self
from datetime import datetime

class FoodProduct:
        __slots__ = ("_product_id", "name", "_quantity", "_unit", "_expiry_days", "_exp_date", "_weight")

        VALID_UNITS = {"g", "kg", "ml", "l", "szt"}

        def __init__(self,product_id: int,name: str,quantity: int | float,unit: str,
                expiry_days: int,exp_date: str | None = None,weight: float = 0.0
        ) -> None:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Nazwa produktu nie może być pusta.")
            self._product_id: int = int(product_id)
            self.name: str = name.strip()
            self._quantity = quantity
            self.unit = unit
            self._expiry_days = expiry_days
            self._exp_date = exp_date
            self._weight = weight

        @property
        def product_id(self) -> int:
            return self._product_id

        @property
        def unit(self) -> str:
            return self._unit

        @unit.setter
        def unit(self, value: str) -> None:
            if value not in self.VALID_UNITS:
                raise ValueError(f"Niedozwolona jednostka: '{value}'. Dozwolone to: {self.VALID_UNITS}")
            self._unit = value

        def is_expired(self) -> bool:
            return self._expiry_days <= 0


class PantryShelf:
    def __init__(self, shelf_id: int = 1, products: list[FoodProduct] | None = None) -> None:
        self.shelf_id: int = shelf_id
        self._products: list[FoodProduct] = []
        for p in (products if products is not None else []):
            self.add_product(p)

    @property
    def products(self) -> list[FoodProduct]:
        return list(self._products)

    def next_id(self) -> int:
        return max((p.product_id for p in self._products), default=0) + 1

    def add_product(self, product: FoodProduct) -> None:
        if any(p.product_id == product.product_id for p in self._products):
            raise ValueError(f"Produkt o ID {product.product_id} już istnieje.")
        self._products.append(product)

    def expired_products(self) -> list[FoodProduct]:
        return [p for p in self._products if p.is_expired()]

    def generate_shopping_list(self) -> list[FoodProduct]:
        return [p for p in self._products if p.quantity == 0]

    def to_dict(self) -> dict[str, Any]:
        return {
            "shelf_id": self.shelf_id,
            "products": [p.to_dict() for p in self._products],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        restored = [FoodProduct.from_dict(raw) for raw in data.get("products", [])]
        return cls(int(data.get("shelf_id", 1)), restored)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PantryShelf):
            return False
        return self.to_dict() == other.to_dict()

    def __str__(self) -> str:
        lines = [f"=== PÓŁKA #{self.shelf_id} ==="]
        lines.extend(f"  * {p}" for p in self._products)
        return "\n".join(lines)