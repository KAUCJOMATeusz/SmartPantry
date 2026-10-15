# Sprawozdanie z Zadania Laboratoryjnego nr 1
**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
**Projekt:** SmartPantry  
**Zespół (Autorzy):**  
1. Patryk Cisek (nr albumu: 164820) – login Git: PatrykC890
2. Mateusz Garwacki (nr albumu: 164828 ) – login Git:   KAUCJOMATeusz
**Data oddania:** 15.10.2026 

---

## 1. Cel i Zakres Inżynierski Zadania
Celem zadania było stworzenie prostej aplikacji tekstowej w konsoli do zarządzania domową spiżarnią SmartPantry. W tym etapie skupiliśmy się na stworzeniu głównego menu działającego w pętli oraz na zabezpieczeniu programu przed błędami użytkownika. Przetestowaliśmy, jak Python radzi sobie z typami danych i jak bezpiecznie pobierać liczby oraz tekst za pomocą instrukcji try-except.

---

## 2. Architektura Rozwiązania i Struktura Modułów
Program podzieliliśmy na cztery pliki w folderze src/, żeby każdy odpowiadał za jedną rzecz:
* `src/data.py` – Przechowuje startową listę produktów w spiżarni (jako listy i słowniki) oraz podstawowe ustawienia.
* `src/validators.py` – Zawiera funkcje, które sprawdzają, czy użytkownik wpisał poprawne dane (np. czy podał liczbę a nie litery).
* `src/services.py` – Odpowiada za logikę programu: ładne wyświetlanie tabeli z produktami i dodawanie nowych rzeczy.
* `src/main.py` – Główny plik programu, który uruchamia menu i kieruje użytkownika do odpowiednich opcji za pomocą match-case.

---

## 3. Kluczowy Fragment Kodu i Uzasadnienie Inżynierskie


```python
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
```

**Uzasadnienie wyboru:**  
Ta funkcja jest kluczowa, ponieważ chroni program przed nagłym wyłączeniem. Dzięki pętli while True i przechwytywaniu błędu ValueError, aplikacja nie zawiesi się, gdy ktoś przez pomyłkę wpisze litery zamiast cyfr, tylko poprosi o ponowne wpisanie danych.

---

## 4. Scenariusze Weryfikacji i Wyniki Testów


### Scenariusz A: Ścieżka poprawna (Happy Path)
* **Dane wejściowe:** Liczba 1
* **Oczekiwany i uzyskany wynik:**
```text
________________________________________
INTELIGENTNA SPIŻARNIA SMART-PANTRY
________________________________________
1.Wyświetl zawartość spiżarni
2.Dodaj nowy produkt
3.Sprawdzenie ilości produktów
4.Wyjście z programu
________________________________________
Wybierz opcje [1-4]1

________________________________________
| ID | Nazwa produktu       | Data ważności | Ilość |
| 1  | Makaron spaghetti    | 2027-03-20    | 3     |
| 2  | Mleko UHT            | 2026-12-15    | 6     |
| 2  | Kawa ziarnista       | 2027-10-28    | 2     |
```

### Scenariusz B: Obsługa błędów i wartości brzegowych
* **Dane wejściowe (błędne):** Wpisanie litery "a"
```text
________________________________________
INTELIGENTNA SPIŻARNIA SMART-PANTRY
________________________________________
1.Wyświetl zawartość spiżarni
2.Dodaj nowy produkt
3.Sprawdzenie ilości produktów
4.Wyjście z programu
________________________________________
Wybierz opcje [1-4]a
Nieznana opcja wybierz 1-4

```

---

## 5. Podział Pracy w Zespole

* **Patryk Cisek**
  * Odpowiedzialność za moduły: `src/data, src/services`
  * Zaimplementowane funkcjonalności: Baza produktów, Wyświetlanie, dodawanie i filtrowanie przedmiotów
  * Liczba wykonanych commitów: 3
* **Mateusz Garwacki**
  * Odpowiedzialność za moduły: `src/main, src/validators`
  * Zaimplementowane funkcjonalności: Stworzenie wyświetlania i działania menu aplikacji, sprawdzenie typu wprowadzanych wartości i obsługa błedów 
  * Liczba wykonanych commitów: 5
