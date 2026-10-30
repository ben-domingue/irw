#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0221087
# DOI: 10.1371/journal.pone.0221087
# Paper: Natesan, P., Hadid, D., Harb, Y. A., & Hitti, E. (2019). Comparing
#   patients and families perceptions of satisfaction and predictors of overall
#   satisfaction in the emergency department. PLOS ONE 14(8).
# Data: journal.pone.0221087.s001 (S1 File, .csv), 705 rows x 38 columns.
# License: CC BY 4.0 (Crossref licence record for the version of record; the
#   data is a Supporting Information file of the article itself).
# 705 emergency-department visit interviews.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# ONE output table: a 28-item emergency-department satisfaction questionnaire,
# Q2..Q29, all items on one 5-point scale.
#
# Q1 IS NOT AN ITEM, which the column name hides and a naive melt would not.
# It sits in the same Q-numbered sequence as the satisfaction items, but 203
# of its 705 values are FREE TEXT ("My primary care provider or specialist is
# at AUBMC", "Conviniently located/ close to my residency") and the remaining
# 502 are small integers -- it is a partly-coded "why did you choose this ED"
# question, not a rated item. Dropped. Note the consequence for the scale
# itself: including Q1 made the pooled domain look like 1-7, because its
# reason codes run higher than the satisfaction scale. The real scale is 1-5,
# and the first draft of this script had it wrong for exactly that reason.
#
# A HOLE IN MY OWN CHECK, worth recording because it is reusable. The first
# draft asserted the response range with
# `pd.to_numeric(..., errors="coerce").dropna().between(LO, HI).all()`, which
# passes happily on free text: coerce turns it into NaN and dropna removes it
# before the comparison. The range check said fine and the later astype(int)
# blew up. The assert below instead requires every NON-NULL item value to be
# numeric FIRST, and only then checks the range.
#
# `cov_respondent_type` IS THE POINT OF THE STUDY, not an incidental
# covariate, which is why it is called out here. The paper asks "whether the
# items that measure patient and family members' satisfaction function
# identically across the patient and family member groups" -- i.e. it is a
# measurement-invariance study, and this column is the grouping variable the
# invariance is tested across. Anyone using this table for a DIF or invariance
# analysis needs it, so it ships with the respondent type as the deposit codes
# it: 1 (466 interviews), 2 (237) and 3 (2).
#
# A SMALL UNDOCUMENTED CATEGORY, KEPT AND FLAGGED. The paper describes two
# groups, patients and family members, but `Person_interviewed` takes a third
# value in exactly 2 of 705 rows. The deposit has no codebook and the article
# does not mention a third category, so what code 3 means is unknown -- most
# likely a both-present or other-relative interview. Those 2 rows are KEPT,
# because their 29 satisfaction responses are real, and the covariate value
# ships as 3 rather than being folded into 1 or 2 or dropped. Which of 1 and 2
# is "patient" is also not stated; the counts (466 vs 237) match the paper's
# design of interviewing more patients than families, but that is suggestive
# rather than proof, so no relabelling is attempted and the codes ship as
# given. Said in the table description.
#
# MISSINGNESS IS PER-ITEM AND LARGE, which is expected for an ED satisfaction
# instrument: per-item n runs 290 to 705, because many items are about a
# specific aspect of care that not every visit involved (an item about
# laboratory results cannot be answered by a visit with no tests). Every one of
# the 705 respondents answered at least one item, asserted below, so cells are
# dropped and no respondent is. The lowest-n item is answered by 41% of the
# sample, which is worth knowing before computing a total score.
#
# ONE table, not several: 29 items, one 7-point scale, one instrument. The
# paper treats them as a single satisfaction measure with a general factor,
# which is what the invariance analysis is about.
#
# `id` is the deposit's unnamed first column, a row number 1..705 verified
# unique. Renamed rather than used positionally.
#
# Covariates: respondent type (above), gender, education, guarantor type
# (insurance), whether this was a first visit, and visit time.
#
# OCCUPATION AND SERVICE ARE DROPPED FOR MIXED CODING, which is a different
# defect from the undocumented-column drops elsewhere in this batch. Both
# columns are HALF coded and HALF free text -- 230 of ~705 values in each are
# names ("House hold", "Construction", "Ophtalmology", "Surgery") and the rest
# are digit codes. So the same category can appear both as `3` and as
# `Surgery`, and without the key nothing can reconcile them. A covariate that
# silently splits one category across two representations is worse than no
# covariate, so neither ships.
#
# Item text: NOT SHIPPED. The deposit names its items Q1..Q29 with no wording,
# and the article discusses the instrument's factor structure without
# reproducing the items. No wording exists to ship, so this is an availability
# gap rather than a rights question and no register row is written.
#
# PII: screened over all 38 columns. Two string columns (Occupation, Service),
# both closed vocabularies of digit codes; no names, emails, dates, free text
# or geography.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("NATESAN_RAW", "journal.pone.0221087_S1_File.csv")

TABLE = "natesan_2019_ed_satisfaction"
N_ROWS = 705
N_ITEMS = 28          # Q2..Q29; Q1 is a partly-free-text question, not an item
LO, HI = 1, 5

COVS = {"Person_interviewed": "cov_respondent_type", "Gender": "cov_gender",
        "Education": "cov_education", "Guarantor_type": "cov_guarantor_type",
        "Firstvisit": "cov_first_visit", "Visit_time": "cov_visit_time"}
# dropped, each for a reason stated in the header
DROP = {"Q1": "partly free text -- a 'why this ED' question, not a rated item",
        "Occupation": "mixed coding: 230 of 704 values are text, the rest digit "
                      "codes, so the same category appears both ways",
        "Service": "mixed coding: 230 of 705 values are text, the rest digit codes"}

PII_PAT = (r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
           r"|\+?\d{9,}"
           r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")


def screen_for_pii(df):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(strings)} string column(s) of {len(df.columns)}: "
          f"{strings}")
    hits = [(c, v) for c in strings for v in df[c].dropna().astype(str).unique()
            if pd.Series([v]).str.contains(PII_PAT, regex=True,
                                           case=False).any()]
    assert not hits, f"PII screen hit: {hits[:5]}"
    # three string columns, and all three are MIXED: part digit code, part
    # written-in text. Report that honestly rather than calling them codes.
    mixed = {}
    for c in strings:
        nn = df[c].dropna().astype(str)
        n_text = int(pd.to_numeric(nn, errors="coerce").isna().sum())
        mixed[c] = (n_text, len(nn), df[c].nunique())
    for c, (n_text, n, lv) in mixed.items():
        assert n_text, f"{c} was expected to hold written-in text and does not"
        print(f"    {c}: {n_text} of {n} values are written-in text, "
              f"{lv} distinct levels")
    assert set(mixed) == {"Occupation", "Service", "Q1"}, sorted(mixed)
    print("  clean of PII: the written-in text is occupation names, hospital "
          "service names and reasons for choosing the ED -- no names, emails, "
          "phone numbers, dates or geography. All three columns are DROPPED "
          "(Q1 is not an item; the other two are unusable as covariates "
          "because the same category appears both coded and written out)")


def convert():
    df = pd.read_csv(RAW)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    items = [c for c in df.columns
             if re.fullmatch(r"Q\d+", str(c)) and c not in DROP]
    assert len(items) == N_ITEMS, (len(items), N_ITEMS)
    assert "Q1" not in items, "Q1 is not an item -- see the header"
    id_col = [c for c in df.columns if str(c).startswith("Unnamed")]
    assert len(id_col) == 1, id_col
    accounted = set(items) | set(COVS) | set(DROP) | set(id_col)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    print(f"dropped {len(DROP)} columns: " +
          "; ".join(f"{k} ({v})" for k, v in DROP.items()))

    # every NON-NULL item value must be numeric BEFORE the range is checked.
    # Coercing first and dropping NaN would let free text pass silently -- see
    # the header; that is exactly what the first draft of this script did.
    # .dropna() after .stack() because stack() in this pandas KEEPS NaN, so
    # the non-numeric test would otherwise flag every missing cell (the same
    # quirk that bit trusz_2022 in the 2026-10-29f batch)
    stacked = df[items].stack().dropna()
    nonnum = stacked[pd.to_numeric(stacked, errors="coerce").isna()]
    assert nonnum.empty, (
        f"{len(nonnum)} non-numeric item value(s), e.g. "
        f"{list(nonnum.unique())[:3]}")
    vals = pd.to_numeric(stacked)
    assert vals.between(LO, HI).all(), sorted(vals.unique())
    assert (vals % 1 == 0).all(), "a fractional response"

    # per-item nonresponse, by design: not every visit involves every aspect
    counts = df[items].notna().sum()
    assert df[items].notna().any(axis=1).all(), "a respondent answered no items"
    skipped = int(df[items].isna().sum().sum())
    print(f"per-item n runs {int(counts.min())}-{int(counts.max())} of "
          f"{N_ROWS}: items about a specific aspect of care cannot be answered "
          f"by every visit. {skipped} cells dropped, no respondent dropped "
          f"(lowest-n item answered by {100 * counts.min() / N_ROWS:.0f}%)")

    # the measurement-invariance grouping variable, with its undocumented third code
    grp = df["Person_interviewed"].value_counts().sort_index()
    assert set(grp.index) == {1, 2, 3}, grp.to_dict()
    assert grp[3] == 2, (
        f"the undocumented third respondent-type code now has {grp[3]} rows, "
        f"not 2 -- the description says it is a 2-row anomaly, so recheck")
    print(f"cov_respondent_type (the paper's invariance grouping variable): "
          f"{grp.to_dict()} -- codes ship as the deposit gives them; which of "
          f"1/2 is 'patient' is not stated, and code 3 is undocumented")

    assert df[id_col[0]].nunique() == len(df), "the row number is not unique"
    df = df.rename(columns={id_col[0]: "id", **COVS})
    cov_cols = sorted(COVS.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=items,
                   var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    assert long["id"].nunique() == N_ROWS, long["id"].nunique()
    assert long["item"].nunique() == N_ITEMS
    assert not long.duplicated(["id", "item"]).any()
    assert len(long) == N_ITEMS * N_ROWS - skipped, len(long)
    assert len(TABLE) <= 40, TABLE

    long = long[["id", "item", "resp"] + cov_cols]

    # gate before writing -- the contract check requires the validator to run
    # in-script, not just on the output file
    checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                            for i in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:170]}")

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
