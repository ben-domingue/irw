#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0354305
# DOI: 10.1371/journal.pone.0354305
# Paper: Al-Daraiseh R, Ta'an W, Mukattash T, et al. (2026). Development of a
#   scale for measuring the perception of artificial intelligence among mental
#   health consumers. PLOS ONE 21(7): e0354305.
# Data: S1 File (journal.pone.0354305.s001, "Row data"), 431 adult consumers of
#   the Jordanian mental-health care system.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 4, BATCH_LOG.md).
#
# ONE output table, al_daraiseh_2026_aip: the 20-item Artificial Intelligence
# Perception (AIP) scale, A1..A20, 1 strongly disagree .. 5 strongly agree
# (the S2 File questionnaire). Four factors of five items: A1-A5 readiness and
# acceptance, A6-A10 perceived importance and benefits, A11-A15 perceived risk,
# A16-A20 perceived challenges. Kept AS DEPOSITED: the paper says negatively
# worded items were reverse-coded before analysis, but the deposit's own
# subscale totals (Jahizeh_AI .. Masa3eb_AI) equal the raw sums of these values
# on every row, so the file does not tell us which direction A11-A20 run in.
# Covariate: gender (1 male / 2 female -- 191/240 reproduces the paper's
#   44.3% male / 55.7% female).
# Dropped: Marital, Education, Income, PlaceofBirth, Employ, Insurance,
#   ChronicD, MentalD (constant), MentlType (bare integer codes; Table 4 gives
#   the counts but not the code order), ChronicType (free-typed comma lists of
#   condition codes), and the ten subscale/total columns (derived).
# `id` is the row index (the sheet has no id column).
#
# Item text: NOT SHIPPED. The English wording of all 20 items is in S2 File
#   (journal.pone.0354305.s002), but the scale was "prepared and circulated in
#   Arabic", and the Arabic wording is not in the deposit; the sheet has column
#   codes only (no labels at any level). instrument: study-authored (AIP,
#   Al-Daraiseh et al. 2026).

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ALDARAISEH_RAW", "journal.pone.0354305.s001.xlsx")
NAME = "al_daraiseh_2026_aip"


def convert():
    df = pd.read_excel(RAW, sheet_name="Row data")
    assert df.shape == (431, 41), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == ["ChronicType"]
    items = [f"A{i}" for i in range(1, 21)]
    assert df["Gender"].value_counts().to_dict() == {2: 240, 1: 191}
    df["id"] = range(1, len(df) + 1)
    df["cov_gender"] = df["Gender"].map({1: "male", 2: "female"})
    long = df[["id", "cov_gender"] + items].melt(id_vars=["id", "cov_gender"], var_name="item", value_name="resp")
    assert long["resp"].notna().all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) == {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp", "cov_gender"]]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    dropped = ["Marital", "Education", "Income", "PlaceofBirth", "Employ", "ChronicD", "ChronicType", "Insurance",
               "MentalD", "MentlType", "Jahizeh_AI", "Ahmieh_AI", "Ma5ater_AI", "Masa3eb_AI", "AITotal",
               "Jahizeh_AI_MEAN", "Ahmieh_AI_MEAN", "Ma5ater_AI_MEAN", "Masa3eb_AI_MEAN", "AITotal_MEAN"]
    assert set(df.columns) - {"id", "cov_gender"} == set(items) | {"Gender"} | set(dropped)
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}; dropped {dropped}")


if __name__ == "__main__":
    convert()
