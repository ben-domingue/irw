#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0350327
# DOI (correction, which carries the corrected data): 10.1371/journal.pone.0350327
# DOI (original article): 10.1371/journal.pone.0325777
# Paper: Lena, O., Gjini, E., & Todri, J. (2025). Translation, cross-cultural
#   adaptation, validity and reliability of the inaugural Albanian
#   Roland-Morris Disability Questionnaire in Albanian population with low
#   back pain. PLOS ONE 20(7): e0325777. Corrected by The PLOS ONE Editors
#   (2026), PLOS ONE 21(5): e0350327, which supplied an updated S1 File.
# Data: journal.pone.0350327.s001 (S1 File, .xlsx), 202 rows x 57 columns
#   under a TWO-ROW header.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 200 Albanian patients with low back pain and related diagnoses.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# ONE output table, 24 items, 9,576 responses. THE DATA COMES FROM THE
# CORRECTION, NOT THE ORIGINAL ARTICLE: the 2026 correction notice exists in
# part to supply an updated S1 File, so this is the corrected dataset and the
# provenance records both DOIs.
#
# EVAL1 AND EVAL2 ARE TEST AND RETEST, AND THE DEPOSIT'S OWN TOTAL PROVES
# WHICH IS WHICH. The 48 item columns are Q1EVAL1..Q24EVAL2 and nothing in
# the file says what EVAL means. Summing the 24 EVAL1 columns reproduces the
# deposit's `RMDQTotal` on 100% of complete rows; summing the EVAL2 columns
# reproduces it on 29%. So EVAL1 is the administration the published total
# was computed from -- the test -- and EVAL2 is the retest the reliability
# analysis uses. `wave` carries that as "test" and "retest". Asserted, so a
# relabelled deposit would fail here rather than silently swap the occasions.
#
# THE INSTRUMENT IS THE ROLAND-MORRIS DISABILITY QUESTIONNAIRE, 24 binary
# items, which matches the deposit exactly: Q1..Q24, every value 0 or 1. That
# agreement is itself a check -- a 24-item 0/1 block in a paper validating a
# 24-item 0/1 instrument leaves nothing to infer.
#
# TWO NON-PARTICIPANT ROWS ARE DROPPED. The sheet ends with an explanatory
# note about the age bands written straight into a data row ("Note: age
# range 55-60 include ages between 56-60 ...") plus its continuation; both
# are removed by requiring the participant number to be numeric. 200 participant rows remain, matching the
# correction's stated sample, of which one has incomplete item data -- that
# respondent is KEPT and only their missing cells are dropped.
#
# THE AGE BANDS CONTAIN TWO TYPOS AND SHIP AS DEPOSITED. Alongside the
# regular five-year bands (50-55, 55-60, ... 85-90) the column holds '65-75'
# and '80-75', which the deposit's own note does not cover. They are left
# exactly as found: silently folding '80-75' into '80-85' would be inventing
# a value. Flagged here and in the table description.
#
# COVARIATES: gender (the deposit's own Male/Female labels), age band,
# diagnosis (six named conditions -- back pain, lumbar discal hernia, lumbar
# trauma, lumbar fracture, arthrosis, coxo-femoral luxation), pain duration,
# weekly physical activity, and the VAS pain total. The two derived totals
# (RMDQTotal, and VASTotal which is a single-item scale rather than a sum)
# are not items: RMDQTotal is dropped as derived, VASTotal ships as a
# covariate because it is a separate measurement rather than a summary of
# these items.
#
# Item text: NOT SHIPPED. The RMDQ is Roland & Morris's instrument, not the
# authors'; the correction adds an S2 File holding the Albanian version, but
# an Albanian translation of a third-party questionnaire is not ours to
# redistribute and the deposit's columns carry no wording in any case.
# Registered as a hold.
#
# PII: screened. The string columns are gender, age band and diagnosis, each
# a closed vocabulary; no names, dates or free text ship (the one free-text
# cell in the file is the explanatory note row, which is dropped).

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LENA_RAW", "journal.pone.0350327_S1_File.xlsx")

TABLE = "lena_2025_rmdq_albanian"
N_PARTICIPANTS = 200
N_ITEMS = 24
EVAL1 = [f"Q{i}EVAL1" for i in range(1, N_ITEMS + 1)]
EVAL2 = [f"Q{i}EVAL2" for i in range(1, N_ITEMS + 1)]
COVS = {"Gender": "cov_gender", "Age range": "cov_age_band",
        "Diagnosis": "cov_diagnosis",
        "PainDurationDayHours": "cov_pain_duration",
        "PhysicalActivityHoursWeek": "cov_physical_activity",
        "VASTotal": "cov_vas_pain"}


def convert():
    df = pd.read_excel(RAW, header=1).dropna(how="all")
    df.columns = [str(c).strip() for c in df.columns]

    # participant rows only -- the sheet ends with an explanatory note
    # written into a data row
    num_id = pd.to_numeric(df["Items"], errors="coerce")
    notes = df[num_id.isna()]
    assert len(notes) == 2, (
        f"{len(notes)} non-participant rows, not the two this script expects "
        f"(an explanatory note written into a data row, and a trailing row "
        f"holding only its continuation)")
    df = df[num_id.notna()].copy()
    df["id"] = num_id[num_id.notna()].astype(int)
    assert len(df) == N_PARTICIPANTS, len(df)
    assert df["id"].nunique() == N_PARTICIPANTS, "the participant id repeats"
    print(f"dropped 2 non-participant rows (an explanatory note about the "
          f"age bands, written into the data, and its continuation); "
          f"{N_PARTICIPANTS} participant rows remain, matching the "
          f"correction's stated sample")

    for cols in (EVAL1, EVAL2):
        missing = [c for c in cols if c not in df.columns]
        assert not missing, missing
        df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")
    vals = pd.concat([df[EVAL1], df[EVAL2]]).stack().dropna()
    assert set(vals.unique()) == {0, 1}, sorted(vals.unique())

    # which EVAL is the test? the deposit's own total says so
    total = pd.to_numeric(df["RMDQTotal"], errors="coerce")
    ok = df[EVAL1].notna().all(axis=1) & total.notna()
    a = (df.loc[ok, EVAL1].sum(axis=1) == total[ok]).mean()
    b = (df.loc[ok, EVAL2].sum(axis=1) == total[ok]).mean()
    assert a == 1.0 and b < 0.5, (
        f"RMDQTotal matches EVAL1 on {a:.0%} and EVAL2 on {b:.0%}; the "
        f"test/retest labelling rests on EVAL1 being the published total, so "
        f"stop and re-derive")
    print(f"RMDQTotal reproduces summing EVAL1 on {a:.0%} of rows and EVAL2 "
          f"on {b:.0%}, so EVAL1 is the test and EVAL2 the retest")

    # 'Unnamed: 0' is the sheet's row-label gutter ("Participants" against
    # the first data row and empty after); it holds no respondent data
    assert set(df["Unnamed: 0"].dropna().unique()) <= {"Participants"}, \
        sorted(set(df["Unnamed: 0"].dropna().unique()))
    df = df.drop(columns=["Unnamed: 0"])
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert set(strings) <= set(COVS), sorted(set(strings) - set(COVS))
    for c in ("Gender", "Age range", "Diagnosis"):
        assert df[c].nunique() <= 12, (c, df[c].nunique())
    bands = sorted(str(v) for v in df["Age range"].dropna().unique())
    odd = [b for b in bands if not re.fullmatch(r"(\d\d)-(\d\d)", b) or
           int(b[3:]) - int(b[:2]) != 5]
    print(f"PII screen: string columns are gender, age band and diagnosis, "
          f"all closed vocabularies. Age bands as deposited include "
          f"{odd} alongside the regular five-year bands -- shipped unchanged")

    d = df.rename(columns=COVS)
    cov_cols = sorted(COVS.values())
    frames = []
    for cols, wave in ((EVAL1, "test"), (EVAL2, "retest")):
        ren = {c: f"Q{i}" for i, c in enumerate(cols, 1)}
        sub = d[["id"] + cov_cols + cols].rename(columns=ren)
        long = sub.melt(id_vars=["id"] + cov_cols,
                        value_vars=list(ren.values()),
                        var_name="item", value_name="resp")
        long["wave"] = wave
        frames.append(long)
    long = pd.concat(frames, ignore_index=True).dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long.reset_index(drop=True)

    assert long["id"].nunique() == N_PARTICIPANTS
    assert long["item"].nunique() == N_ITEMS
    assert set(long["wave"]) == {"test", "retest"}
    assert not long.duplicated(["id", "item", "wave"]).any()
    assert len(TABLE) <= 40, TABLE
    long = long[["id", "item", "resp", "wave"] + cov_cols]

    checks = run_qc(long, permitted_values={f"Q{i}": [0, 1]
                                            for i in range(1, N_ITEMS + 1)})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:150]}")

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    per = long.groupby("wave")["resp"].count().to_dict()
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={N_ITEMS} waves={per} resp=0-1")


if __name__ == "__main__":
    convert()
