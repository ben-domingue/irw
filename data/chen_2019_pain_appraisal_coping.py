#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0215087
# DOI: 10.1371/journal.pone.0215087
# Supporting Information: https://doi.org/10.1371/journal.pone.0215087.s001
#
# Cold-pressor pain-appraisal study, N=235. Two confirmed raw-item scales
# (confirmed via the paper's Measures section text, not just column
# naming):
#   cdrsc -- Connor-Davidson Resilience Scale-Chinese (CDRS-C, 10 items,
#            the paper's baseline covariate measure), 0="never" to
#            4="almost always".
#   csq   -- task-specific Coping Strategies Questionnaire (CSQ, 27
#            items), 0-6.
# pse01-08/appraisal01,a02-06/nrs01-03/hs01-06 (37 columns total) were
# left unprocessed -- no SPSS variable labels and no clearly matching
# instrument description found in the paper's available text, so their
# exact construct/scoring can't be confirmed. resilience/tolerance/
# PSEQ1/PSEQ2/PSE_change/challenge/threat/intensity/reinterpret/divert/
# selfstatement/ignore/catastrophize/cognitivecoping are derived
# subscale/summary scores, excluded regardless.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0215087.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"gender": "cov_sex", "age": "cov_age", "race": "cov_race",
              "appraisal_conditions": "cov_condition"}

RS_COLS = [f"rs{i:02d}" for i in range(1, 11)]
CSQ_COLS = [f"csq{i:02d}" for i in range(1, 28)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"ID": "id", **COV_RENAME})


def melt_scale(df, cov_cols, item_cols, out_name):
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

    melt_scale(df, cov_cols, RS_COLS, "chen_2019_cdrsc")
    melt_scale(df, cov_cols, CSQ_COLS, "chen_2019_csq")


if __name__ == "__main__":
    convert()
