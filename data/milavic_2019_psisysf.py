from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0220930
# DOI: 10.1371/journal.pone.0220930
# The raw file's trailing column is an empty Excel-overflow artifact
# (literal header "#########", all-NaN) -- dropped along with the other
# non-item metadata columns.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0220930.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "Sex": "cov_sex",
    "Age": "cov_age",
    "Category": "cov_category",
    "Train_Hours_Weekly": "cov_train_hours_weekly",
    "Years_of_Training": "cov_years_of_training",
    "National_TeamPlayer": "cov_national_team_player",
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch()
    df = df.rename(columns={"ID": "id"})
    df = df.rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]

    item_cols = [c for c in df.columns if c.startswith("PSIS-Y-SF_")]
    assert df["id"].nunique() == len(df)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                   var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "milavic_2019_psisysf.csv"
    long.to_csv(out_path, index=False)
    print(f"milavic_2019_psisysf: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
