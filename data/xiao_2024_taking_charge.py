#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0315916
# DOI: 10.1371/journal.pone.0315916
# Data: S1 Dataset (xlsx)
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0315916.s001
# License: CC BY 4.0 (PLOS ONE)
#
# Xiao et al. (2024), "The impact of hierarchical plateau on civil servants'
# taking charge behavior". 307 matched two-wave questionnaires from civil
# servants in the Pearl River Delta, Guangdong, China (the paper analyses 286
# after excluding invalid responses; the deposit carries all 307 matched rows,
# which is what is shipped here).
#
# Four scales, each measured once, so no `wave` column: the two survey stages
# 20 days apart carried different instruments (stage 1: demographics, HP, TM;
# stage 2: WE, TC) rather than repeating the same items.
#
#   HP1-HP4    hierarchical plateau, Allen et al. 4-item brief career
#              plateau scale, 1-5
#   WE1-WE9    UWES-9 work engagement (vigor/dedication/absorption), 1-5
#   TM1-TM15   Mindful Attention Awareness Scale (MAAS) trait mindfulness,
#              1-6. 30 item-responses are blank and are dropped.
#   TC1-TC4    taking charge behavior, Morrison & Phelps items as used by
#              Parker & Collins, 1-5
#
# No id column in the deposit; the row index is the respondent id (one row =
# one respondent, verified: 307 rows, and the four blocks are aligned).
#
# Item text: not shipped -- the deposit carries positional codes only (HP1,
# WE1, ...), no variable or value labels of any kind (it is an .xlsx, not a
# .sav). The stems are in the published source instruments (Allen et al.'s
# career plateau scale, UWES-9, MAAS, Morrison & Phelps' taking charge
# scale), not in this deposit or in the article, so shipping them would mean
# republishing four third-party instruments.

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0315916.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Education": "cov_education",
    "Tenure": "cov_tenure",
    "Job category": "cov_job_category",
}

# out_name -> (item-column regex, valid resp range)
SCALES = {
    "xiao_2024_hierarchical_plateau": (r"HP\d+", (1, 5)),
    "xiao_2024_work_engagement":      (r"WE\d+", (1, 5)),
    "xiao_2024_trait_mindfulness":    (r"TM\d+", (1, 6)),
    "xiao_2024_taking_charge":        (r"TC\d+", (1, 5)),
}


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = requests.get(SI_URL, headers=UA, timeout=120)
    raw.raise_for_status()
    df = pd.read_excel(io.BytesIO(raw.content))

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COV_RENAME)
    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    for out_name, (pattern, (lo, hi)) in SCALES.items():
        item_cols = [c for c in df.columns if re.fullmatch(pattern, str(c))]
        if not item_cols:
            raise SystemExit(f"no item columns matched {pattern}")
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
        long = long[["id", "item", "resp"] + cov_cols].reset_index(drop=True)
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
