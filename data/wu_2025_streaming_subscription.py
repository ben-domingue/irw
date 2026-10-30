#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0322860
# DOI: 10.1371/journal.pone.0322860
# Paper: Wu, T., Jiang, N., Sharif, S. P., & Chen, M. (2025). Explaining
#   subscription intention for video streaming platforms in China: Integrating
#   the UTAUT2 model, perceived value theory, and S-O-R theory.
#   PLOS ONE 20(5).
# Data: Harvard Dataverse 10.7910/DVN/OHWKPD -- "Data English version.xlsx",
#   506 rows x 75 columns, downloaded with ?format=original.
#
# LICENCE verified on the DEPOSIT: the data is off-site on Dataverse, so the
# article's CC BY cannot grant it. The Dataverse API reports CC0 1.0
# (rightsIdentifier CC0-1.0), which is MORE permissive than the article's
# CC BY 4.0 -- so unlike the four figshare deposits in this batch the two
# licences differ, and the deposit's own terms are what govern the data.
#
# TWO FILES, ONE DATASET -- caught before building. The deposit lists
# "Data English version.xlsx" and "Data English version-1.xlsx", both 146,484
# bytes and both md5 664957ada81d6ed6eaace48923ce0f3a. Byte-identical: the
# depositors uploaded the same file twice. Same shape as the Trusz
# IEEH3O/3BZAUD duplicate in the 2026-10-29f batch, and worth checking rather
# than assuming the second file is a second wave or a second language.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# EIGHT output tables, one per named construct. Every count below is stated
# explicitly in the paper's Measures section, so these boundaries are
# documented rather than inferred -- the same footing as the eight
# lin_2024_escooter_* tables and unlike the opaque-label cases in this batch:
#   S    8 items  Subscription intention       (adapted from Venkatesh et al.)
#   PE   9 items  Performance expectancy       (Venkatesh et al.)
#   EE   9 items  Effort expectancy            (Venkatesh et al.)
#   SI   8 items  Social influence             (Venkatesh et al. 2012)
#   HM   7 items  Hedonic motivation           (Kim et al. 2006; Venkatesh 2012)
#   H    7 items  Habit                        (Limayem et al. 2007; Venkatesh)
#   PV   8 items  Perceived value              (Zhang 2024; Sweeney & Soutar)
#   AOA  9 items  Attractiveness of alternatives (Kuo 2013; Jones 2000; Kim 2011)
# 65 items in all, every one on the paper's "seven-point Likert scale ranging
# from 1 (strongly disagree) to 7 (strongly agree)". Split rather than merged
# because the study treats them as distinct latent variables in a PLS-SEM path
# model, not as subscales of one instrument.
#
# M1-M4 ARE NOT SHIPPED, and the reason is specific rather than cautious: they
# are the study's MARKER VARIABLE. The paper used "Harman's one-way test and
# marker variable techniques ... to statistically assess common method
# variance", and a marker variable is by construction a battery chosen to be
# unrelated to the model. The paper never says what it measures. So these four
# columns are real responses on the same 1-7 scale, but their construct is
# unknown -- a table with no identifiable construct is not worth shipping, and
# guessing one would be worse. This is the only block in the file the Measures
# section does not name, which is itself the evidence. Noted in BATCH_LOG.
#
# Clean source, verified: zero missing cells across all 69 item columns
# (including M), every item's observed domain exactly 1-7. No sentinel codes.
#
# Covariates are properly labelled here, unusually for this batch: the deposit
# names them "1. Gender", "2. Age", "3. Employment Status", "4.Education
# level", "5. Monthly Income" (note the missing space in the fourth, which the
# rename map handles verbatim). Contrast lin_2024_escooter_*, whose nine
# demographic columns are bare integers and had to be dropped.
#
# `id` is the deposit's "Serial Number", verified unique over all 506 rows.
#
# Item text: NOT SHIPPED. The paper cites a per-construct source for every
# battery and points to "Appendix 2 Questionnaire" for the wording, but no
# appendix file is in the Dataverse deposit (only the duplicated data file) and
# the article's own appendix is not reproduced in the HTML. So the wording is
# neither in the deposit nor recoverable from the article, and the items are
# adapted from six different cited instruments rather than study-authored. A
# register row is written, verdict hold.
#
# PII: screened over all 75 columns. Every one is numeric; no names, emails,
# dates, free text or geography.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("WU_STREAM_RAW", "Data English version.xlsx")

N_ROWS = 506
LO, HI = 1, 7

# prefix -> (table, item count stated in the paper, construct label)
CONSTRUCTS = {
    "S": ("wu_2025_streaming_subscription_intent", 8, "Subscription intention"),
    "PE": ("wu_2025_streaming_performance_exp", 9, "Performance expectancy"),
    "EE": ("wu_2025_streaming_effort_exp", 9, "Effort expectancy"),
    "SI": ("wu_2025_streaming_social_influence", 8, "Social influence"),
    "HM": ("wu_2025_streaming_hedonic_motivation", 7, "Hedonic motivation"),
    "H": ("wu_2025_streaming_habit", 7, "Habit"),
    "PV": ("wu_2025_streaming_perceived_value", 8, "Perceived value"),
    "AOA": ("wu_2025_streaming_alt_attractiveness", 9,
            "Attractiveness of alternatives"),
}
MARKER = "M"          # the common-method-variance marker variable; not shipped
N_MARKER = 4

COVS = {"1. Gender": "cov_gender", "2. Age": "cov_age",
        "3. Employment Status": "cov_employment_status",
        "4.Education level": "cov_education",
        "5. Monthly Income": "cov_monthly_income"}


def screen_for_pii(df):
    txt = [c for c in df.columns
           if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert not txt, f"unexpected text column(s) -- screen them: {txt}"
    print("  every column is numeric; no name, email, date, free text or "
          "geographic column in this file")


def convert():
    df = pd.read_excel(RAW, sheet_name=0)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    found = {}
    for c in df.columns:
        m = re.match(r"^([A-Z]+)(\d+)$", str(c).strip())
        if m:
            found.setdefault(m.group(1), []).append(c)
    got = {k: len(v) for k, v in found.items() if k in CONSTRUCTS}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    assert got == want, f"construct counts are {got}, expected {want}"
    assert len(found.get(MARKER, [])) == N_MARKER, (
        f"expected {N_MARKER} marker columns, found {found.get(MARKER)}")

    accounted = set(COVS) | {"Serial Number"}
    for cols in found.values():
        accounted |= set(cols)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"

    # the marker variable's construct is never named in the paper
    all_items = [c for cols in found.values() for c in cols]
    assert int(df[all_items].isna().sum().sum()) == 0, "unexpected missing cells"
    print(f"not shipping the {N_MARKER} {MARKER}* columns: they are the "
          f"study's common-method-variance marker variable, and the paper "
          f"never says what it measures (see header)")

    assert df["Serial Number"].nunique() == len(df), "Serial Number not unique"
    df = df.rename(columns={"Serial Number": "id", **COVS})
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    written = set()
    for prefix, (name, n, label) in CONSTRUCTS.items():
        cols = sorted(found[prefix], key=lambda c: int(re.sub(r"\D", "", str(c))))
        assert name not in written and len(name) <= 40, (name, len(name))
        written.add(name)

        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all() and vals.between(LO, HI).all(), \
            (name, sorted(vals.unique()))

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)

        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()

        long = long[["id", "item", "resp"] + cov_cols]

        # gate before writing -- the contract check requires the validator to
        # run in-script, not just on the output file
        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:150]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}  [{label}]")

    assert total == 65 * N_ROWS, total
    print(f"8 tables, {total} responses (65 items x {N_ROWS} respondents, "
          f"no missing cells; 4 marker-variable items withheld)")


if __name__ == "__main__":
    convert()
