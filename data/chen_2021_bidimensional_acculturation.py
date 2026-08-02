from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0258323
# DOI: 10.1371/journal.pone.0258323
# Chen et al. (2021), "The psychometric properties of the Bidimensional
# Acculturation Scale for Marriage-Based Immigrant Women in Taiwan". S1
# Data. CC BY 4.0. N=310. Two 24-item raw subscales: ACC (acculturation
# to host culture) and ENC (heritage-culture retention/"enculturation").
# `*_Domain_*` and `*_Total` columns (derived) not shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0258323.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Age_5C": "cov_age_cat", "EDU_4C": "cov_education", "Income_5C": "cov_income",
           "Country_12C": "cov_country"}

SCALES = {
    "chen_2021_acculturation": [f"ACC_{i}" for i in range(1, 25)],
    "chen_2021_enculturation": [f"ENC_{i}" for i in range(1, 25)],
}

LIKERT_MAP = {"never": 1, "seldom": 2, "sometimes": 3, "often": 4, "always": 5}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={**COV_MAP, "ID": "id"})


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(str).map(LIKERT_MAP)
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
