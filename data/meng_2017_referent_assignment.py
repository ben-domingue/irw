#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0187368
# DOI: 10.1371/journal.pone.0187368
# Supporting Information: https://doi.org/10.1371/journal.pone.0187368.s001
#
# Children's referent-assignment task: 74 children x 2 blocks x 2 trials,
# each producing 5 raw binary correctness scores -- EQ (explicit
# question), AQ (ambiguous question, same trial), EQ2 (explicit question
# after a topic shift), AQ2 (ambiguous question after the shift), AQ3
# (repeated ambiguous question, consistency check). The paper's Methods
# text spells out that Base-Assignment/Shift/Re-Assignment/Follow-RA
# (the columns the automated triage flagged as "items") are each a
# derived AND of two of these raw scores (e.g. "Base-Assignment ... coded
# as 1 when both the EQ and AQ were correct") -- composites, not raw
# responses, and are dropped. `wave` encodes the block/trial order
# (block 1 trial 1 = wave 1, ..., block 2 trial 2 = wave 4); duplicate
# id+item pairs across trials are expected and valid with `wave` present.
# LPS and CES are constant within each child across all 4 rows and are
# carried as covariates (LPS's 0-8 range is consistent with the paper's
# forward digit-span task, used as the phonological-loop capacity
# measure, though the source doesn't spell out the CES abbreviation).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0187368.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["EQ", "AQ", "EQ2", "AQ2", "AQ3"]
COV_RENAME = {"month": "cov_age_months", "sex": "cov_sex", "pattern": "cov_pattern",
              "LPS": "cov_lps", "CES": "cov_ces"}
WAVE_MAP = {(1, 1): 1, (1, 2): 2, (2, 1): 3, (2, 2): 4}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns=COV_RENAME)
    df["wave"] = df.apply(lambda row: WAVE_MAP[(row["block"], row["trial"])], axis=1)

    cov_cols = list(COV_RENAME.values())
    long = df.melt(id_vars=["id", "wave"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 0) & (long["resp"] <= 1)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "meng_2017_referent_assignment.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
