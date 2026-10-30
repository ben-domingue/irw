#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0339943
# DOI: 10.1371/journal.pone.0339943
# Paper: Guo, W., Zhong, Y., Wang, Y., Chen, P., Zhuang, S., & Liu, J. (2026).
#   Reframing participation through empowerment: mechanisms driving Chinese
#   women's intentions in adventure sports tourism. PLOS ONE 21(5).
# Data: journal.pone.0339943.s002 (S2 File, .xlsx), 566 rows x 54 columns.
# License: CC BY 4.0 (the data is a Supporting Information file of the article
#   itself, so the article's licence reaches it -- no off-site deposit here).
# 566 adult women surveyed while skiing, surfing or rock climbing at Wanlong
# Ski Resort, Riyue Bay and Moon Hill, February-April 2025.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# ELEVEN output tables, 45 items, zero missing cells -- 25,470 responses. The
# paper: "five-point Likert scale ranging from 1 (strongly disagree) to 5
# (strongly agree)", higher = stronger, which the observed 1-5 range on every
# one of the 45 columns matches. No item is described as reverse-coded.
#
# THE DEPOSIT NAMES ITS OWN CONSTRUCTS, which is why eleven tables rather than
# four. Every item column is headed with its subscale in words ('IM-to know 1',
# 'Political empowerment 2'), and the article's item counts agree column for
# column: intrinsic motivation 4+4+4, extrinsic motivation 4+4+4, empowerment
# 5+3+4, risk perception 6, participation intention 3.
#
# WHY THE SIX MOTIVATION SUBSCALES ARE NOT ONE 24-ITEM TABLE. They are the
# Sport-Motivation-Scale family, laid out along the self-determination
# continuum from intrinsic through identified, introjected and external
# regulation. The continuum is the point of the instrument: the subscales are
# designed to be distinguishable, not interchangeable, and the paper models
# them as separate latent variables. Pooling them would assert a
# unidimensionality the instrument is built to deny. Same for the three
# empowerment dimensions, which the paper's own mediation model treats as
# three separate mediators. So the split follows the instrument, not the file.
#
# ITEM TEXT IS SHIPPED FOR 36 OF THE 45 ITEMS, and the gap is worth stating
# precisely because it is an availability gap rather than a rights one:
#   S1 File prints all 24 motivation items under their subscale headings, in
#     the deposit's column order.
#   S3 File prints all 12 empowerment items -- as a two-column table of Boley
#     & McGehee's (2014) ORIGINAL wording beside this study's ADAPTED wording.
#     Only the adapted column ships: that is what these 566 women answered,
#     and it is the authors' own text published under their own CC BY licence.
#     The original RETS wording is third-party and is not reproduced.
#   Risk perception (6) and participation intention (3) have NO published
#     wording anywhere in the article or its eight supporting files. Nothing
#     is invented for them; those two tables ship without item text.
# See guo_2026_itemtext.py for the item-text build.
#
# COVARIATES SHIP AS THE DEPOSIT'S OWN LABELS, not as codes, because the
# deposit stores them as readable text ('26-35 years', 'Postgraduate or
# above'). Every value carries a trailing space in the file, stripped here.
# Eight covariates: age band, education, monthly income, which sport, mobility
# range, annual frequency, participation mode and residential region.
#
# THE SAMPLE IS ALL WOMEN, so there is no gender covariate to ship and its
# absence is not an omission -- the study recruited adult female participants
# only. Recorded in the table description instead, where a constant belongs.
#
# `id` is the deposit's `Number`, 1..566, verified unique.
#
# PII: screened over all 54 columns. The eight string columns are closed
# category vocabularies (3-4 levels each); no names, emails, dates, free text
# or geography finer than a third of China.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("GUO_RAW", "journal.pone.0339943_S2_File.xlsx")

N_ROWS = 566
LO, HI = 1, 5

# (deposit column prefix, table name, expected item count, label)
BLOCKS = [
    ("IM-to know", "guo_2026_adv_motiv_to_know", 4,
     "Intrinsic motivation - to know"),
    ("IM-accomplishment", "guo_2026_adv_motiv_accomplishment", 4,
     "Intrinsic motivation - accomplishment"),
    ("IM-stimulation", "guo_2026_adv_motiv_stimulation", 4,
     "Intrinsic motivation - experience stimulation"),
    ("EM-identified regulation", "guo_2026_adv_motiv_identified_reg", 4,
     "Extrinsic motivation - identified regulation"),
    ("EM-introjected regulation", "guo_2026_adv_motiv_introjected_reg", 4,
     "Extrinsic motivation - introjected regulation"),
    ("EM-external regulation", "guo_2026_adv_motiv_external_reg", 4,
     "Extrinsic motivation - external regulation"),
    ("Psychological empowerment", "guo_2026_adv_psych_empowerment", 5,
     "Psychological empowerment"),
    ("Social empowerment", "guo_2026_adv_social_empowerment", 3,
     "Social empowerment"),
    ("Political empowerment", "guo_2026_adv_political_empowerment", 4,
     "Political empowerment"),
    ("Risk perception", "guo_2026_adv_risk_perception", 6,
     "Risk perception"),
    ("Participation intention", "guo_2026_adv_participation_intent", 3,
     "Participation intention"),
]

COVS = {"Age": "cov_age_band",
        "Education Level": "cov_education",
        "Average Monthly Income": "cov_monthly_income",
        "Frequently Participated Adventure Sports": "cov_sport",
        "Mobility Range": "cov_mobility_range",
        "Annual Frequency of Adventure Sports Tourism": "cov_annual_frequency",
        "Participation Mode": "cov_participation_mode",
        "Residential Region": "cov_region"}

PII_PAT = (r"[\w.+-]+@[\w-]+\.[a-z]{2,}"
           r"|\+?\d{9,}"
           r"|\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b")


def item_code(col):
    """'IM-to know 1' -> 'IM_to_know_1'. Traceable back to the deposit header,
    and the join key the item-text table uses."""
    return col.strip().replace("-", "_").replace(" ", "_")


def screen_for_pii(df):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(strings)} string column(s) of {len(df.columns)}: "
          f"{strings}")
    assert set(strings) == set(COVS), sorted(set(strings) ^ set(COVS))
    hits = [(c, v) for c in strings for v in df[c].dropna().astype(str).unique()
            if pd.Series([v]).str.contains(PII_PAT, regex=True,
                                           case=False).any()]
    assert not hits, f"PII screen hit: {hits[:5]}"
    for c in strings:
        lv = df[c].nunique()
        assert lv <= 6, (c, lv, "more levels than a closed vocabulary -- "
                                "re-screen, this may be written-in text")
    print("  every string column is a closed category vocabulary of 3-4 "
          "levels (age band, education, income band, sport, mobility range, "
          "frequency band, participation mode, region); no names, emails, "
          "dates, free text or fine geography")


def convert():
    df = pd.read_excel(RAW)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    blocks = {}
    for prefix, name, n, label in BLOCKS:
        cols = [c for c in df.columns if str(c).startswith(prefix + " ")]
        cols.sort(key=lambda c: int(str(c).rsplit(" ", 1)[1]))
        assert len(cols) == n, (prefix, len(cols), n)
        blocks[name] = cols

    accounted = {"Number"} | set(COVS)
    for cols in blocks.values():
        accounted |= set(cols)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    assert sum(len(c) for c in blocks.values()) == 45

    assert df["Number"].nunique() == len(df), "Number is not unique"
    df = df.rename(columns={"Number": "id", **COVS})
    for c in COVS.values():
        df[c] = df[c].astype(str).str.strip()
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, name, n, label in BLOCKS:
        cols = blocks[name]
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all(), (name, "a non-numeric response")
        assert vals.between(LO, HI).all(), (name, sorted(vals.unique()))
        assert (vals % 1 == 0).all(), (name, "a fractional response")

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["item"] = long["item"].map(item_code)
        long["resp"] = long["resp"].astype(int)

        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()
        assert len(long) == n * N_ROWS, (name, len(long))
        assert len(name) <= 40, name

        long = long[["id", "item", "resp"] + cov_cols]

        # gate before writing -- the contract check requires the validator to
        # run in-script, not just on the output file
        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in long["item"].unique()})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:145]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}  [{label}]")

    assert total == 45 * N_ROWS, total
    print(f"{len(BLOCKS)} tables, {total} responses "
          f"(45 items x {N_ROWS} respondents, no missing cells)")


if __name__ == "__main__":
    convert()
