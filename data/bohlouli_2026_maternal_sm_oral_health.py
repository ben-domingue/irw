#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0357008
# DOI: 10.1371/journal.pone.0357008
# Paper: Bohlouli, S., Murugeshappa, D., Bohlouli, B., & Amin, M. (2026).
#   Social media addiction, maternal mental health, and children's oral
#   health behaviours among immigrants. PLOS ONE 21(8): e0357008.
# Data: journal.pone.0357008.s001 (S1 Data, .xlsx), sheet 'MandA',
#   304 rows x 43 columns, with a second sheet 'code' giving the codebook.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# Mothers surveyed in Canada about their own social media use and mental
# health and their child's oral health.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# THREE output tables, 20 items. The deposit's 42 substantive columns divide
# into four parts, named by the codebook sheet, and only two of the four are
# shippable:
#   Part 1, demographics (One..Fifteen)        -- DROPPED, see PII below
#   Part 2, child oral-health behaviours (7)   -- DROPPED, see below
#   Part 3, maternal social media addiction (6) -- SHIPPED
#   Part 4, maternal anxiety (7) and depression (7) -- SHIPPED as two tables
#
# PII: PART 1 CONTAINS TWO REAL DATES OF BIRTH and is dropped entirely without
# being examined further. The codebook names column `Two` as the child's date
# of birth and column `Four` as the mother's; both hold full dates, not years.
# Dates of birth are on the drop-on-sight list, so the whole demographic block
# goes -- not just those two columns -- because the rest of it (country of
# origin as free text, immigration category, immigration status, marital
# status, household income, number of children) is exactly the kind of
# quasi-identifier set that re-identifies a person once a date of birth has
# been in the same file. No value from any Part 1 column is printed by this
# script or reproduced in any record it writes.
#
# PART 2 IS DROPPED FOR A DIFFERENT REASON: it is seven questions on seven
# DIFFERENT response scales (last dental examination 1-3, reasons for visiting
# 1-4, perceived dental health 1-5, cavities 1-3, brushing frequency 1-4, age
# started brushing 1-4, sugar consumption 1-4). That is a behaviour
# questionnaire, not an item battery; putting seven response formats on one
# `resp` is what the one-scale-per-file rule exists to prevent, and no subset
# of three shares a scale.
#
# THE TWO SHIPPED INSTRUMENTS ARE IDENTIFIABLE FROM THE CODEBOOK'S OWN TEXT:
#   Part 3 is the Bergen Social Media Addiction Scale -- the codebook's six
#     stems are "felt an urge to use", "tried to cut down", "become restless",
#     and so on, the BSMAS's six criteria, on a 1-5 frequency scale.
#   Part 4 is the Hospital Anxiety and Depression Scale. Its stems are
#     verbatim HADS ("I can sit at ease and feel relaxed", "I get a sort of
#     frightened feeling like butterflies in the stomach", "I feel as if I am
#     slowed down", "I have lost interest in my appearance"), 7 anxiety and 7
#     depression items on the HADS's own 0-3 scale. The two subscales ship as
#     two tables, which is how the HADS is scored.
#
# `10` IS A MISSING CODE, NOT A RESPONSE. It appears in several columns of
# every part, including HADS columns whose documented range is 0-3 and
# social-media columns whose range is 1-5. No codebook entry defines a level
# 10 anywhere. Those cells are dropped rather than shipped as an out-of-range
# response; the count is reported below so the loss is visible.
#
# TWO ROWS ARE EMPTY (every column null, including the participant id) and are
# dropped, leaving 302 respondents.
#
# `id` is the deposit's `PID # Anonymous`, already anonymised by the
# depositors; verified unique over the non-empty rows.
#
# Item text: NOT SHIPPED despite being legible in the codebook sheet. Both
# instruments are third-party -- the HADS is Zigmond & Snaith's and is
# commercially licensed, the BSMAS is Andreassen et al.'s -- so the article's
# CC BY does not reach their wording. Registered as holds.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("SADEGHI_RAW", "journal.pone.0357008_S1_Data.xlsx")

MISSING_CODE = 10
WORDS = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
         "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen"]
PART1 = WORDS                                  # demographics -- DOBs, dropped
PART2 = ["Two" + w.lower() for w in
         ["One", "Two", "Three", "Four", "Five", "Six", "Seven"]]
PART3 = ["Three" + w.lower() for w in
         ["One", "Two", "Three", "Four", "Five", "Six"]]
HADS_A = ["A" + w.lower() for w in
          ["One", "Two", "Three", "Four", "Five", "Six", "Seven"]]
HADS_D = ["D" + w.lower() for w in
          ["One", "Two", "Three", "Four", "Five", "Six", "Seven"]]

TABLES = [
    ("bohlouli_2026_maternal_sm_addiction", PART3, 1, 5,
     "Bergen Social Media Addiction Scale (6 items)"),
    ("bohlouli_2026_maternal_hads_anxiety", HADS_A, 0, 3,
     "Hospital Anxiety and Depression Scale -- anxiety (7 items)"),
    ("bohlouli_2026_maternal_hads_depression", HADS_D, 0, 3,
     "Hospital Anxiety and Depression Scale -- depression (7 items)"),
]


def convert():
    df = pd.read_excel(RAW, sheet_name="MandA")
    assert len(df) == 304, len(df)

    # Part 1 is dropped before anything looks at it -- see the header
    shipped = [c for _, cols, *_ in TABLES for c in cols]
    accounted = ["PID # Anonymous"] + PART1 + PART2 + PART3 + HADS_A + HADS_D
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    df = df[["PID # Anonymous"] + shipped]
    print(f"dropped Part 1 ({len(PART1)} demographic columns, two of them "
          f"real dates of birth -- not examined, not printed, not recorded) "
          f"and Part 2 ({len(PART2)} oral-health behaviour questions on seven "
          f"different response scales, so not an item battery)")

    # two rows hold no item response at all; one of them also has no id
    empty = df[shipped].isna().all(axis=1)
    assert int(empty.sum()) == 2, int(empty.sum())
    df = df[~empty].reset_index(drop=True)
    n_rows = len(df)
    assert n_rows == 302, n_rows
    print(f"dropped {int(empty.sum())} wholly empty rows, leaving {n_rows} "
          f"respondents")

    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert strings == ["PID # Anonymous"] or not strings, strings
    assert df["PID # Anonymous"].nunique() == n_rows, "the id is not unique"
    df = df.rename(columns={"PID # Anonymous": "id"})
    df["id"] = df["id"].astype(str)

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, cols, lo, hi, label in TABLES:
        sub = df[["id"] + cols].copy()
        n_missing_code = int((sub[cols] == MISSING_CODE).sum().sum())
        sub[cols] = sub[cols].mask(sub[cols] == MISSING_CODE)
        # .dropna() after .stack() because stack() in this pandas KEEPS NaN,
        # and the cells just masked as the 10 missing code are legitimately
        # null; every REMAINING value must still be numeric before the range
        # is checked (the natesan_2019 lesson earlier in this batch)
        stacked = sub[cols].stack().dropna()
        vals = pd.to_numeric(stacked, errors="coerce")
        assert vals.notna().all(), (
            name, "a non-numeric response",
            list(stacked[vals.isna()].unique())[:3])
        assert vals.between(lo, hi).all(), (name, sorted(vals.unique()))

        long = sub.melt(id_vars=["id"], value_vars=cols, var_name="item",
                        value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long.reset_index(drop=True)
        assert long["item"].nunique() == len(cols)
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name
        long = long[["id", "item", "resp"]]

        checks = run_qc(long, permitted_values={i: list(range(lo, hi + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}  "
              f"({n_missing_code} cells coded {MISSING_CODE} dropped as "
              f"missing)  [{label}]")

    print(f"3 tables, {total} responses (20 items x up to {n_rows} mothers)")


if __name__ == "__main__":
    convert()
