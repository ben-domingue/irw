from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0307216
# DOI: 10.1371/journal.pone.0307216
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0307216.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# Item 1 ("Age at release") is a polytomous person-level attribute scored
# from an age-at-release table (18-34.9=1, 35-39.9=0, 40-59.9=-1, 60+=-3),
# not a repeated behavioral response like items 2-10 -- kept as a covariate.
ITEM_COLS = [f"S99R item {i}" for i in range(2, 11)]
COV_MAP = {
    "S99R item 1": "cov_age_at_release",
    "Psychotic disorder": "cov_psychotic_disorder",
    "Intellectual disability": "cov_intellectual_disability",
    "Substance use disorder": "cov_substance_use_disorder",
    "Nordic background": "cov_nordic_background",
    "Secondary school diploma": "cov_secondary_school_diploma",
    "Steady partner": "cov_steady_partner",
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch()
    df = df.rename(columns={df.columns[0]: "id"})
    df = df.rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]

    item_rename = {c: f"item{c.split(' ')[-1]}" for c in ITEM_COLS}
    df = df.rename(columns=item_rename)
    item_cols = list(item_rename.values())

    assert df["id"].nunique() == len(df)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                   var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "baudin_2024_static99r.csv"
    long.to_csv(out_path, index=False)
    print(f"baudin_2024_static99r: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
