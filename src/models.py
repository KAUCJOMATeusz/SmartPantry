class FoodProduct:
    __slots__ = ("_product_id", "name", "_quantity", "_unit", "_expiry_days", "_exp_date", "_weight")

    def __init__(self, product_id: int, name: str, quantity: int | float,
                 unit: str, expiry_days: int,
                 exp_date: str | None = None, weight: float = 0.0) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Nazwa produktu nie może być pusta.")
        self._product_id: int = int(product_id)
        self.name: str = name.strip()
        self.quantity = quantity
        self.unit = unit
        self.expiry_days = expiry_days
        self.exp_date = exp_date
        self.weight = weight