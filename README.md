# Doradca sportowy — Zadanie Z4 (Od reguł do danych: drzewo decyzyjne CART)

Projekt realizowany w ramach przedmiotu **Inżynieria wiedzy i maszynowe uczenie** (Wydział Informatyki UKW, Spotkanie 4). Wykorzystuje zweryfikowany system regułowy `Doradca sportowy` (`wiedza/doradca_sportowy.json`, 22 reguły, 11 klas decyzyjnych) jako generator etykiet do uczenia nadzorowanego klasyfikatora `DecisionTreeClassifier` (`scikit-learn`).

## Struktura repozytorium

* `wiedza/doradca_sportowy.json` — baza wiedzy systemu ekspertowego (5 atrybutów wejściowych, 1 wniosek pośredni `tryb_treningu`, cel `aktywnosc`),
* `se/silnik.py`, `se/weryfikacja.py` — silnik wnioskujący w przód i wstecz z modułem wyjaśnień oraz weryfikator bazy wiedzy (0 błędów, 0 uwag),
* `app.py` — interfejs webowy aplikacji w bibliotece Streamlit,
* `ml/generator.py` — generator danych uczących (`N = 1000`, `SEED = 42`), raportu luk i warstwowego podziału grupowego,
* `ml/dane.csv` — wygenerowany zbiór danych (`1000` przypadków, `843` unikalne kombinacje wejść, `0` luk),
* `ml/luki.json` — rejestr kombinacji wejść bez dopasowanej decyzji (`liczba_luk: 0`),
* `ml/slownik_danych.json` — słownik danych, dziedziny atrybutów i metadane próbkowania,
* `ml/podzial.json` — indeksy podziału `StratifiedGroupKFold(n_splits=5)` (`800` trening / `200` test, `11/11` klas w zbiorze testowym; zbiór testowy zamknięty do zadania Z6),
* `ml/trening.py` — potok przetwarzania (`Pipeline`: `OneHotEncoder` + `DecisionTreeClassifier(max_depth=4)`),
* `ml/reguly_drzewa.txt`, `ml/drzewo.png` — tekstowa i graficzna reprezentacja wyuczonego drzewa decyzyjnego.

## Uruchomienie

```bash
python ml/generator.py
python ml/trening.py
