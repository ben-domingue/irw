#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0233359
# DOI: 10.1371/journal.pone.0233359
# Supporting Information: https://doi.org/10.1371/journal.pone.0233359.s001
#
# Automated triage flagged this as low-confidence id mapping; id is
# clean/unique (371/371). Raw file has secf_1m..secf_10m (10 items, 0-3
# scale, financial-security-related). f1-f4 are continuous IRT/factor
# scores (not raw items -- hundreds of distinct non-integer values), and
# fdsecureraw/dpsscore are aggregate sums -- excluded. A separate small
# item set (SECA_7, SECA_9, SECA_11, SECJ_1) appears to be a scattered
# leftover from the CFPB Financial Well-Being item bank but is far too
# incomplete (4 non-consecutive items out of that bank's much larger set)
# to be usable as a coherent instrument -- not included.
#
# NOTE (irw#2197): the ten items are the CES-D-10, mapped to canonical
# positions during item-text extraction (batch_220). secf_4m ("I felt that
# everything I did was an effort") is detached from the scale in this sample:
# item-rest r = 0.07 (the other nine 0.27-0.73), r = -0.18 and -0.08 with the
# two positive-affect items, and the highest mean of the ten (1.68). Its
# position rests on canonical CES-D-10 order plus endorsement rank, not on any
# correlational signal, so it is the weakest of the ten assignments: either the
# item performs poorly here or the deposit's column order departs from the
# canonical order at this position, and the data do not say which. Separately,
# secf_5m ("hopeful about the future") and secf_8m ("happy") are stored
# already reverse-scored in the deposit; the plain row sum reproduces the
# authors' dpsscore exactly. Data are as deposited; nothing is recoded here.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0233359.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# #2198: the ten secf_*m items are the CES-D-10, not a financial-security
# scale: rowSums(secf_1m..secf_10m) equals the study's own dpsscore for all 371
# respondents, and the items read "I felt depressed", "I felt lonely", "My sleep
# was restless". So the table ships as weida_2020_cesd10 (it was
# weida_2020_financial_security until 2026-09; same rows). The script keeps its
# old filename, which the other notes cite.
COV_RENAME = {"GENDER": "cov_gender", "age": "cov_age", "race": "cov_race"}
ITEM_COLS = [f"secf_{i}m" for i in range(1, 11)]
OUT_NAME = "weida_2020_cesd10"
# Two respondents' age is -83 in the deposit; the live table has had those
# nulled since 2026-09-03 (irw_validate/repair_cov_age.py, #1779), so the
# script now does the same.
AGE_RANGE = (0, 120)


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_sas(io.BytesIO(r.content), format="sas7bdat")


def convert():
    df = fetch_data()
    df = df.rename(columns={"SUBJECT": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]
    lo, hi = AGE_RANGE
    long.loc[~long["cov_age"].between(lo, hi), "cov_age"] = float("nan")
    # The SAS file stores every number as a float; write the integer-valued
    # columns as integers ("103", not "103.0"), as the live table has them.
    for c in ["id", "cov_gender", "cov_race"]:
        long[c] = long[c].astype("Int64")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{OUT_NAME}.csv", index=False)
    print(f"{OUT_NAME}.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
