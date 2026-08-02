from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0261617
# DOI: 10.1371/journal.pone.0261617
# Fitriana & Hutagalung (2022), "Happiness at work: A cross-cultural
# validation of happiness at work scale". S1/S2 Data. CC BY 4.0. Two
# separate samples: S1 = EFA sample (N=105, all 31 candidate items A1-A31,
# 1-5 Likert); S2 = field study sample (N=370, the 18-item final scale
# A1-A18, plus demographics). Shipped as two tables since the item sets
# and samples differ.
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def _fetch(url: str) -> bytes:
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    return r.content


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # EFA sample
    url1 = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0261617.s001")
    df1 = pd.read_excel(io.BytesIO(_fetch(url1)))
    df1 = df1.rename(columns={"Unnamed: 0": "id"})
    item_cols = [c for c in df1.columns if c.startswith("A")]
    long1 = df1.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long1["resp"] = pd.to_numeric(long1["resp"], errors="coerce")
    long1 = long1.dropna(subset=["resp"]).reset_index(drop=True)
    long1 = long1[["id", "item", "resp"]]
    out1 = OUT_DIR / "fitriana_2022_hapwork_efa.csv"
    long1.to_csv(out1, index=False)
    print(f"fitriana_2022_hapwork_efa: rows={len(long1)} ids={long1['id'].nunique()} "
          f"items={long1['item'].nunique()} resp={long1['resp'].min():.0f}-{long1['resp'].max():.0f}")

    # Field study sample
    url2 = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0261617.s002")
    df2 = pd.read_excel(io.BytesIO(_fetch(url2)))
    df2 = df2.rename(columns={"1. Gender": "cov_gender", "2. Age": "cov_age"})
    df2["id"] = range(1, len(df2) + 1)
    item_cols2 = [c for c in df2.columns if c.startswith("A")]
    cov_cols = ["cov_gender", "cov_age"]
    long2 = df2.melt(id_vars=["id"] + cov_cols, value_vars=item_cols2, var_name="item", value_name="resp")
    long2["resp"] = pd.to_numeric(long2["resp"], errors="coerce")
    long2 = long2.dropna(subset=["resp"]).reset_index(drop=True)
    long2 = long2[["id", "item", "resp"] + cov_cols]
    out2 = OUT_DIR / "fitriana_2022_hapwork_field.csv"
    long2.to_csv(out2, index=False)
    print(f"fitriana_2022_hapwork_field: rows={len(long2)} ids={long2['id'].nunique()} "
          f"items={long2['item'].nunique()} resp={long2['resp'].min():.0f}-{long2['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
