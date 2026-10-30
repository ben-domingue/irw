#!/usr/bin/env python3
# Source: https://www.psycharchives.org/en/item/6dfc48c9-2d86-442d-ae00-47ca888f04fb
# DOI: 10.23668/psycharchives.22277
# Deposit: Tung, L., & Gibson, D. (2026). Supplementary materials to "Math
#   anxiety and financial literacy: The role of math avoidance" [Research
#   Data]. PsychArchives (ZPID).
# Data: Tung_Gibson_2026_Math_anxiety_and_financial_literacy_SUPPL_-_data.csv
#   (393 US undergraduates aged 18-22)
# Codebook: ..._SUPPL_-_codebook.csv in the same deposit, one row per variable
#   with the verbatim question and its response options.
# License: CC BY 4.0 (resolved from the PsychArchives record:
#   https://creativecommons.org/licenses/by/4.0/)
#
# Found by the PsychArchives recycled-terms discovery pass of 2026-10-29.
#
# ONE output table, and the deposit is mostly not item-level. What it holds:
#   Financial.Literacy1-3   the "Big Three" financial-literacy questions
#                           (Lusardi & Mitchell) -- the only real item battery
#   Math.Anxiety            ONE question ("How nervous or anxious does math
#                           make you?", 1-5) -- a single-item measure
#   Reading.Anxiety         ONE question, same form -- a single-item measure
#   Financial.Anxiety       the deposit's own COMPOSITE: "Average score on
#                           12-item scale" (Shapiro & Burchell's Financial
#                           Anxiety Scale). The 12 items themselves are not in
#                           the file, only the mean, which is why its values
#                           are fractional
#   Financial.Literacy.Score  a composite: 1 iff all three Big Three correct
# The two single-item anxiety measures are not shipped (never ship a table with
# one distinct item, however clean the measure) and neither composite is
# shipped. The 12-item Financial Anxiety Scale would have been the better table
# of the two, and it is the one the depositors did not publish item-level.
#
# resp CODING. The source records each Big Three answer as one of "Correct",
# "Incorrect" or "Nonresponse (i.e., I don't know or Refuse to answer)". Those
# three are NOT ordered -- "don't know" is not between right and wrong -- so a
# 0/1/2 coding would be a nominal scale masquerading as an ordinal one. They
# are shipped as the conventional dichotomy instead: resp = 1 for Correct, 0
# for Incorrect or Nonresponse, which is exactly how the depositors scored
# their own Financial.Literacy.Score (verified: that column equals
# "all three Correct" for all 393 rows, asserted below). The distinction
# between a wrong answer and a declined one is therefore NOT in the shipped
# table and is in the source file; the "don't know" share is large and uneven
# across the three items (60, 79 and 185 of 393), so anyone modelling these
# items should read the source rather than assume the 0s are errors. Said in
# the table description too.
#
# Item text: NOT shipped. The wording is in hand -- the deposit's codebook
# prints all three questions verbatim -- but the items are Lusardi & Mitchell's
# "Big Three", not the depositors', and a CC BY deposit does not relicense a
# third-party instrument reproduced inside it. Searched 2026-10-29 for a grant:
# GFLEC's own "About the Big Three" page states no reuse terms, and the NBER
# working-paper front matter grants only short quotation with credit, which
# covers that paper rather than the instrument. A register row is written with
# this batch, verdict hold. Label levels: not applicable -- the file is a plain
# CSV with no variable or value labels at all; the wording comes from the
# companion codebook CSV.
#
# PII: screened with an is_string_dtype selector over all 8 string columns
# (count asserted non-zero). No email, name, phone, postal code or date. The
# Race and Gender columns include the labels "None of these terms describe my
# identity; Please explain:" and "Gender not listed here. Please explain:" --
# the follow-up free text was not deposited, only the option label, so there is
# no free-text column here at all.

import os
import re

import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

RAW = os.environ.get("TUNG_RAW",
                     "Tung_Gibson_2026_Math_anxiety_and_financial_literacy_"
                     "SUPPL_-_data.csv")

TABLE = "tung_2026_financial_literacy"
ITEMS = ["Financial.Literacy1", "Financial.Literacy2", "Financial.Literacy3"]
DEMOG = {"Age": "cov_age", "Education": "cov_education", "Income": "cov_income",
         "Race": "cov_race", "Ethnicity": "cov_ethnicity", "Gender": "cov_gender"}
# not shipped, each for a reason in the header
DROP = ["ID", "Education_numeric", "Gender_man", "Math.Anxiety",
        "Reading.Anxiety", "Financial.Anxiety", "Financial.Literacy.Score"]


def screen_for_pii(df):
    """Select text columns with is_string_dtype, not dtype == object, and print
    the denominator so a zero is visible instead of silent.

    Note the second guard: this file is read with dtype=str, so EVERY column
    arrives as a string, including the numeric composites -- and the long
    decimals in Financial.Anxiety ("3.58333333333333") match a bare
    nine-or-more-digits phone pattern. A column whose every value parses as a
    number is not a text column, so it is excluded before matching rather than
    the pattern being loosened.
    """
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: examined {len(txt)} of {len(df.columns)} columns: {txt}")
    assert txt, "PII screen selected no columns -- the selector is wrong"
    pat = re.compile(r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
                     r"|\+?\d{9,}"
                     r"|\b\d{5}\b"
                     r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")
    hits = [(c, v) for c in txt for v in df[c].dropna().astype(str)
            if pat.search(v)]
    assert not hits, f"PII screen hit: {hits[:5]}"
    print("PII screen: clean")


def convert():
    df = pd.read_csv(RAW, dtype=str)
    screen_for_pii(df)

    assert df["ID"].nunique() == len(df), "ID is not unique"
    df["id"] = df["ID"].astype(int)

    for c in ITEMS:
        seen = set(df[c].dropna().unique())
        assert seen <= {"Correct", "Incorrect", "Nonresponse"}, (c, seen)

    correct = df[ITEMS].eq("Correct")
    # the depositors' own composite is 1 iff all three are Correct -- this is
    # what licenses the dichotomous coding below rather than inventing one
    recon = correct.all(axis=1).astype(int)
    theirs = df["Financial.Literacy.Score"].astype(int)
    assert recon.equals(theirs), "Financial.Literacy.Score does not reconstruct"
    print(f"Financial.Literacy.Score reconstructs exactly from the three items "
          f"for all {len(df)} rows ({int(recon.sum())} scored 1)")

    for src, dst in DEMOG.items():
        df[dst] = df[src]
    cov_cols = sorted(DEMOG.values())

    accounted = set(ITEMS) | set(DEMOG) | set(DROP)
    left_out = [c for c in pd.read_csv(RAW, nrows=0).columns
                if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    print(f"dropped {len(DROP)} source columns: 2 single-item anxiety measures, "
          f"2 composites, 2 recoded demographic copies, and the raw ID")

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                   var_name="item", value_name="label")
    long = long.dropna(subset=["label"]).reset_index(drop=True)
    long["resp"] = (long["label"] == "Correct").astype(int)
    # a nonresponse is a real observed answer here ("I don't know or Refuse"),
    # recorded as not-correct rather than dropped -- see the header
    print("  response mix shipped as resp=0: "
          f"{int((long['label'] == 'Incorrect').sum())} Incorrect + "
          f"{int((long['label'] == 'Nonresponse').sum())} Nonresponse")

    assert long["resp"].between(0, 1).all()
    assert long["id"].nunique() >= 100, long["id"].nunique()
    assert long["item"].nunique() >= 3, long["item"].nunique()

    os.makedirs(OUT_DIR, exist_ok=True)
    long = long[["id", "item", "resp"] + cov_cols]
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
