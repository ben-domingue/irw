#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0294350
# DOI: 10.1371/journal.pone.0294350
# Paper: Li, Y., Chen, D., & Deng, X. (2024). The impact of digital educational
#   games on student's motivation for learning: The mediating effect of
#   learning engagement and the moderating effect of the digital environment.
#   PLOS ONE 19(1).
# Data: journal.pone.0294350.s001 (S1 Data, .xlsx), 434 rows x 64 columns.
# License: CC BY 4.0 (Crossref licence record for the version of record; the
#   data is a Supporting Information file of the article itself).
# 434 valid responses from students at three universities in Thailand.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# FOUR output tables. This deposit is unusual and valuable in one specific way:
# its column headers ARE the verbatim item wording, in English, rather than
# codes. Nothing had to be inferred about which column is which item.
#
# THE ITEM LABELS ARE SHORT CODES ANYWAY, which is a deliberate choice against
# the easy option. The headers could have been used directly as `item` values,
# and the first draft of this script did exactly that -- but an item label is
# the permanent join key between a response table and its item text table, and
# a 90-character English sentence makes a brittle one: any later whitespace or
# punctuation normalisation silently breaks the join, and the wording differs
# in register across the four batteries. So each battery gets stable positional
# codes (`perc_01`.. , `mot_01`.. , `env_01`.. , `eng_01`..) in the deposit's
# own column order, and the verbatim wording stays recoverable from the
# deposit, which the provenance row records. A future item text extraction
# maps trivially by position -- code n is the nth column of that battery.
#
# THE SCALE DIRECTION IS REVERSED FROM THE USUAL CONVENTION, and this is the
# single most important thing to know before modelling these tables. The paper:
# "Responses to the study variables were scored using a 5-point Likert scale,
# ranging from '1' to '5,' indicating the level of agreement with the item
# descriptions, varying from HIGH TO LOW." So resp = 1 is the STRONGEST
# agreement and resp = 5 the weakest -- the opposite of the overwhelmingly
# common 1 = strongly disagree convention, and the opposite of every other
# Likert table in this batch. Nothing in the data would reveal it; only that
# sentence does. It is stated in all four table descriptions, because a user
# who assumes the usual direction will get the sign of every correlation wrong.
#
# The four batteries, taken from the deposit's own numbering (each battery
# restarts at 1, and three of the four merge their instruction text into the
# first item's header, which is how the boundaries are visible):
#   cols  5-18  14 items  Perceptions of digital educational games -- knowledge
#                         of, family support for, and perceived importance of
#                         them. The paper calls this the project's own
#                         assessment (Cronbach's alpha 0.893).
#   cols 19-33  15 items  Motivation for learning. The paper derives this from
#                         the OECD "PIAAC Adult Literacy Survey Technical
#                         Report" chapter on "willingness to learn".
#   cols 34-48  15 items  The school's digital educational environment.
#   cols 49-63  15 items  Learning engagement / perceptions of participation.
# 59 items in all, every one on the same reversed 1-5 scale, zero missing
# cells. Four tables because the paper models them as four distinct variables
# (games -> motivation, mediated by engagement, moderated by environment), not
# as subscales of one instrument.
#
# A quirk left as it is: items 6 and 7 of the first battery read as yes/no
# questions ("Have you ever played a digital educational game?") yet were
# recorded on the same 1-5 scale as the rest. That is what the instrument did;
# it is not a coding error to repair, and the per-item distributions are in the
# data for anyone who wants to treat them separately.
#
# `id` is the deposit's own "Number", verified unique across all 434 rows.
#
# Covariates: place of residence (a 2-level urban/rural indicator, not a
# location, so the geographic ruling does not reach it), parents' education
# level, whether the home has basic network equipment, and general online
# gaming frequency.
#
# ADMINISTERED LANGUAGE IS UNCLEAR AND IS NOT GUESSED. The sample is at three
# universities in Thailand, but the deposited item wording is English and
# several items refer to "our school" in a register that reads as translated.
# The paper states no administration language and no translation procedure.
# `language` is therefore left as English -- the language of the wording that
# actually exists -- and this uncertainty is recorded in the provenance row
# rather than resolved by assumption.
#
# Item text: NOT SHIPPED, and for once the obstacle is neither the wording nor
# the mapping. Both are perfect: the headers are the verbatim stems and the
# header IS the column. Two things block it. (1) OPTIONS: the itemtext schema
# wants option_text per resp code, and the paper gives only "from high to low"
# -- no labels for the five points. Inventing anchors on a scale whose
# direction is already counter-conventional would be the worst possible place
# to guess. (2) MIXED RIGHTS: the first battery is the authors' own, but the
# motivation battery is derived from an OECD PIAAC instrument, so the four
# tables do not share one rights answer. Two register rows are written
# accordingly. Queued in TODO.md.
#
# PII: screened over all 64 columns. Every one is numeric; no names, emails,
# dates, free text or geography beyond the binary urban/rural indicator.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LI_DEG_RAW", "journal.pone.0294350_S1_Data.xlsx")

N_ROWS = 434
LO, HI = 1, 5

# (table, first column index, last column index, item count, code prefix, label)
BATTERIES = [
    ("li_2024_deg_perceptions", 5, 18, 14, "perc",
     "Perceptions of digital educational games"),
    ("li_2024_deg_motivation", 19, 33, 15, "mot", "Motivation for learning"),
    ("li_2024_deg_school_environment", 34, 48, 15, "env",
     "School digital educational environment"),
    ("li_2024_deg_engagement", 49, 63, 15, "eng", "Learning engagement"),
]
COV_IDX = {1: "cov_residence_urban_rural", 2: "cov_parent_education",
           3: "cov_home_network_equipment", 4: "cov_online_gaming_frequency"}
ID_IDX = 0


def screen_for_pii(df):
    txt = [c for c in df.columns
           if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert not txt, f"unexpected text column(s) -- screen them: {txt}"
    print("  every column is numeric; the only geography is a binary "
          "urban/rural indicator, which is not a location")


def convert():
    df = pd.read_excel(RAW, sheet_name=0)
    assert len(df) == N_ROWS, len(df)
    assert len(df.columns) == 64, len(df.columns)
    screen_for_pii(df)

    cols = list(df.columns)
    # every item block must be fully populated and strictly inside 1-5
    covered = set()
    for _, lo_i, hi_i, n, _, _ in BATTERIES:
        assert hi_i - lo_i + 1 == n, (lo_i, hi_i, n)
        covered |= set(range(lo_i, hi_i + 1))
    assert covered == set(range(5, 64)), "the four batteries do not tile cols 5-63"
    assert set(COV_IDX) | {ID_IDX} | covered == set(range(64))

    ren = {cols[ID_IDX]: "id"}
    ren.update({cols[i]: v for i, v in COV_IDX.items()})
    df = df.rename(columns=ren)
    cov_cols = sorted(COV_IDX.values())
    assert df["id"].nunique() == len(df), "Number is not unique"

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, lo_i, hi_i, n, prefix, label in BATTERIES:
        item_cols = cols[lo_i:hi_i + 1]
        assert len(item_cols) == n
        assert int(df[item_cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[item_cols].stack(), errors="coerce")
        assert vals.notna().all() and vals.between(LO, HI).all(), \
            (name, sorted(vals.unique()))

        # stable short codes in the deposit's own column order, so the join key
        # to a future item text table cannot break on text normalisation
        code = {c: f"{prefix}_{i:02d}" for i, c in enumerate(item_cols, 1)}
        long = df.rename(columns=code).melt(
            id_vars=["id"] + cov_cols, value_vars=list(code.values()),
            var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)

        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == n, (name, long["item"].nunique())
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name

        long = long[["id", "item", "resp"] + cov_cols]

        # gate before writing -- the contract check requires the validator to
        # run in-script, not just on the output file
        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in code.values()})
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

    assert total == 59 * N_ROWS, total
    print(f"4 tables, {total} responses (59 items x {N_ROWS} respondents, "
          f"no missing cells). NOTE resp=1 is STRONGEST agreement here")


if __name__ == "__main__":
    convert()
