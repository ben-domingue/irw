#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0227818
# DOI: 10.1371/journal.pone.0227818
# The off-prescription use of modafinil: An online survey of perceived risks
# and benefits (Teodorini, Rycroft & Smith-Spark, PLOS ONE 2020)
# SI: journal.pone.0227818_S4_File.sav, CC BY 4.0
#
# The SI file is a large (168-column) survey covering drug-use history,
# checkbox symptom lists, and free-text fields. The only genuine multi-item
# Likert scale in the file is the 8-item "attitudes toward modafinil for
# cognitive enhancement" block (Q10.1_1 .. Q10.1_8, 1-5 agreement scale).
# Everything else is single-item, checkbox/binary, or open-text and is not
# shipped here.

import os

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0227818.s004"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"Q10.1_{i}" for i in range(1, 9)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    tmp_path = "/tmp/_teodorini_2020_s4.sav"
    with open(tmp_path, "wb") as f:
        f.write(r.content)
    df, _ = pyreadstat.read_sav(tmp_path)
    os.remove(tmp_path)
    return df


def convert():
    df = fetch_data()

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    df = df.rename(columns={"age": "cov_age", "sex": "cov_sex"})
    cov_cols = ["cov_age", "cov_sex"]

    assert all(c in df.columns for c in ITEM_COLS)

    keep = ["id"] + cov_cols + ITEM_COLS
    sub = df[keep].copy()

    long = sub.melt(
        id_vars=["id"] + cov_cols,
        value_vars=ITEM_COLS,
        var_name="item",
        value_name="resp",
    )
    long["item"] = long["item"].str.replace("Q10.1_", "modatt_", regex=False)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    # Scale is documented (in the questionnaire) as a 1-5 agreement scale.
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "teodorini_2020_modafinil_attitudes.csv")
    long.to_csv(out_path, index=False)
    print(f"teodorini_2020_modafinil_attitudes.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
