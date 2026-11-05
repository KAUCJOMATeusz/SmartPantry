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
