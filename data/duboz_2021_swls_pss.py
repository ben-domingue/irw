#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0252134
# DOI: 10.1371/journal.pone.0252134
# Supporting Information: https://doi.org/10.1371/journal.pone.0252134.s001
#
# Two locations pooled (Dakar, Tessekere); Id is unique within Tessekere
# but has 7 exact full-row duplicate pairs within Dakar (confirmed:
# duplicated on every column, not just Id) -- deduplicated, then a
# Location-Id composite used as id. Raw file has the 5-item Satisfaction
# With Life Scale and the 10-item Perceived Stress Scale (PSS-10). Social
# Support and Self-rated Health are each a single aggregate/summary
# variable, not raw items -- excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0252134.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Location": "cov_location", "Sex": "cov_sex", "Age": "cov_age",
              "Education Level": "cov_education", "Material Well-Being": "cov_material_wellbeing"}

SWLS_COLS = [f"Satisfaction with life scale Q{i}" for i in range(1, 6)]
PSS_COLS = [f"Stress{i}" for i in range(1, 11)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.drop_duplicates(subset=[c for c in df.columns if c != "Id"] + ["Id"], keep="first")
    df = df.rename(columns=COV_RENAME)
    df["id"] = df["cov_location"] + "-" + df["Id"].astype(str)
    return df.drop(columns=["Id"])


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_scale(df, cov_cols, SWLS_COLS, "duboz_2021_swls")
    melt_scale(df, cov_cols, PSS_COLS, "duboz_2021_pss10")


if __name__ == "__main__":
    convert()
