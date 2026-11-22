"""Generator danych uczących z silnika Doradca sportowy (Zadanie Z4)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "se"))
from silnik import wczytaj_baze, wnioskuj_w_przod  # noqa: E402

SEED = 42
N_PROBEK = 1000
PLIK_BAZY = ROOT / "wiedza" / "doradca_sportowy.json"
KATALOG_ML = Path(__file__).resolve().parent


def generuj():
    baza = wczytaj_baze(PLIK_BAZY)
    atrybuty = baza["atrybuty"]
    cel = baza["cel"]
    wejscia = [k for k, v in atrybuty.items() if v["typ"] != "wniosek"]

    rng = np.random.default_rng(SEED)
    wiersze = []
    luki = []

    for i in range(N_PROBEK):
        x = {}
        for nazwa in wejscia:
            opis = atrybuty[nazwa]
            if opis["typ"] == "liczba":
                lo, hi = opis["zakres"]
                x[nazwa] = int(rng.integers(lo, hi + 1))
            else:
                x[nazwa] = str(rng.choice(opis["wartosci"]))

        fakty, _ = wnioskuj_w_przod(baza, x)
        decyzja = fakty.get(cel)
        if decyzja is None:
            luki.append(x)
            continue

        wiersze.append({
            "sample_id": len(wiersze),
            **x,
            cel: decyzja,
            "label_source": "rule_engine",
        })

    df = pd.DataFrame(wiersze)
    df.to_csv(KATALOG_ML / "dane.csv", index=False, encoding="utf-8")

    (KATALOG_ML / "luki.json").write_text(
        json.dumps({"liczba_luk": len(luki), "przypadki": luki}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    grupy = df[wejscia].astype(str).agg("|".join, axis=1)
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    train_idx, test_idx = next(sgkf.split(df[wejscia], df[cel], groups=grupy))

    podzial = {
        "metoda": "StratifiedGroupKFold(n_splits=5)",
        "random_state": SEED,
        "cechy_X": wejscia,
        "etykieta_y": cel,
        "liczba_trening": int(len(train_idx)),
        "liczba_test": int(len(test_idx)),
        "train_ids": df.iloc[train_idx]["sample_id"].tolist(),
        "test_ids": df.iloc[test_idx]["sample_id"].tolist(),
    }
    (KATALOG_ML / "podzial.json").write_text(
        json.dumps(podzial, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    slownik = {
        "zrodlo_bazy": "wiedza/doradca_sportowy.json",
        "seed": SEED,
        "liczba_wygenerowanych": int(len(df)),
        "liczba_unikalnych_wejsc": int(grupy.nunique()),
        "liczba_luk": int(len(luki)),
        "rozklad_klas": df[cel].value_counts().to_dict(),
        "kolumny": {
            "sample_id": {"rola": "identyfikator techniczny (nie trafia do X)", "typ": "int"},
            **{
                k: {
                    "rola": "cecha wejściowa (X)",
                    "typ": atrybuty[k]["typ"],
                    "dziedzina": atrybuty[k].get("zakres") or atrybuty[k].get("wartosci"),
                }
                for k in wejscia
            },
            cel: {
                "rola": "etykieta decyzyjna (y)",
                "typ": "klasa (11 wartości)",
                "wartosci": atrybuty[cel]["wartosci"],
            },
            "label_source": {"rola": "metadane pochodzenia etykiety", "wartosc": "rule_engine"},
        },
    }
    (KATALOG_ML / "slownik_danych.json").write_text(
        json.dumps(slownik, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Zapisano {len(df)} wierszy (unikalnych kombinacji: {grupy.nunique()}, luk: {len(luki)}).")
    print(f"Podział: trening={len(train_idx)}, test={len(test_idx)} (klas w teście: {df.iloc[test_idx][cel].nunique()}/11).")
    print("\nLiczebność klas:")
    print(df[cel].value_counts().to_string())


if __name__ == "__main__":
    generuj()