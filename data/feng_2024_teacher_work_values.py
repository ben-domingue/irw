#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0310078
# DOI: 10.1371/journal.pone.0310078
# Data: S1 Dataset (SPSS .sav)
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0310078.s001
# License: CC BY 4.0 (PLOS ONE)
#
# Feng et al. (2024), "The impact of work values on the professional
# development of primary and secondary school teachers". 873 valid responses
# from primary and secondary school teachers in Guangdong Province, China,
# August-October 2023.
#
# Four scales, all 5-point Likert, all complete (no missing item responses).
# Item counts match the article's Measures section exactly:
#
#   WV1-WV27  work values scale (Xu Xingchun), 27 items / 7 dimensions, 1-5
#   TP1-TP21  professional development of primary and secondary school
#             teachers (Chen Jingjun et al.), 21 items / 5 dimensions, 1-5
#   WI1-WI17  Utrecht Work Engagement Scale, Chinese version (Zhang Yiwen &
#             Gan Yiqun), 17 items, 1-5
#   OS1-OS24  perceived organizational support, 24 items, 1-5
#
# Excluded as composites, not responses: WV_mean / WI_mean / OS_mean /
# PD_mean, the named Chinese dimension-score columns, OS_1..OS_3, the
# FAC*_* SPSS regression factor scores, and the 化* transformed variables.
#
# The person id is the deposit's own 序号 ("serial number") column, verified
# unique across all 873 rows.
#
# Item text: not shipped. Both label levels were checked with pyreadstat.
# Variable labels exist for only 29 of 161 columns and all 29 are SPSS
# artefacts ("REGR factor score 1 for analysis 1") -- none of the WV/TP/WI/OS
# item columns carries one. Value labels are present and complete for the
# item columns, but they hold the response options (完全不符合 ... 完全符合),
# not the stems. The stems are in the four source instruments' own
# publications, not in this deposit.

from __future__ import annotations

import io
import re
from pathlib import Path
import tempfile

import pandas as pd
import pyreadstat
import requests

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "automated_finding"))
from irw_triage_updated import run_qc  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0310078.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "性别": "cov_gender",          # gender
    "年龄": "cov_age",             # age band
    "教龄": "cov_teaching_years",  # years teaching
    "学历": "cov_education",       # highest qualification
    "学校级别": "cov_school_level",  # school level
    "村乡县": "cov_locality",       # village / township / county
}

SCALES = {
    "feng_2024_work_values":              r"WV\d+",
    "feng_2024_professional_development": r"TP\d+",
    "feng_2024_work_engagement":          r"WI\d+",
    "feng_2024_org_support":              r"OS\d+",
}
VALID = {1, 2, 3, 4, 5}


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = requests.get(SI_URL, headers=UA, timeout=180)
    raw.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(raw.content)
        tmp.flush()
        df, _meta = pyreadstat.read_sav(tmp.name)

    df = df.rename(columns={"序号": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    if df["id"].nunique() != len(df):
        raise SystemExit("序号 is not unique; fall back to the row index")
    df["id"] = df["id"].astype(int)
    df = df.rename(columns=COV_RENAME)
    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    for out_name, pattern in SCALES.items():
        item_cols = [c for c in df.columns if re.fullmatch(pattern, str(c))]
        if not item_cols:
            raise SystemExit(f"no item columns matched {pattern}")
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[long["resp"].isin(VALID)]
        long = long[["id", "item", "resp"] + cov_cols].reset_index(drop=True)
        checks = run_qc(long)
        failed = [c for c in checks if c.status == "fail"]
        assert not failed, (out_name, [(c.name, c.detail) for c in failed])
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
