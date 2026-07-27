#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0231628
# DOI: 10.1371/journal.pone.0231628
# Supporting Information: https://doi.org/10.1371/journal.pone.0231628.s001
#
# Automated triage flagged this as low-confidence id mapping; `Code` is
# actually clean and unique (1853/1853). Raw file has the 23-item
# Behavioral Regulation in Exercise Questionnaire (BREQ-3) and a 10-item
# Resilience Scale. BREQ's 7 subscale SUM columns (Intrinsic, Extrinsic,
# ..., Amotivation) and the resilience total (GRS) are excluded as
# aggregates. BREQ items are text-coded with an unusual middle-category
# label ("Sometimes" in place of a neutral/undecided midpoint, likely a
# translation artifact) but a consistent 5-point agreement set across all
# 23 items -- mapped Strongly disagree=1 .. Totally agree=5.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0231628.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MAP_BREQ = {"Strongly disagree": 1, "Somewhat disagree": 2, "Sometimes": 3,
            "Somewhat agree": 4, "Totally agree": 5}

COV_RENAME = {"Age": "cov_age", "Gender": "cov_gender", "Height": "cov_height",
              "Weight": "cov_weight", "BMI": "cov_bmi", "Injuries": "cov_injuries"}

BREQ_COLS = [f"BREQ{i}" for i in range(1, 24)]
RS_COLS = [f"RS{i}" for i in range(1, 11)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns={"Code": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=BREQ_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(MAP_BREQ)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "leon_guereno_2020_breq.csv", index=False)
    print(f"leon_guereno_2020_breq.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")

    long2 = df.melt(id_vars=["id"] + cov_cols, value_vars=RS_COLS,
                     var_name="item", value_name="resp")
    long2["resp"] = pd.to_numeric(long2["resp"], errors="coerce")
    # The Resilience Scale is 1-5; a "0" appears only on RS7 (4 of ~1846
    # RS7 responses) and nowhere on the other 9 items -- a real scale
    # point would show up consistently across items, not isolated to one.
    # Data-entry error, not a valid response.
    long2.loc[long2["resp"] == 0, "resp"] = float("nan")
    long2 = long2.dropna(subset=["resp"]).reset_index(drop=True)
    long2["resp"] = long2["resp"].astype(int)
    long2 = long2[["id", "item", "resp"] + cov_cols]
    long2.to_csv(OUT_DIR / "leon_guereno_2020_resilience.csv", index=False)
    print(f"leon_guereno_2020_resilience.csv: ids={long2['id'].nunique()} "
          f"items={long2['item'].nunique()} resp={long2['resp'].min()}-{long2['resp'].max()}")


if __name__ == "__main__":
    convert()
