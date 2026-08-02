from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0199924
# DOI: 10.1371/journal.pone.0199924
# Molino et al. (2018), "Personality and social support as determinants
# of entrepreneurial intention. Gender differences in Italy". S1
# Dataset. CC BY 4.0. N=658. Two scales: `d_5` (8 items, 1-7, already
# numeric) and `d_6` (34 items, 1-7, text-coded endpoints in Italian --
# "Per niente d'accordo" (not at all agree) = 1, "Del tutto daccordo"
# (totally agree) = 7 -- recoded). Demographic columns (d_1-d_4) not
# shipped as items.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0199924.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

LIKERT_MAP = {"Per niente d'accordo": 1, "Del tutto daccordo": 7}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"ID": "id"})


def _ship(df, out_name, item_cols):
    long = df.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"].astype(str).replace(LIKERT_MAP), errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    _ship(df, "molino_2018_d5_scale", [f"d_5_{i}" for i in range(1, 9)])
    _ship(df, "molino_2018_d6_scale", [f"d_6_{i}" for i in range(1, 35)])


if __name__ == "__main__":
    convert()
