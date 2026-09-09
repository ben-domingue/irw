#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0279984
# DOI: 10.1371/journal.pone.0279984
# Data: S1 File (SPSS .sav)
#   https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0279984.s001
# License: CC BY 4.0 (PLOS ONE)
#
# Tatala et al. (2023), "Loneliness and time abroad in Polish migrants in the
# UK: Protective role of religious experience". N=200 Polish migrants in the
# UK. Two instruments, both complete (no missing item responses):
#
#   UCLA1-UCLA20  Revised UCLA Loneliness Scale (R-UCLA), 20 items, 1-4
#   RES1-RES17    Religious Experience Scale, 17 items, 1-5
#
# Excluded as composites, not responses: Intimate_others_Mean,
# Social_others_Mean, Belonging_Mean, Negative_experience_dimension,
# Positive_experience_dimension. Also excluded are the four single-question
# religiosity ratings (Importance, Negative_experiences, Godssupport,
# Entrusting_in_God, Openess_to_God), which are standalone questions rather
# than members of either scale; they are carried as covariates instead.
#
# No id column in the deposit; the row index is the respondent id (200 rows).
#
# Item text: NOT shipped, and the reason is rights, not availability -- this
# is the one deposit in the batch where the wording is fully in hand. Both
# label levels were checked: variable labels are present and complete for all
# 54 columns and carry the verbatim English stems ("I lack companionship.",
# "Despite indifference I experience, I remain with God."); value labels are
# absent for every item column, so the response-option wording is not here.
# The 20 UCLA stems are the Revised UCLA Loneliness Scale (Russell 1996), a
# third-party copyrighted instrument -- the CC BY licence on this deposit
# covers the authors' data, not Russell's items. The 17 RES stems are the
# Religious Experience Scale, on which this paper's first author is an
# author; whether that makes them ours to republish is ben-domingue's call,
# not this script's, so both blocks are held together rather than splitting
# the deposit on a judgment call. See BATCH_LOG.md 2026-09-08.

from __future__ import annotations

import re
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "automated_finding"))
from irw_triage_updated import run_qc  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0279984.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Place_of_residents_PL": "cov_residence_poland",
    "Type_of_relationship":  "cov_marital_status",
    "Place_of_residents_ENG": "cov_living_arrangement",
    "Time_abroad":           "cov_time_abroad",
    "English_language":      "cov_english_level",
    "Religious_community":   "cov_religious_community",
    "Church_access":         "cov_church_access",
}

SCALES = {
    "tatala_2023_ucla_loneliness":    (r"UCLA\d+", {1, 2, 3, 4}),
    "tatala_2023_religious_experience": (r"RES\d+", {1, 2, 3, 4, 5}),
}


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = requests.get(SI_URL, headers=UA, timeout=120)
    raw.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(raw.content)
        tmp.flush()
        df, _meta = pyreadstat.read_sav(tmp.name)

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COV_RENAME)
    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    for out_name, (pattern, valid) in SCALES.items():
        item_cols = [c for c in df.columns if re.fullmatch(pattern, str(c))]
        if not item_cols:
            raise SystemExit(f"no item columns matched {pattern}")
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[long["resp"].isin(valid)]
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
