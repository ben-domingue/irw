#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0248460
# DOI: 10.1371/journal.pone.0248460
# Paper: Tian, Z., Shi, Z., & Cheng, Q. (2021). Examining the antecedents and
#   consequences of mobile travel app engagement. PLOS ONE 16(3): e0248460.
# Data: journal.pone.0248460.s002 (.xlsx), 303 rows x 27 columns.
#   Item wording: .s001, "Appendix A", a .doc (not .docx).
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 303 Chinese mobile travel app users, snowball sample, 7-12 January 2020
# (330 collected, 27 excluded; non-users screened out).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# SEVEN output tables, 21 items, 6,363 responses, zero missing cells. The
# paper: 5-point, 1 "strongly disagree" to 5 "strongly agree".
#
# TWO CODE MISMATCHES BETWEEN THE APPENDIX AND THE DEPOSIT, both resolved and
# both left in the data as the deposit wrote them:
#   * The appendix's seventh construct is PURCHASE INTENTION, items PI1..PI3.
#     The deposit's seventh block is PE1..PE3. PI appears nowhere in the data
#     and PE appears nowhere in the appendix, and each is the only unmatched
#     block on its side, so the identity is forced rather than guessed.
#   * The appendix's BE2 is headed BE22 in the deposit -- a typo, but the item
#     ships as BE22 because that is what the column is called.
#   Renaming either one to match the prose would make the table disagree with
#   its own source; the crosswalk lives in the item-text script instead.
#
# THE OTHER FIVE PREFIXES MATCH EXACTLY (EOU, COM, UIA, CE, AE, BE), three
# items each, 7 x 3 = 21 = the number of item columns.
#
# THE APPENDIX IS A .doc, NOT A .docx, which is worth recording because the
# usual zipfile route fails on it outright and the triage's "no usable file"
# verdict for S1 was wrong for the same reason. It was read by converting with
# libreoffice --headless --convert-to txt. One artefact survives in the source
# itself: COM1 reads "compatible with my travel p References." in both the
# original and the conversion -- an OCR-or-paste corruption of "preferences"
# that is the AUTHORS', not this pipeline's. It ships verbatim; silently
# repairing a published item is not this script's job, and the note is here so
# nobody re-diagnoses it as a conversion bug.
#
# FOUR COVARIATES SHIP LABELLED, each pinned against a published percentage:
#     gender   126 / 177 = 41.6% / 58.4%   -> 1 male, 2 female
#     age      code 2 = 186 = 61.4%, the paper's 18-30 band
#     education codes 3+4 = 267 = 88.1%, the paper's three- or four-year
#              bachelor's; codes 1+2 = 36 = 11.9%, its high school or
#              technical secondary. Four ordered codes, two published groups.
#     salary   code 3 = 93 = 30.7%, the paper's 3,001-5,000 RMB band, and
#              code 4 = 63 = 20.8%, its 5,001-8,000 band -- which also settles
#              an ambiguity in the article's own text, where the 20.8% figure
#              is written as though it covered two bands at once.
# `Regular app` is DROPPED: eight nominal app brands with no legend.
#
# `id` is the deposit's `Serial number`, verified unique over all 303 rows.
#
# Item text: SHIPPED, all 21 items, from Appendix A. See
# tian_2021_travel_app_itemtext.py.
#
# PII: screened over all 27 columns. Every one is numeric.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("TIAN_RAW", "journal.pone.0248460_S2_File.xlsx")

N_ROWS = 303
LO, HI = 1, 5

CONSTRUCTS = {
    "EOU": ("tian_2021_app_ease_of_use", "Ease of use"),
    "COM": ("tian_2021_app_compatibility", "Compatibility"),
    "UIA": ("tian_2021_app_ui_attractiveness", "UI attractiveness"),
    "CE": ("tian_2021_app_cognitive_engagement", "Cognitive engagement"),
    "AE": ("tian_2021_app_affective_engagement", "Affective engagement"),
    "BE": ("tian_2021_app_behavioral_engagement", "Behavioural engagement"),
    "PE": ("tian_2021_app_purchase_intention",
           "Purchase intention (the appendix's PI block)"),
}
COVS = {"Gender": "cov_gender", "Age": "cov_age_band",
        "Education": "cov_education", "Monthly salary": "cov_salary_band"}
DROP = {"Regular app": "8 nominal app brands with no legend"}
PINNED = [("Gender", [1], 126), ("Gender", [2], 177), ("Age", [2], 186),
          ("Education", [3, 4], 267), ("Education", [1, 2], 36),
          ("Monthly salary", [3], 93), ("Monthly salary", [4], 63)]


def blocks_of(df):
    out = {}
    for c in df.columns:
        m = re.fullmatch(r"(EOU|COM|UIA|CE|AE|BE|PE)(\d+)", str(c).strip())
        if m:
            out.setdefault(m.group(1), []).append(str(c))
    return out


def convert():
    df = pd.read_excel(RAW)
    assert len(df) == N_ROWS, len(df)
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert not strings, f"unexpected string column(s): {strings}"
    print(f"PII screen: 0 string columns of {len(df.columns)}")

    blocks = blocks_of(df)
    assert {k: len(v) for k, v in blocks.items()} == \
        {k: 3 for k in CONSTRUCTS}, {k: len(v) for k, v in blocks.items()}
    assert "BE22" in blocks["BE"], (
        "the deposit's BE2 typo (BE22) is gone -- the item-text crosswalk "
        "assumes it, so recheck")
    assert not any(c.startswith("PI") for c in df.columns), (
        "a PI block now exists in the deposit, so the PE=purchase-intention "
        "identification is no longer forced -- recheck")
    print("code mismatches handled: the appendix's PI1-3 are the deposit's "
          "PE1-3 (each the only unmatched block on its side), and the "
          "appendix's BE2 is the deposit's BE22. Both ship as the deposit "
          "writes them")

    accounted = {"Serial number"} | set(COVS) | set(DROP)
    for cols in blocks.values():
        accounted |= set(cols)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    print(f"dropped: " + "; ".join(f"{k} ({v})" for k, v in DROP.items()))

    for col, codes, n in PINNED:
        got = int(df[col].isin(codes).sum())
        assert got == n, (
            f"{col} in {codes} has {got} rows, not the published {n} -- the "
            f"covariate labels rest on this match")
    print("covariates pinned: gender 1=male (41.6%), age 2=18-30 (61.4%), "
          "education 3+4=bachelor's (88.1%) and 1+2=secondary (11.9%), "
          "salary 3=3,001-5,000 RMB (30.7%) and 4=5,001-8,000 (20.8%)")

    assert df["Serial number"].nunique() == len(df), "serial is not unique"
    df = df.rename(columns={"Serial number": "id", **COVS})
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, label) in CONSTRUCTS.items():
        cols = sorted(blocks[prefix], key=lambda c: int(re.sub(r"\D", "", c)))
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all() and vals.between(LO, HI).all(), \
            (name, sorted(vals.unique()))

        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == 3
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name
        long = long[["id", "item", "resp"] + cov_cols]

        checks = run_qc(long, permitted_values={i: list(range(LO, HI + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:140]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items=3 resp={long['resp'].min()}-{long['resp'].max()}  "
              f"[{label}]")

    assert total == 21 * N_ROWS, total
    print(f"7 tables, {total} responses (21 items x {N_ROWS} respondents)")


if __name__ == "__main__":
    convert()
