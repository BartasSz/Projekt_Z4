"""Interfejs systemu ekspertowego — uzupełniony na spotkaniu 3. Uruchom: python -m streamlit run app.py"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "se"))
from silnik import coto, wczytaj_baze, wnioskuj_w_przod, wyjasnij_jak  # noqa: E402
from weryfikacja import weryfikuj  # noqa: E402

PLIK_BAZY = Path(__file__).parent / "wiedza" / "doradca_sportowy.json"  # TODO 1: własna baza wiedzy
baza = wczytaj_baze(PLIK_BAZY)

st.set_page_config(page_title=baza["nazwa"])
st.title(baza["nazwa"])

with st.sidebar:
    st.header("Weryfikacja bazy wiedzy")
    raport = weryfikuj(baza)
    if not raport:
        st.success("Nie wykryto problemów.")
    for poziom, komunikat in raport:
        (st.error if poziom == "BŁĄD" else st.warning)(komunikat)

with st.form("konsultacja"):
    fakty = {}
    for nazwa, opis in baza["atrybuty"].items():
        if opis["typ"] == "liczba":
            lo, hi = opis.get("zakres", [-100, 100])
            fakty[nazwa] = st.slider(opis["pytanie"], lo, hi, (lo + hi) // 2)
        elif opis["typ"] == "wybor":  # TODO 2: przyciski wyboru dla typu "wybor"
            fakty[nazwa] = st.radio(opis["pytanie"], opis["wartosci"], horizontal=True)
    wyslano = st.form_submit_button("Doradź")

if wyslano:
    wynik, slad = wnioskuj_w_przod(baza, fakty)
    cel = wynik.get(baza["cel"])
    # TODO 3: prezentacja wyniku oraz opisu "co to?"
    if cel is None:
        st.error("Brak dopasowanej reguły dla podanych parametrów wejściowych.")
    else:
        st.success(f"Polecam: **{cel}**")
        opis_coto = coto(baza, slad)
        if opis_coto:
            st.info(f"**Co to jest?** {opis_coto}")

    # TODO 4: wyjaśnienie "jak?" krok po kroku
    with st.expander("Jak do tego doszedłem?"):
        kroki = wyjasnij_jak(baza, slad)
        if not kroki:
            st.write("Nie odpalono żadnej reguły.")
        for krok in kroki:
            st.text(krok)