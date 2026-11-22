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
* `ml/drzewo.txt`, `ml/drzewo.png` — tekstowa i graficzna reprezentacja wyuczonego drzewa decyzyjnego.

## Uruchomienie

```bash
python ml/generator.py
python ml/trening.py
```

---

## Porównanie reguł drzewa CART z regułami eksperta (3 obserwacje)

1. **Wierne odtworzenie reguł klubowych (`P1 + R1`, `P1 + R2`, `P1 + R3`):**
   * *Reguły eksperta:* Posiadanie karnetu do klubu fitness (`P1`) w połączeniu z małą ilością czasu (`R1`) prowadzi bezpośrednio do decyzji `krótki bieg` bez względu na pogodę, natomiast przy dużej ilości czasu decyzja zależy od celu treningu (`R2`: `aerobowy` -> `ćwiczenia grupowe`, `R3`: `siłowy` -> `trening ogólnorozwojowy`).
   * *Drzewo CART:* W obu głównych gałęziach korzenia (`sym__czas_wolny_dużo <= 0.50` oraz `> 0.50`) sprawdzenie warunku `sym__co_wykorzystac_karnet do klubu fitness > 0.50` odtwarza te ścieżki z 100% dokładnością — tworzy czysty liść `krótki bieg` (głębokość 2) oraz dzieli gałąź przy dużej ilości czasu po cesze `sym__cel_treningu_siłowy <= 0.50` na `ćwiczenia grupowe` i `trening ogólnorozwojowy` (głębokość 4).

2. **Przybliżenie progów temperatury i łączenie warunków pogodowych (`14.50 °C` i `17.00 °C` zamiast `10 °C` i `15 °C`):**
   * *Reguły eksperta:* Reguły `P3`–`P6` rozdzielają aktywność w plenerze od domowej dwoma osobnymi progami: `temperatura >= 10` przy słonecznej pogodzie (`P6`) oraz `temperatura >= 15` przy zachmurzeniu (`P5`).
   * *Drzewo CART:* Algorytm CART wyznacza progi podziału w połowie między sąsiednimi wartościami w próbie uczącej, dlatego w drzewie pojawiają się progi połówkowe `remainder__temperatura <= 14.50` (odpowiednik `<= 14 °C`) oraz `remainder__temperatura <= 17.00` w gałęzi `co_wykorzystac == rower`, gdzie w jednym węźle połączono przypadki słoneczne (`>= 10 °C`) i pochmurne (`>= 15 °C`).

3. **Wchłonięcie klas mniejszościowych przez płytkie drzewo (`max_depth=4`):**
   * *Reguły eksperta:* Baza rozróżnia 11 klas decyzyjnych, w tym rzadziej losowane kombinacje takie jak `trening na siłowni plenerowej` (18 przykładów w próbie), `spacer` (46 przykładów) czy `deska SUP w plenerze` (32 przykłady).
   * *Drzewo CART:* Drzewo binarne o głębokości 4 posiada maksymalnie 16 liści ($2^4$), a kodowanie *One-Hot* rozbija każdy atrybut symboliczny na osobne kolumny binarne. W rezultacie przy `max_depth=4` drzewo nie zdążyło wydzielić liści dla wszystkich 11 klas (np. `trening na siłowni plenerowej` i `spacer` zostały połączone z liśćmi większościowymi `trening domowy`, `deska SUP w plenerze` i `bieganie`).

---

## Ograniczenia przyjętego rozwiązania

* **Pomiar wierności odtwarzania reguł zamiast walidacji dziedzinowej:** Etykiety w zbiorze `ml/dane.csv` pochodzą bezpośrednio z silnika `se/silnik.py`, zatem ocena drzewa mierzy wyłącznie stopień odwzorowania logiki zapisanej w pliku JSON, a nie merytoryczną trafność doboru aktywności w rzeczywistości (ta wymagałaby danych oznaczonych przez niezależnego eksperta).
* **Niedouczenie przy ograniczeniu `max_depth=4` i kodowaniu One-Hot:** Binarne podziały CART wymagają większej głębokości drzewa niż wielogałęziowe algorytmy typu ID3, aby bezstratnie odwzorować pełną strukturę 22 reguł i 11 klas.
* **Brak strojenia hiperparametrów na tym etapie:** Zgodnie z założeniami zadania Z4 zbiór testowy (`200` próbek w `ml/podzial.json`) pozostał nienaruszony — dobór optymalnej głębokości i przycinanie drzewa z wykorzystaniem walidacji krzyżowej na zbiorze treningowym zostaną przeprowadzone w zadaniu Z5.
