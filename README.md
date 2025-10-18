# Program pobierający aktualną pogodę

## Wstęp

```
Program pobierający aktualne dane z dotyczące pogody ze strony
meteo.gig.eu/archiwum/aktualne.txt, obrabia, pokazuje i transmituje je przy pomocy
protokołu ModbusTCP.
Pobrane dane i błędy zapisywane są w bazie danych SQLite w lokalizacji
“outputs\logs.db”
```
## Instalacja Python

```
Projekt napisany jest w języku Python. Aby móc go obsługiwać (przez pliki .py)
należy zainstalować Python, według następujących kroków:
● wejść na strone https://www.python.org/downloads/ oraz pobrać najonwszą wersję
(kliknąć żółty przycisk “Download Python [najnowsza wersja])
● uruchomić instalator - otworzyć pobrany plik .exe
● upewnić się, że pole "Add Python to PATH" jest zaznaczone (dół okna)
● kliknąć "Install Now" i postępować zgodnie z instrukcjami instalatora

Po zakończeniu instalacji zweryfikować czy Python został poprawnie zainstalowany:
● otworzyć wiersz poleceń
● wpisać “python --version” lub “python3 --version”. Jeśli zwrócona informacja
nie jest błędem oznacza, że Pyhon został zainstalowany pomyślnie

Czasami dodatkowo trzeba zrestartować urządzenie.
```
## Instalacja pip

```
Program korzysta z szeregu bibliotek, które należy zainstalować przy pomocy ‘pip’.
W większości przypadków pip jest instalowany razem z Python-em. Aby sprawdzić czy pip
jest zainstalowany na naszym urządzeniu należy otworzyć wiersz poleceń i wpisać
“pip --version”. Jeśli zwrócona wartość nie jest błędem oznacza, że pip został już
wcześniej zainstalowany. W przeciwnym wypadku należy:
● otworzyć wiersz poleceń
● wpisać “python -m ensurepip --upgrade”
● pponownie zweryfikować obecność pip na urządzeniu przez wpisanie “pip --version”
w wierszu poleceń
```

## Wykorzystane biblioteki

```
Program wykorzystuje następujące biblioteki:
● tk
● datetime
Aby je zainstalować należy dla każdej z nich w wierszu poleceń użyć komendy
“pip install [nazwa biblioteki]”
```
## Znaczenie danych w Modbus według indeksów

```
● Znaczenie danych w Modbus według indeksów
0 - rok, 1 - miesiąc, 2 - dzień, 3 - godzina, 4 - minuta, 5 - sekunda
● 6: sygnałżycia
● 10-48: pobrane dane; wartości liczbowe mnożone są razy 10; kolejność tak
jak w pliku; oznaczenie kierunku wiatru "N"-"1", "E"-"2", "S"-"3", "W"-"4"
```
## Ustawienia

```
Program posiada system ustawień, w ramach którego można ustawić:
● “updateTime” - ilość sekund, po których pobierane są nowe dane. Domyślnie 600.
● “port” - numer portu, na którym transmitowane są dane. Domyślnie 502.
Ustawienia przechowywane są w pliku .json znajdującym się w “outputs\settings.json”.
Jeśli program nie znajdzie pliku z ustawieniami wygeneruje go z wartościami domyślnymi.
```

