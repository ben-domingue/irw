from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0247609
# DOI: 10.1371/journal.pone.0247609
# Audretsch, Belitski & Cherkas (2021), "Entrepreneurial ecosystems in
# cities: The role of institutions". S2 File (.dta). CC BY 4.0.
# N=1860 individual survey respondents (entrepreneurs, professors,
# investors, policymakers, etc.) across cities in 10 countries, rating
# 15 aspects of their local entrepreneurial ecosystem on a 1-7 scale
# (1=very poor .. 7=excellent).
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0247609.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [
    "eship_skills", "ee_quality", "eshipquantity", "govtsupport",
    "veturecapital", "univsupport", "corporatesupport", "mediasupport",
    "debtcapital", "formal_networking", "informal_networking",
    "eshipculture", "eship_aware", "corruption", "political_eship",
]

COV_COLS = {
    "female": "cov_gender",
    "age": "cov_age",
    "higheducation": "cov_higheducation",
    "occupation": "cov_occupation",
    "country": "cov_country",
    "city": "cov_city",
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".dta") as tmp:
        tmp.write(r.content)
        tmp.flush()
        df = pd.read_stata(tmp.name)

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COV_COLS)

    for c in ITEM_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    cov_cols = list(COV_COLS.values())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    out_name = "audretsch_2021_entrepreneurial_ecosystems"
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
