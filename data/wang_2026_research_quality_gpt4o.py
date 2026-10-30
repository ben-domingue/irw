#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0341620
# DOI: 10.1371/journal.pone.0341620
# Paper: Wang, S., & Wang, Y. (2026). Assessing the sustainable development of a
#   national research ecosystem: A generative AI-based evaluation of empirical
#   educational research in China (2004-2023). PLOS ONE 21(1).
# Data: journal.pone.0341620.s001 (S1 Table, .xlsx), 2,145 rows x 35 columns.
# License: CC BY 4.0 (Crossref licence record for the version of record; the
#   data is a Supporting Information file of the article itself).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# THE RESPONSES ARE MACHINE-GENERATED, AND THAT IS THE FIRST THING THIS TABLE
# SAYS ABOUT ITSELF. The "respondent" is not a person: each row is a published
# empirical education paper, and each score is GPT-4o's rating of that paper
# against one of 31 quality indicators on a 1-10 analytic rubric. The authors
# are explicit that this is the design, not a side effect -- the paper
# "utilizes a large language model as a data simulation tool, treating its
# generated analyses as the primary research data", and GPT-4o was instructed
# to read the full text, review the 31 indicators, extract evidence and assign
# a 1-10 score for each.
#
# This is admissible in IRW on the same footing as the jiang_2026_openeval_*
# tables -- machine responses are welcome PROVIDED they are marked as machine
# responses. What is not acceptable is LLM or simulated output presented as if
# it were human. So the table description opens by naming the rater and the
# units, exactly as the OpenEval rows open with "AI models as respondents:",
# and a `rater` column carries the model name on every row so the provenance
# travels with the data rather than living only in the dictionary.
#
# (This script exists because of a correction: the first pass of the
# 2026-10-30 batch REJECTED this deposit as "not human item responses" and
# marked the lead rejected_content. That was the wrong rule. The leads file
# now records it as shipped.)
#
# ONE output table: 2,145 papers x 31 indicators = 66,495 ratings, zero
# missing cells.
#
# resp is 3-10 against a documented 1-10 rubric. The bottom two rubric points
# were never awarded by the model to any paper on any indicator -- an
# unendorsed anchor is a fact about the ratings, not a scale boundary, so the
# permitted range stays 1-10 and the observed range is stated in the
# description. It is also an interesting property of the rater: a human panel
# would be unlikely to leave the bottom 20% of a 10-point scale entirely
# unused across 66,495 judgements.
#
# `id` is the deposit's `serial number`, unique over all 2,145 rows. The
# `Paper` column is NOT used as id and is not shipped: its titles are
# truncated with ellipses and only 657 of 2,145 are distinct, so it identifies
# nothing reliably. No PII question arises either way -- the units are
# published papers, not people.
#
# Covariates: publication year (2004-2023) and journal. The journal column is
# already anonymised by the depositors to "Journal A" through "Journal D", so
# it ships as given; there is nothing to de-identify and nothing to infer.
#
# Item text: NOT SHIPPED, and the obstacle is the OPTIONS, not the stems or the
# rights. The 31 indicator names are the item wording, verbatim, in the
# deposit's own column headers, and they are the authors' own rubric under the
# article's CC BY 4.0 -- so a register row is written with verdict ship. But
# the itemtext schema wants option_text per resp code, and a 1-10 analytic
# rubric has ten level descriptors that are not in the deposit and are not
# printed in the article. Shipping stems with invented anchors is the failure
# the CES-D-10 hold in this same batch avoided, so this is held for the same
# reason and queued in TODO.md.
#
# PII: screened over all 35 columns. Two are text -- the redacted paper titles
# and the anonymised journal labels -- and neither names a person. No emails,
# dates, phone numbers or free-text responses.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("WANG_RQ_RAW", "journal.pone.0341620_S1_Table.xlsx")

TABLE = "wang_2026_research_quality_gpt4o"
N_ROWS = 2145
N_ITEMS = 31
LO, HI = 1, 10          # the rubric's documented range
RATER = "gpt-4o"        # the paper's scoring model

META = {"serial number": "becomes id",
        "Paper": "redacted, non-unique paper titles -- identifies nothing",
        "Year": "becomes cov_year",
        "From": "becomes cov_journal (already anonymised to Journal A-D)"}

PII_PAT = (r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
           r"|\+?\d{9,}"
           r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")


def screen_for_pii(df):
    """The units here are published papers, so the usual person-identifier
    question is moot -- but the screen still runs, because "it's not about
    people" is an assumption worth testing against the actual columns."""
    txt = [c for c in df.columns
           if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: examined {len(txt)} text column(s) of "
          f"{len(df.columns)}: {txt}")
    hits = [(c, v) for c in txt for v in df[c].dropna().astype(str).unique()
            if pd.Series([v]).str.contains(PII_PAT, regex=True,
                                           case=False).any()]
    assert not hits, f"PII screen hit: {hits[:5]}"
    print("  clean: the two text columns are redacted paper titles and "
          "depositor-anonymised journal labels; the units are published "
          "papers, not people")


def convert():
    df = pd.read_excel(RAW, sheet_name=0)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    items = [c for c in df.columns if c not in META]
    assert len(items) == N_ITEMS, (
        f"found {len(items)} indicator columns, expected {N_ITEMS} -- the "
        f"paper scores each study on 31 quality indicators")
    left_out = [c for c in df.columns if c not in items and c not in META]
    assert not left_out, f"unaccounted source columns: {left_out}"

    assert int(df[items].isna().sum().sum()) == 0, "unexpected missing cells"
    vals = pd.to_numeric(df[items].stack(), errors="coerce")
    assert vals.notna().all(), "a non-numeric rating"
    assert (vals % 1 == 0).all(), "a fractional rating"
    assert vals.between(LO, HI).all(), sorted(vals.unique())
    obs = sorted(int(v) for v in set(vals.unique()))
    print(f"ratings: {len(items)} indicators x {N_ROWS} papers, zero missing. "
          f"Observed {obs[0]}-{obs[-1]} on a documented {LO}-{HI} rubric -- "
          f"the model never awarded the bottom {obs[0] - LO} point(s) to any "
          f"paper on any indicator")

    assert df["serial number"].nunique() == len(df), "serial number not unique"
    assert df["Year"].between(2004, 2023).all()
    df = df.rename(columns={"serial number": "id", "Year": "cov_year",
                            "From": "cov_journal"})
    cov_cols = ["cov_journal", "cov_year"]

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=items,
                   var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(int)
    # the provenance travels with the data, not only in the dictionary
    long["rater"] = RATER

    assert long["id"].nunique() == N_ROWS
    assert long["item"].nunique() == N_ITEMS
    assert not long.duplicated(["id", "item", "rater"]).any()
    assert len(long) == N_ITEMS * N_ROWS, len(long)
    assert len(TABLE) <= 40, TABLE

    long = long[["id", "item", "resp", "rater"] + cov_cols]

    # gate before writing -- the contract check requires the validator to run
    # in-script, not just on the output file
    checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                            for i in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:175]}")

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()} "
          f"rater={RATER} (MACHINE-GENERATED ratings of published papers)")


if __name__ == "__main__":
    convert()
