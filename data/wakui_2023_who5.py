#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0294357
# DOI: 10.1371/journal.pone.0294357
# Supporting Information: https://doi.org/10.1371/journal.pone.0294357.s007
#
# WHO-5 Well-Being Index (5 items, 0-5 scale), RCT of aroma seals vs
# placebo on mask-wearing stress, measured at baseline and 2-week
# follow-up (Time 0/1) -- kept as a `wave` column since these are the
# same 61 respondents at two timepoints. The paper's own DASS-21
# Supporting Information file (S5) turned out to contain only
# already-computed subscale totals (Total/Anxiety/Depression/Stress), not
# raw per-item responses, so DASS-21 is not shipped from this paper (see
# datastandard.md's "Verifying a continuous-looking column is actually a
# raw response"). "Group" (1/2) is kept as cov_group rather than `treat`
# because the article text does not state which numeric code is the aroma
# (treatment) arm and which is placebo -- mislabeling treat/control would
# be worse than leaving it as an unmapped covariate.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0294357.s007")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

WHO5_ITEMS = ["W1", "W2", "W3", "W4", "W5"]


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), header=2)
    df = df.rename(columns={"ID": "id", "Group": "cov_group", "Time": "wave"})
    df["wave"] = pd.to_numeric(df["wave"], errors="coerce") + 1  # 0/1 -> 1/2 (larger = later)

    cov_cols = ["cov_group"]
    long = df.melt(id_vars=["id", "wave"] + cov_cols, value_vars=WHO5_ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 0) & (long["resp"] <= 5)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "wakui_2023_who5.csv"
    long.to_csv(out_path, index=False)
    print(f"wakui_2023_who5: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
