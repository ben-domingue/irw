from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("Assessment of health literacy among migrant populations in "
         "Southern Spain (Poza Méndez, Bas Sarmiento, Fernández Gutiérrez "
         "& Erahmouni, 2026, figshare)")
URL  = "https://figshare.com/articles/dataset/Assessment_of_health_literacy_among_migrant_populations_in_Southern_Spain/31078552"
DOI  = "10.6084/m9.figshare.31078552"
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://ndownloader.figshare.com/files/61057522"

COV_COLS = {
    "Sexo": "cov_sex",
    "Edad": "cov_age",
    "Nacionalidad": "cov_nationality",
    "Estadocivil": "cov_marital_status",
    "Estudios": "cov_education",
    "Formaciónsanitaria": "cov_health_training",
}


def convert():
    print("Downloading Datos_HL_Migrant_.sav ...")
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    raw = pd.read_spss(pd.io.common.BytesIO(r.content), convert_categoricals=False)
    raw = raw.rename(columns={"CÓDIGOSUJETO": "id"})
    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)
    cov_cols = list(cov.columns.drop("id"))

    item_cols = [f"PREGUNTA{i}" for i in range(1, 17)]
    items = raw[["id"] + item_cols].merge(cov, on="id")
    long = items.melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp"] + cov_cols
    long = long[col_order].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "poza2026_hlseu.csv"
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


if __name__ == "__main__":
    convert()
