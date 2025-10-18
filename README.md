# Programpobierającyaktualnąpogodę

## Wstęp

```
Programpobierającyaktualnedanezdotyczącepogodyzestrony
meteo.gig.eu/archiwum/aktualne.txt,obrabia,pokazujeitransmitujejeprzypomocy
protokołuModbusTCP.
PobranedaneibłędyzapisywanesąwbaziedanychSQLitewlokalizacji
“outputs\logs.db”
```
## InstalacjaPython

```
ProjektnapisanyjestwjęzykuPython.Abymócgoobsługiwać(przezpliki.py)
należyzainstalowaćPython,wedługnastępującychkroków:
● wejśćnastronehttps://www.python.org/downloads/orazpobraćnajonwsząwersję
(kliknąćżółtyprzycisk“DownloadPython[najnowszawersja])
● uruchomićinstalator-otworzyćpobranyplik.exe
● upewnićsię,żepole"AddPythontoPATH"jestzaznaczone(dółokna)
● kliknąć"InstallNow"ipostępowaćzgodniezinstrukcjamiinstalatora
```
```
PozakończeniuinstalacjizweryfikowaćczyPythonzostałpoprawniezainstalowany:
● otworzyćwierszpoleceń
● wpisać“python--version”lub“python3--version”
Jeślizwróconainformacjaniejestbłędemoznacza,żePyhonzostałzainstalowany
pomyślnie.
```
```
Czasamidodatkowotrzebazrestartowaćurządzenie.
```
## Instalacjapip

```
Programkorzystazszeregubibliotek,którenależyzainstalowaćprzypomocy‘pip’.
WwiększościprzypadkówpipjestinstalowanyrazemzPython-em.Abysprawdzić
czypipjestzainstalowanynanaszymurządzeniunależyotworzyćwierszpoleceńi
wpisać“pip--version”.Jeślizwróconawartośćniejestbłędemoznacza,żepipzostał
jużwcześniejzainstalowany.Wprzeciwnymwypadkunależy:
● otworzyćwierszpoleceń
● wpisać“python-mensurepip--upgrade”
● ponowniezweryfikowaćobecnośćpipnaurządzeniuprzezwpisanie“pip--version”w
wierszupoleceń
```

## Wykorzystanebiblioteki

```
Programwykorzystujenastępującebiblioteki:
● tk
● datetime
Abyjezainstalowaćnależydlakażdejznichwwierszupoleceńużyćkomendy“pip
install[nazwabiblioteki]”
```
## ZnaczeniedanychwModbuswedługindeksów

```
● dataigodzina,zktórejpochodządane(kiedyzostałypobrane):
0 - rok, 1 - miesiąc, 2 - dzień, 3 - godzina, 4 - minuta, 5 - sekunda
● 6:sygnałżycia
● 10-48:pobranedane;wartościliczbowemnożonesąrazy10;kolejnośćtakjakw
pliku;oznaczeniekierunkuwiatru"N"-"1","E"-"2","S"-"3","W"-"4"
```
## Ustawienia

```
Programposiadasystemustawień,wramachktóregomożnaustawić:
● “updateTime”-ilośćsekund,poktórychpobieranesąnowedane.Domyślnie600.
● “port”-numerportu,naktórymtransmitowanesądane.Domyślnie502.
Ustawieniaprzechowywanesąwpliku.jsonznajdującymsięw
“outputs\settings.json”.Jeśliprogramnieznajdzieplikuzustawieniamiwygeneruje
gozwartościamidomyślnymi.
```

