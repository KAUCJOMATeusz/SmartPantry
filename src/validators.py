def get_int_input(
        prompt: str,
        min_value: int = None,
        max_value: int = None
    ) -> int:
    while True:
            raw=input(prompt).strip()
            if not raw:
                print("Błąd: pusta wartość")
                continue
            try:
                val = int(raw)
                if min_value is not None and val < min_value:
                    print(f"Błąd: Wartośc jest mniejsza niż {min_value}")
                    continue
                if max_value is not None and val > max_value:
                    print(f"Błąd: Wartość jest większa niż {max_value}")
                    continue
                return val
            except ValueError:
                print(f"Błąd: '{raw}' nie jest liczbą całkowitą")

    """promt domyslnie zwraca str"""
def get_non_empty_string(prompt: str) -> str:
    while True:
        raw=input(prompt).strip()
        if not raw:
            print("Błąd wartości: pole jest puste")
        else:
            return raw




