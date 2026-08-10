#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0283170
# DOI: 10.1371/journal.pone.0283170
#
# Lai et al. (2023) "Influence of artificial intelligence in education on
# adolescents' social adaptability: The mediatory role of social support."
# PLOS ONE. License: CC BY 4.0.
#
# S1 File (SAV, "minimized data", N=1332) has raw item-level responses for
# several scales, one file per scale (datastandard.md "one scale per file"):
#   - Social Adaptability Scale: QZGX1-18 (18 items, 1-5 scale)
#   - Parent-Child Relationship (father report): FUQIN1-20 (20 items, 1-5 scale)
#   - Parent-Child Relationship (mother report): MUQIN1-20 (20 items, 1-5 scale)
#   - Teacher-Student Relationship: SSGX1-7 (7 items, 1-5 scale)
#   - Peer-Relationship Scale: TBGX1-18 (18 items, 1-6 scale)
#
# Scale ranges above are per the article's own Methods text (fetched
# 2026-08-09), not just the raw file's apparent min/max: Parent-Child
# Relationship is documented as an 18-item, 5-point (1-5) scale;
# Teacher-Student Relationship as 7 items, 5-point (1-5); Peer
# Relationship as 18 items, 6-point (1-6). An earlier version of this
# script used the raw file's naive min/max (1-6 for father/mother, 0-6 for
# teacher-student and peer), which shipped a handful of out-of-scale
# values as genuine responses: isolated single stray 0s/6s scattered
# across many items (data-entry artifacts, now excluded), plus FUQIN1
# ("father" item 1) specifically had 62/1319 responses of 6 despite its
# mother-report counterpart (MUQIN1) having zero -- inconsistent with a
# real shared 1-6 scale for that block, so also excluded pending an actual
# codebook. Note the raw file has 20 FUQIN/MUQIN columns but the paper
# describes an 18-item scale; which 2 columns are extra/non-scale
# (possibly reverse-coded duplicates or a different sub-measure) is not
# resolved here -- all 20 are still shipped as-is pending the codebook.
#
# The "Parent-Child Communication Scale" (SHSY1-20) is DELIBERATELY excluded:
# its raw values are inconsistent across items (some items take only
# {-2,0,2}, others {-2,0,2,3}, others {-2,0,2,4,5}) rather than a shared
# ordinal code set -- looks like a scoring/export artifact rather than a
# clean Likert scale, so it's not safe to ship as `resp` without the
# original codebook. -2 elsewhere is a clear missing-data sentinel.
# AIEdYes0No1 (single dichotomous item) is not part of any multi-item scale
# and is excluded (would violate the no-single-item-scale rule).

import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0283170.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "SCHOOLNAME": "cov_school",
    "GENDER": "cov_gender",
    "GRADE": "cov_grade",
    "AGE": "cov_age",
}

SCALES = {
    "lai_2023_social_adaptability": ([f"QZGX{i}" for i in range(1, 19)], 1, 5),
    "lai_2023_parent_relation_father": ([f"FUQIN{i}" for i in range(1, 21)], 1, 5),
    "lai_2023_parent_relation_mother": ([f"MUQIN{i}" for i in range(1, 21)], 1, 5),
    "lai_2023_teacher_student_rel": ([f"SSGX{i}" for i in range(1, 8)], 1, 5),
    "lai_2023_peer_relationship": ([f"TBGX{i}" for i in range(1, 19)], 1, 6),
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/_lai_2023.sav"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df, _meta = pyreadstat.read_sav(tmp)
    return df


def convert():
    print("Fetching S1 File (SAV)...")
    raw = fetch_raw()
    df = raw.rename(columns=COV_RENAME)
    # Source ID column is not unique -- use row index instead.
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    assert df["id"].is_unique, "id column not unique"

    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    os.makedirs(OUT_DIR, exist_ok=True)
    for out_name, (item_cols, lo, hi) in SCALES.items():
        sub = df[["id"] + cov_cols + item_cols].copy()
        for c in item_cols:
            sub[c] = pd.to_numeric(sub[c], errors="coerce")
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)].reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"{out_name}.csv"
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
