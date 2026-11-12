# Sprawozdanie z Zadania Laboratoryjnego nr 1, 2, 3
**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
**Projekt:** SmartPantry  
**Zespół (Autorzy):** 
1. Patryk Cisek (nr albumu: 164820) – login Git: PatrykC890  
2. Mateusz Garwacki (nr albumu: 164828 ) – login Git:   KAUCJOMATeusz  

**Data oddania:**  
[Etap 1] 15.10.2026  
[Etap 2] 29.10.2026  
[Etap 3] 12.11.2026

---

## 1. Cel i Zakres Inżynierski Zadania
[Etap 1] Celem tego etapu było stworzenie prostej aplikacji tekstowej w konsoli do zarządzania domową spiżarnią SmartPantry. W tym etapie skupiliśmy się na stworzeniu głównego menu działającego w pętli oraz na zabezpieczeniu programu przed błędami użytkownika. Przetestowaliśmy, jak Python radzi sobie z typami danych i jak bezpiecznie pobierać liczby oraz tekst za pomocą instrukcji try-except.

[Etap 2] Drugi etap polegał na przejściu z ulotnej pamięci RAM na zapis danych na twardym dysku w formacie JSON oraz generowanie raportów z braków magazynowych spiżarni (list zakupów). Kluczowym elementem było wdrożenie defensywnej obsługi wątków wejścia/wyjścia, która chroni program przed awarią, w przypadku braku lub uszkodzenia plików bazy danych, zapewniając automatyczną inicjalizację struktury. Dodatkowym elementem, który zastosowaliśmy było zabezpieczenie ciągłości działania aplikacji poprzez mechanizm kopii zapasowych.

[Etap 3] W trzecim etapie przebudowaliśmy aplikację tak, aby zamiast zwykłych słowników (`dict`) korzystała z obiektów i klas. Dodaliśmy mechanizmy pilnujące poprawności danych – program sam sprawdza teraz, czy wpisana jednostka miary jest dozwolona, oraz pilnuje, by na jednej półce nie pojawiły się dwa produkty o tym samym numerze ID. 
Usprawniliśmy także wyświetlanie i sortowanie. Dzięki dodaniu metod porównujących produkty (`__lt__`), spiżarnia sama układa zawartość od tych rzeczy, którym najszybciej kończy się termin ważności. Dodatkowo zastosowaliśmy liczenie dni do końca przydatności – użytkownik wpisuje tylko zwykłą datę przydatności, a program sam wylicza ilość pozostałych dni.
Wprowadziliśmy dziedziczenia i polimorfizm, przebudowaliśmy klasę FoodProduct na klasę abstrakcyjną. Wprowadziliśmy także klasę menedżera, która zarządza całą kolekcją

## 2. Architektura Rozwiązania i Struktura Modułów
[Etap 1]
Program podzieliliśmy na cztery pliki w folderze src/, żeby każdy odpowiadał za jedną rzecz:
* `src/data.py` - Przechowuje startową listę produktów w spiżarni (jako listy i słowniki) oraz podstawowe ustawienia.
* `src/validators.py` - Zawiera funkcje, które sprawdzają, czy użytkownik wpisał poprawne dane (np. czy podał liczbę a nie litery).
* `src/services.py` - Odpowiada za logikę programu: ładne wyświetlanie tabeli z produktami i dodawanie nowych rzeczy.
* `src/main.py` - Główny plik programu, który uruchamia menu i kieruje użytkownika do odpowiednich opcji za pomocą match-case.

[Etap 2]
W tym etapie całkowicie usunęliśmy plik src/data.py, zastępując go trwałym zapisem dyskowym i wprowadzając dodatkową architekturę
* `src/storage.py` - Przejął rolę zarządzania danymi. Odpowiada wyłącznie za fizyczny odczyt i zapis plików na dysku
* `src/data/pantry_stock.json` - Trwała baza danych w formacie JSON, w której zapisujemy aktualny stan zapasów spiżarni
* `src/exports/shopping_list.csv` - Wygenerowany arkusz CSV zawierający listę brakujących składników
* `srce/data/backups` - Przechowuje kopie zapasowe bazy danych

[Etap 3]
W tym etapie stworzyliśmy nowy plik na modele danych i dostosowaliśmy resztę programu do pracy na obiektach
* `src/models.py` - Zawiera dwie klasy: Encje - FoodProduct oraz Agregat - PantryShelf
* `src/test_models.py` - Niezależny skrypt z automatycznymi testami jednostkowymi. Sprawdza działanie klas z pliku `models.py` bez konieczności ręcznego przeklikiwania menu
* `src/main.py` - Menu zostało połączone z obiektami, posiada dodatkową opcję - wyświetlanie produktów przeterminowanych
* `src/storage.py` - Funkcje wczytywania i zapisywania danych zostały zmodyfikowane pod pracę z obiektami
* `src/services.py` - Dostosowany do wyświetlania tabeli z właściwości obiektów, wprowadzoana szersza tabela z wyliczonymi dniami do przeterminowania.
* `src/menager.py` - Zawiera klasę która oddziela logikę zarządzania produktami i zapisem plików
* `src/test_menager` - Zestaw autotestów sprawdzający blokadę klasy abstrakcyjnej, walidację podklas, sortowanie priorytetów oraz odczyt polimorficzny z pliku JSON.

---

## 3. Kluczowy Fragment Kodu i Uzasadnienie Inżynierskie

[Etap 1]
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

[Etap 2]

```python
DEFAULT_STOCK = [
    {"id": 1, "name": "Makaron spaghetti", "exp_date": "2027-03-20", "quantity": 4, "weight": 500},
    {"id": 2, "name": "Mleko UHT", "exp_date": "2026-12-15", "quantity": 6, "weight": 250},
    {"id": 3, "name": "Kawa ziarnista", "exp_date": "2027-10-28", "quantity": 1, "weight": 480},
]


def safe_load_pantry():
    try:
        with open(DATA_PATH, mode="r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(DATA_PATH, mode="w", encoding="utf-8") as f:
            json.dump(DEFAULT_STOCK, f, indent=4, ensure_ascii=False)
        return DEFAULT_STOCK
```

**Uzasadnienie wyboru**
Ta funkcja jest kluczowa dla stabilności programu w drugim etapie projektu. Zaimplementowano w niej wzorzec automatycznej inicjalizacji bazy danych oraz bezpiecznego fallbacku. Dzięki temu aplikacja nie zawiesza się przy pierwszym uruchomieniu na czystym systemie lub w przypadku uszkodzenia struktury pliku JSON. Zamiast tego cicho odbudowuje plik bazy danych, zasilając go domyślną kolekcją `DEFAULT_STOCK`.

[Etap 3]

```python
DEFAULT_STOCK = [
    {"id": 1, "name": "Makaron spaghetti", "exp_date": "2027-03-20", "quantity": 4, "weight": 500},
    {"id": 2, "name": "Mleko UHT", "exp_date": "2026-12-15", "quantity": 6, "weight": 250},
    {"id": 3, "name": "Kawa ziarnista", "exp_date": "2027-10-28", "quantity": 1, "weight": 480},
]


 def __lt__(self, other: "FoodProduct") -> bool:
            if not isinstance(other, FoodProduct):
                return False
            return (self._expiry_days, self.name) < (other._expiry_days, other.name)
```

**Uzasadnienie wyboru**
Ta metoda pozwala na automatyczne sortowanie listy produktów za pomocą zwykłego polecenia `.sort()`. Dzięki temu, że w jednej krotce połączyliśmy dni ważności i nazwę, Python sam ustawia na początku listy te produkty, które najszybciej się zepsują, a przy tej samej dacie układa je alfabetycznie.

---

## 4. Scenariusze Weryfikacji i Wyniki Testów

[Etap 1]

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
Wybierz opcje [1-4]a
Nieznana opcja wybierz 1-4

```



[Etap 2]
### Scenariusz A: Ścieżka poprawna (Happy Path)
* **Dane wejściowe:** Produkt: "Płatki owsiane", Data ważności: "2028-07-19", Waga: "400", Ilość: "2"
* **Oczekiwany i uzyskany wynik:**
```text
 --- DODAJ NOWY PRODUKT ---
Podaj nazwę produktu: Płatki owsiane
Podaj datę ważności: 2028-07-19
Podaj masę w gramach: 400
Podaj ilość: 2
Pomyślnie dodano produkt: Płatki owsiane (przyznane ID: 7)

_____________________________________________________________________________
| ID | Nazwa produktu       | Data ważności | Waga w gramach     | Ilość    |
_____________________________________________________________________________
| 1  | Makaron spaghetti    | 2027-03-20    | 500                | 4        |
| 2  | Mleko UHT            | 2026-12-15    | 250                | 6        |
| 3  | Kawa ziarnista       | 2027-10-28    | 480                | 2[!]     |
| 4  | Ser żółty            | 2026-10-15    | 248.879            | 0[!]     |
| 5  | Herbata czarna       | 2028-07-22    | 80.0               | 0[!]     |
| 6  | Śmietana 30%         | 2026-12-28    | 300.0              | 0[!]     |
| 7  | Płatki owsiane       | 2028-07-19    | 400.0              | 2[!]     |
_____________________________________________________________________________

```

Nowy produkt pojawia się w tabeli. Po zamknięciu i ponownym włączeniu aplikacji dane są dalej dostępne.

### Scenariusz B: Obsługa błędów i wartości brzegowych
* **Dane wejściowe (błędne):** Usunięcie pliku bazy danych z dysku i uruchomienie skryptu
* **Oczekiwany i uzyskany wynik:**

Program uruchamia się bez błędów typu `FileNotFoundError`. W tle zostaje automatycznie wygenerowany folder oraz plik `pantry_stock.json` zasilony domyślnymi produktami z kolekcji `DEFAULT_STOCK`.


[Etap 3 ]
### Scenariusz A: Ścieżka poprawna (Happy Path)
* **Dane wejściowe:** Uruchomienie skryptu `python test_models.py`
* **Oczekiwany i uzyskany wynik:**

Program uruchamia 4 testy sprawdzające działanie klas: poprawne tworzenie obiektów, blokowanie błędnych jednostek i duplikatów ID za pomocą błędu `ValueError`, poprawne sortowanie produktów oraz zapis i odczyt całej półki z zachowaniem wszystkich danych.

### Scenariusz B: Obsługa błędów i wartości brzegowych
* **Dane wejściowe (błędne):** Wprowadzenie nieprawidłowej jednostki przy dodawaniu nowego produktu
* **Oczekiwany i uzyskany wynik:**

```text
--- DODAJ NOWY PRODUKT ---
Podaj nazwę produktu: cebula
Podaj datę ważności: 2026-20-12
Podaj masę w gramach: 50
Podaj ilość: 10
Podaj jednostkę: x

[BŁĄD] Nie można dodać produktu: Niedozwolona jednostka: 'x'. Dozwolone to: {'szt', 'ml', 'kg', 'l', 'g'}

```


## 5. Podział Pracy w Zespole
[Etap 1]
* **Patryk Cisek**
  * Odpowiedzialność za moduły: `src/data, src/services`
  * Zaimplementowane funkcjonalności: Baza produktów, Wyświetlanie, dodawanie i filtrowanie przedmiotów
  * Liczba wykonanych commitów: 3
* **Mateusz Garwacki**
  * Odpowiedzialność za moduły: `src/main, src/validators`
  * Zaimplementowane funkcjonalności: Stworzenie wyświetlania i działania menu aplikacji, sprawdzenie typu wprowadzanych wartości i obsługa błedów 
  * Liczba wykonanych commitów: 5

[Etap 2]  
* **Patryk Cisek**
  * Odpowiedzialność za moduły: `src/storage`
  * Zaimplementowane funkcjonalności: Stworzenie funckji zapisu do bazy danych i eksportu do csv, utworzenie funkcji zapisu atomowego i tworzenia kopii zapasowej
  * Liczba wykonanych commitów: 4  
* **Mateusz Garwacki**
  * Odpowiedzialność za moduły: `src/main`
  * Zaimplementowane funkcjonalności: Modyfikacja kodu i zaimplementowanie funkcji zapisu do bazy danych i eksportu do csv, modyfikacja kodu o działanie kopii i zapisu atomowego
  * Liczba wykonanych commitów: 3  

[Etap 3]  
* **Patryk Cisek**
  * Odpowiedzialność za moduły: `src/models, src/test_models, menager.py`
  * Zaimplementowane funkcjonalności: Stworzenie klas: FoodProduct i PantryShelf, oraz utworzenie automatycznych testów jednostkowych, stworzenie klasy PantryStockMenager
  * Liczba wykonanych commitów: 3  
* **Mateusz Garwacki**
  * Odpowiedzialność za moduły: `src/models, src/test_menager.py`
  * Zaimplementowane funkcjonalności: Stworzenie i implementacja niezmiennika oraz metody genreującą stan magazynu i generującą brakujące pozycje, modyfikacja klasy FoodProduct na klasę abstrakcyjną, utworzenie autotestów `test_menager.py`
  * Liczba wykonanych commitów: 2  
