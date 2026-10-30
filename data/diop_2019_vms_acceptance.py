#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0216007
# DOI: 10.1371/journal.pone.0216007
# Paper: Diop, E. B., Zhao, S., & Duy, T. V. (2019). An extension of the
#   technology acceptance model for understanding travelers' adoption of
#   variable message signs. PLOS ONE 14(4).
# Data: journal.pone.0216007.s001 (S1 File, .xlsx), sheet 'Indicators',
#   762 rows x 38 columns.
# License: CC BY 4.0 (Crossref licence record for the version of record; the
#   data is a Supporting Information file of the article itself).
# 762 travellers surveyed about variable message signs (VMS).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# FIVE output tables, 17 items. A small deposit by this batch's standards, and
# two of its 38 columns are the reason to read the header before using it.
#
# THE ATT BLOCK IS NOT SHIPPED: attitude is measured with only TWO items
# (ATT1, ATT2). IRW ships no table with fewer than three distinct items, so
# this construct is dropped entirely rather than padded or merged into a
# neighbouring one. That is a real loss -- attitude is a named construct in
# the paper's TAM extension -- and it is the floor doing its job, not an
# oversight.
#
#   PU    4 items  Perceived usefulness
#   PEOU  4 items  Perceived ease of use
#   IQ    3 items  Information quality
#   FAM   3 items  Familiarity
#   BI    3 items  Behavioural intention
#   (ATT  2 items  Attitude -- NOT SHIPPED, below the three-item floor)
#
# All on a 5-point scale, zero missing cells. Note PU, BI and ATT never attract
# a 1 from any respondent: their observed ranges are 2-5 while PEOU, IQ and FAM
# run 1-5. An unendorsed bottom anchor is a fact about the responses rather
# than a different scale, so permitted values stay 1-5 throughout.
#
# THE COVARIATES ARE A PRE-DUMMIED DESIGN MATRIX, and this deposit is where the
# line between "undocumented" and "self-naming" had to be drawn. All 18
# non-item columns are 0/1 dummies with implicit reference categories -- this
# is the regression matrix, not the questionnaire's demographics. They split
# three ways:
#   SHIPPED (14) -- dummies whose NAME states the category the 1 means:
#     MIDAGE, OLD, ASSO, BACH, GRAD, MARRC, MARRNC, MID_INC, HIGH_INC, STUD,
#     PRIVATE, OTHERJOB, MIDEXP, HIGHEXP. "ASSO = 1" is unambiguously "holds an
#     associate degree"; nothing has to be guessed, and the implicit reference
#     category is recoverable by elimination within each family.
#   DROPPED, ambiguous (1) -- GENDER. A 0/1 column named only "GENDER" does
#     not say which sex is 1, and 492 of 762 being 1 does not settle it. A
#     covariate whose direction is unknown is worse than no covariate.
#   DROPPED, opaque (3) -- INFO_B, EXP_B, INFOEXP_B. The names do not state a
#     category and the article does not define them. Checked whether INFOEXP_B
#     is the INFO_B x EXP_B interaction, which would have made it derived: it
#     is not (479 ones against a product with far fewer), so it is a third
#     unexplained indicator rather than a product to discard. Dropped either
#     way, and the check is in the script so the reasoning is not lost.
# This is the same rule applied to lin_2024_escooter_* (nine columns named `1`
# through `9`, all dropped) and lin_2026_advertising_literacy (No2/No4/No5
# dropped) earlier in this batch -- the difference here is that a name like
# `BACH` carries its own meaning where `1` and `No4` carry none.
#
# `id` is the deposit's `num`, verified unique over all 762 rows.
#
# Item text: NOT SHIPPED. The deposit holds only construct-prefixed codes
# (PU1..BI3) and no wording, and the measures are a TAM extension adapted from
# the technology-acceptance literature rather than study-authored. This is the
# fourth UTAUT/TAM-family deposit in this batch, so no new register row is
# written -- the existing `TAM-SERVQUAL-SE` and `UTAUT2-STREAM` rows already
# record the same reasoning, and the TODO item asking for a general ruling on
# the UTAUT/TAM item pool covers this one too.
#
# PII: screened over all 38 columns. Every one is numeric; no names, emails,
# dates, free text or geography.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("DIOP_RAW", "journal.pone.0216007_S1_File.xlsx")

N_ROWS = 762
LO, HI = 1, 5

CONSTRUCTS = {
    "PU": ("diop_2019_vms_usefulness", 4, "Perceived usefulness"),
    "PEOU": ("diop_2019_vms_ease_of_use", 4, "Perceived ease of use"),
    "IQ": ("diop_2019_vms_info_quality", 3, "Information quality"),
    "FAM": ("diop_2019_vms_familiarity", 3, "Familiarity"),
    "BI": ("diop_2019_vms_intention", 3, "Behavioural intention"),
}
# below the three-item floor -- dropped, not merged (see header)
BELOW_FLOOR = ("ATT", 2)

# dummies whose name states the category the 1 means
COVS = {c: "cov_" + c.lower() for c in
        ["MIDAGE", "OLD", "ASSO", "BACH", "GRAD", "MARRC", "MARRNC",
         "MID_INC", "HIGH_INC", "STUD", "PRIVATE", "OTHERJOB",
         "MIDEXP", "HIGHEXP"]}
DROP_AMBIGUOUS = ["GENDER"]                      # 0/1 but which sex is 1?
DROP_OPAQUE = ["INFO_B", "EXP_B", "INFOEXP_B"]   # names state no category


def screen_for_pii(df):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(strings)} string column(s) of {len(df.columns)}: "
          f"{strings}")
    assert not strings, f"unexpected string column(s) -- screen them: {strings}"
    print("  every column is numeric; no name, email, date, free text or "
          "geographic column in this file")


def convert():
    df = pd.read_excel(RAW, sheet_name="Indicators")
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

    floor_pre, floor_n = BELOW_FLOOR
    assert len(found.get(floor_pre, [])) == floor_n, (
        f"{floor_pre} has {len(found.get(floor_pre, []))} items, expected "
        f"{floor_n}; if it now clears the three-item floor it should ship")
    print(f"NOT shipping {floor_pre} ({floor_n} items): below the three-item "
          f"floor. Attitude is a named construct in the paper's model, so this "
          f"is a real loss, not an oversight")

    # INFOEXP_B would be derived if it were the product; it is not
    prod_match = bool((df["INFO_B"] * df["EXP_B"] == df["INFOEXP_B"]).all())
    assert not prod_match, (
        "INFOEXP_B now equals INFO_B*EXP_B, i.e. it IS a derived interaction "
        "term -- the header says it is not, so recheck before shipping")
    print(f"dropped {len(DROP_AMBIGUOUS)} ambiguous dummy ({DROP_AMBIGUOUS[0]}: "
          f"0/1 with no statement of which sex is 1) and {len(DROP_OPAQUE)} "
          f"opaque dummies ({', '.join(DROP_OPAQUE)}; checked and NOT an "
          f"interaction term)")

    accounted = set(COVS) | set(DROP_AMBIGUOUS) | set(DROP_OPAQUE) | {"num"}
    for cols in found.values():
        accounted |= set(cols)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"

    for c in COVS:
        assert set(df[c].dropna().unique()) <= {0, 1}, (c, "not a 0/1 dummy")
    assert df["num"].nunique() == len(df), "num is not unique"
    df = df.rename(columns={"num": "id", **COVS})
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, n, label) in CONSTRUCTS.items():
        cols = sorted(found[prefix], key=lambda c: int(re.sub(r"\D", "", str(c))))
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all() and vals.between(LO, HI).all(), \
            (name, sorted(vals.unique()))

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)

        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name

        long = long[["id", "item", "resp"] + cov_cols]

        # gate before writing -- the contract check requires the validator to
        # run in-script, not just on the output file
        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in cols})
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

    assert total == 17 * N_ROWS, total
    print(f"5 tables, {total} responses (17 items x {N_ROWS} respondents; "
          f"{floor_n} ATT items withheld below the floor)")


if __name__ == "__main__":
    convert()
