"""Trening drzewa decyzyjnego CART na zbiorze treningowym (Zadanie Z4)."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree

KATALOG_ML = Path(__file__).resolve().parent


def trenuj():
    df = pd.read_csv(KATALOG_ML / "dane.csv", encoding="utf-8")
    podzial = json.loads((KATALOG_ML / "podzial.json").read_text(encoding="utf-8"))
    slownik = json.loads((KATALOG_ML / "slownik_danych.json").read_text(encoding="utf-8"))

    cechy_x = podzial["cechy_X"]
    cel_y = podzial["etykieta_y"]
    symb = [c for c in cechy_x if slownik["kolumny"][c]["typ"] == "wybor"]

    train_df = df[df["sample_id"].isin(podzial["train_ids"])]
    X_train = train_df[cechy_x]
    y_train = train_df[cel_y]

    kod = ColumnTransformer(
        [("sym", OneHotEncoder(handle_unknown="ignore"), symb)],
        remainder="passthrough",
    )
    model = Pipeline([
        ("kod", kod),
        ("drzewo", DecisionTreeClassifier(max_depth=4, random_state=podzial["random_state"])),
    ])
    model.fit(X_train, y_train)

    drzewo = model.named_steps["drzewo"]
    nazwy_cech = list(model.named_steps["kod"].get_feature_names_out())

    tekst_drzewa = export_text(drzewo, feature_names=nazwy_cech)
    (KATALOG_ML / "reguly_drzewa.txt").write_text(tekst_drzewa, encoding="utf-8")
    print("=== Reguły drzewa (max_depth=4) ===")
    print(tekst_drzewa)

    fig, ax = plt.subplots(figsize=(22, 10), dpi=200)
    plot_tree(
        drzewo,
        feature_names=nazwy_cech,
        class_names=list(drzewo.classes_),
        filled=True,
        rounded=True,
        fontsize=8,
        ax=ax,
    )
    plt.tight_layout()
    plt.savefig(KATALOG_ML / "drzewo.png")
    print("Zapisano: ml/reguly_drzewa.txt oraz ml/drzewo.png")


if __name__ == "__main__":
    trenuj()