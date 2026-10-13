def print_menu():
    print("/n" + "_" * 40)
    print("INTELIGENTNA SPIŻARNIA SMART-PANTRY")
    print("_" * 40)
    print("1.Wyświetl stan spiżarni ")
    print("2.Sprawdź daty przydatności")
    print("3.Generator przepisów")
    print("4.Wyjście z programu")
    print("_" * 40)

def main():
    running = True
    while running:
        print_menu()
        choice = input("Wybierz opcje [1-4]")
        match choice.strip():
            case "1":
                """tutaj nazwya funckji"""
                running = False
            case "2":
                """tutaj nazwya funckji"""
                running = False
            case "3":
                """tutaj nazwya funckji"""
                running = False
            case "4" | "q" | "exit":
                print("Zamykanie programu...")
                running = False
            case _:
                    print("Nieznana opcja wybierz 1-4")
                    running = True

