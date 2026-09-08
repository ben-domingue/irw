#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0245078
# DOI: 10.1371/journal.pone.0245078
# Data: S1 Data (xlsx)
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0245078.s001
# License: CC BY 4.0 (PLOS ONE)
#
# Zniradsic & Bernik (2021), "Impact of work-family balance results on
# employee work engagement within the organization". N=247 Slovenian
# employees, online survey.
#
# The deposit has no item codes at all: every column header is the item's
# full English stem, and the five instruments run in fixed blocks with no
# separator. The block boundaries below are the article's Instruments
# section (2.1) read against the header text, and the item counts add up to
# the file exactly: 9 demographics + 9 + 9 + 25 + 4 + 9 = 65 columns.
#
#   cols  9-17  leader support for work-family balance, 9 items (Shinn et
#               al.), 1 (never) - 5 (very often)                     -> LS01-LS09
#   cols 18-26  the same 9 items re-asked about co-workers            -> CS01-CS09
#   cols 27-51  organizational work-family practices, 25 items from the
#               Slovenian Family-Friendly Company certificate measure
#               set, 1-5                                             -> OP01-OP25
#   cols 52-55  work-family balance, 4 items (Brough et al.), 1-5     -> WFB1-WFB4
#   cols 56-64  UWES-9 work engagement, 1-5                           -> UWES1-UWES9
#
# Positional item codes are assigned because the raw headers are unusable as
# item names (up to 120 characters, leading whitespace, and pandas has
# already de-duplicated the repeated co-worker stems with ".1" suffixes). The
# code -> original header mapping is printed by this script and is fully
# recoverable from the deposit's column order, which is what a later item
# text pass needs.
#
# Sentinel filtering: three item responses fall outside the 1-5 scale (a 41
# in the leader block, a 22 and a 55 in the practices block) and are dropped
# as data-entry errors rather than kept as in-range-looking values.
#
# No id column; the row index is the respondent id (247 rows).
#
# Item text: NOT shipped, and again the reason is rights rather than
# availability -- the stems are right there in the headers, in English, and
# there is no label layer to check because the deposit is a plain .xlsx. All
# five blocks are third-party published instruments (Shinn et al.'s
# supervisor support questionnaire, the Family-Friendly Company measure set,
# Brough et al.'s work-family balance scale, and UWES-9, whose wording
# Schaufeli & Bakker license separately). The CC BY licence on this deposit
# covers the authors' responses, not the instruments they administered.
# See BATCH_LOG.md 2026-09-08.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0245078.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# out_name -> (first col, last col exclusive, item-code prefix, zero pad)
SCALES = {
    "znidarsic_2021_leader_support":   (9, 18, "LS", 2),
    "znidarsic_2021_coworker_support": (18, 27, "CS", 2),
    "znidarsic_2021_org_practices":    (27, 52, "OP", 2),
    "znidarsic_2021_wf_balance":       (52, 56, "WFB", 1),
    "znidarsic_2021_uwes":             (56, 65, "UWES", 1),
}

COV_COLS = {
    0: "cov_gender",
    1: "cov_age",
    2: "cov_education",
    3: "cov_company_size",
    4: "cov_job_position",
    5: "cov_work_hours_week",
    6: "cov_work_complexity",
    7: "cov_marital_status",
    8: "cov_children",
}

VALID = {1, 2, 3, 4, 5}


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = requests.get(SI_URL, headers=UA, timeout=120)
    raw.raise_for_status()
    df = pd.read_excel(io.BytesIO(raw.content), sheet_name=0)
    if df.shape[1] != 65:
        raise SystemExit(f"expected 65 columns, got {df.shape[1]}; "
                         "the block boundaries below are positional")

    covs = df.iloc[:, list(COV_COLS)].copy()
    covs.columns = [COV_COLS[i] for i in COV_COLS]
    covs = covs.reset_index(drop=True)
    covs.insert(0, "id", covs.index + 1)
    cov_cols = [c for c in covs.columns if c.startswith("cov_")]

    for out_name, (lo, hi, prefix, pad) in SCALES.items():
        block = df.iloc[:, lo:hi].copy()
        codes = [f"{prefix}{i:0{pad}d}" for i in range(1, hi - lo + 1)]
        for code, header in zip(codes, block.columns):
            print(f"    {out_name} {code} <- {str(header).strip()[:70]}")
        block.columns = codes
        block = block.reset_index(drop=True)
        block.insert(0, "id", block.index + 1)

        long = block.merge(covs, on="id", validate="one_to_one")
        long = long.melt(id_vars=["id"] + cov_cols, value_vars=codes,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[long["resp"].isin(VALID)]
        long = long[["id", "item", "resp"] + cov_cols].reset_index(drop=True)
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
