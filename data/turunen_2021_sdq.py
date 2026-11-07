#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0249112
# DOI: 10.1371/journal.pone.0249112
# Paper: Turunen T, Poskiparta E, Salmivalli C, Niemi P, Lerkkanen M-K (2021).
#   Longitudinal associations between poor reading skills, bullying and
#   victimization across the transition from elementary to middle school.
#   PLoS ONE 16(3): e0249112.
# Data: PLOS Supporting Information S1 File (journal.pone.0249112.s001, SPSS
#   .sav with variable and value labels), 1,824 pupils of a Finnish community
#   cohort followed from kindergarten; three measurement points T1-T3 (Grades
#   6, 7 and 9).
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 3.
#
# ONE output table: turunen_2021_sdq -- the Finnish self-report Strengths and
#   Difficulties Questionnaire, 25 items at each of three waves, 0-2 ("0 = not
#   true; 1 = somewhat true; 2 = certainly true", the paper). `wave` 1-3 =
#   T1-T3. Item codes are the deposit's column names without the wave tag:
#   sdq1 ... sdq25. Items 7, 11, 14, 21 and 25 -- the SDQ's positively worded
#   items -- are deposited ALREADY REVERSED, with an "r" suffix (sdq7T1r, and
#   the deposit's own subscale means use the r columns); their codes keep it
#   (sdq7r, sdq11r, sdq14r, sdq21r, sdq25r) so the direction is visible. The
#   value labels attached to the items (1-3) do not match the stored 0-2
#   codes, which match the paper's 0-2 scoring.
#   377 of the 136,800 SDQ cells hold 0.5 or 1.5 (162 pupils). They are not
#   mean-imputed (each column's mean is far from its half-point values) and
#   read as a mark between two boxes; the paper documents no half points, so
#   those cells are dropped (datastandard.md, "No imputed values").
# `cluster_id` is the pupil's classroom at T1 (groidT1).
# Dropped: the reading-test sum scores and their z-scores and means (rtl2S*,
#   difw*, ly6/ly7*, Zrtl2S*, Zdifw*, tread*); the two single bullying items
#   per wave (bullfr*, bullse*); the SDQ subscale means (mextwo7*, memot*).
# `id` is the row index (the deposit has no pupil id).
#
# Item text: NOT SHIPPED. Variable labels say only "Strengths and
#   difficulties, item k"; the SDQ is a published instrument (Goodman).

import os
import re
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0249112.s001"
RAW = os.environ.get("TURUNEN_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
REVERSED = {7, 11, 14, 21, 25}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        src = os.path.join(OUT_DIR, "_turunen_tmp.sav")
        open(src, "wb").write(r.content)
    df, meta = pyreadstat.read_sav(src)
    if not RAW:
        os.remove(src)
    return df, meta


def convert():
    df, meta = load()
    assert df.shape == (1824, 106), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and not txt
    sdq = {}
    for c in df.columns:
        m = re.fullmatch(r"sdq(\d+)T([123])(r?)", c)
        if m:
            k, w, r = int(m.group(1)), int(m.group(2)), m.group(3)
            assert (r == "r") == (k in REVERSED), c
            sdq[c] = (f"sdq{k}{r}", w)
    assert len(sdq) == 75
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cluster_id"] = df["groidT1"]
    parts = []
    for c, (item, w) in sdq.items():
        p = df[["id", "cluster_id"]].copy()
        p["item"], p["resp"], p["wave"] = item, df[c], w
        parts.append(p)
    long = pd.concat(parts, ignore_index=True)
    long = long[long["resp"].notna()].copy()
    half = (long["resp"] % 1) != 0
    assert set(long.loc[half, "resp"]) <= {0.5, 1.5} and half.sum() == 377, half.sum()
    long = long[~half].copy()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {0, 1, 2}
    long["cluster_id"] = long["cluster_id"].astype("Int64")
    long = long[["id", "item", "resp", "wave", "cluster_id"]]
    assert not long.duplicated(["id", "item", "wave"]).any()
    items = sorted(long["item"].unique())
    checks = run_qc(long, permitted_values={c: [0, 1, 2] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:150]}")
    long.to_csv(os.path.join(OUT_DIR, "turunen_2021_sdq.csv"), index=False)
    print(f"turunen_2021_sdq: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"waves={sorted(long['wave'].unique())}")


if __name__ == "__main__":
    convert()
