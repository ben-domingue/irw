#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0307744
# DOI: 10.1371/journal.pone.0307744
# Skurvydas et al. (2024), "Leisure-time physical activity improves happiness,
# health, and mood profile better than work-related physical activity".
# S1 Dataset. CC BY 4.0. N=1140 Lithuanian adults.
#
# The S1 Dataset xlsx contains mostly PRE-AGGREGATED per-person totals (IPAQ
# physical-activity minutes, SSREIT emotional-intelligence total, PSS-10
# perceived-stress total, single-item subjective health/overeating/happiness
# ratings) -- not raw items, so those columns are excluded per datastandard.md
# ("Subscale aggregate columns", "no single-item scales").
#
# The ONE genuinely raw item-level instrument in this file is the 4-item
# Vigour subscale of the Brunel Mood Scale (BRUMS): "Energetic", "Active",
# "Lively", "Alert", each rated 0-4 ("0 = not at all" ... "4 = extremely").
# The header spans two Excel rows (a merged "Vigour" banner over the 4 item
# columns) -- read with header=None and skiprows=2 per datastandard.md's
# "Excel files with header rows above the column names". A legend row
# ("0 = not at all", etc.) and a blank row are embedded near the end of the
# sheet; both are dropped when id/resp are coerced to numeric.
# No PII (no names/emails/DOB); SBP/BMI/age retained as covariates are
# ordinary survey covariates, not identifiers.
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

from pathlib import Path
import io

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0307744.s002")

ITEM_COLS = ["energetic", "active", "lively", "alert"]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()

    df = pd.read_excel(io.BytesIO(r.content), header=None, skiprows=2)
    df = df.iloc[:, :21]
    df.columns = [
        "id", "cov_gender", "cov_age", "cov_bmi", "cov_education",
        "cov_training_experience", "cov_residence", "mvpaw", "mvpah",
        "mvpalt", "mvpatotal", "cov_subjective_health", "sbp", "overeat",
        "happy", "energetic", "active", "lively", "alert", "ei", "ps",
    ]

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df), "id column not unique"

    cov_cols = ["cov_gender", "cov_age", "cov_bmi", "cov_education",
                "cov_training_experience", "cov_residence",
                "cov_subjective_health"]

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 0) & (long["resp"] <= 4)]

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    out_name = "skurvydas_2024_vigour.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
