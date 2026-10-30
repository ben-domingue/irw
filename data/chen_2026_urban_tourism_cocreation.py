#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0348028
# DOI: 10.1371/journal.pone.0348028
# Paper: Chen, G., et al. (2026). How host-guest interaction types shape value
#   co-creation in urban tourism. PLOS ONE 21(4).
# Data: Mendeley Data 10.17632/kb9f2c8xw4 -- date.xlsx, 507 rows x 37 columns.
#
# LICENCE verified on the DEPOSIT, not the article: the data is hosted off-site
# on Mendeley Data, whose dataset page states "Creative Commons Attribution
# 4.0 International" / CC BY 4.0. (The Mendeley public API's version endpoint
# 404s for this dataset, so the licence was read from the deposit page itself
# -- worth knowing for the next Mendeley-hosted lead.)
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# SIX output tables, 24 items, four per construct, all on a 7-point scale with
# zero missing cells. 507 urban tourism respondents.
#
#   TGI  4  Tourist-government interaction
#   TRI  4  Tourist-resident interaction
#   CI   4  Co-creation intention
#   CE   4  Customer empowerment
#   P    4  Passion
#   U    4  Usability
# The construct names come from the deposit itself rather than from inference:
# alongside the item blocks it carries seven Chinese-headed columns whose names
# translate directly to these constructs, and each is a fractional mean of its
# block (see below), so the mapping from prefix to construct is given by the
# file.
#
# SEVEN COMPOSITES DROPPED, EACH CONFIRMED FRACTIONAL FIRST. The Chinese-headed
# columns are subscale means, not items: every one holds values like 1.25 and
# 6.625 that cannot be a 7-point response. The script asserts each is
# fractional before dropping it, so a future file where one of them is actually
# an item would fail rather than lose data. One of the seven is worth naming:
# the AI-technology-stimulus column is ALSO a fractional mean, but its item
# block is NOT in the deposit -- so that construct exists in the analysis and
# not in the data, and no table can be built for it.
#
# `id` is the deposit's serial column (Chinese header for "serial number"),
# verified unique across all 507 rows. Covariates are the five Chinese-headed
# demographics: sex, occupation, education, age and income.
#
# Item text: NOT SHIPPED. The deposit holds construct-prefixed codes with no
# wording, and the measures are a tourism value-co-creation battery assembled
# from prior literature rather than study-authored. No register row -- the same
# assembled-from-the-literature shape already recorded in this batch.
#
# PII: screened over all 37 columns. Every one is numeric or a Chinese column
# header over numeric values; no names, emails, dates, free text or geography.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("CHEN_TOURISM_RAW", "date.xlsx")

N_ROWS = 507
LO, HI = 1, 7

CONSTRUCTS = {
    "TGI": ("chen_2026_tourist_govt_interaction", 4,
            "Tourist-government interaction"),
    "TRI": ("chen_2026_tourist_resident_interaction", 4,
            "Tourist-resident interaction"),
    "CI": ("chen_2026_cocreation_intention", 4, "Co-creation intention"),
    "CE": ("chen_2026_customer_empowerment", 4, "Customer empowerment"),
    "P": ("chen_2026_passion", 4, "Passion"),
    "U": ("chen_2026_usability", 4, "Usability"),
}
# Chinese headers: serial, sex, occupation, education, age, income
COV_HEADERS = ["\u6027\u522b", "\u804c\u4e1a", "\u6559\u80b2\u7a0b\u5ea6",
               "\u5e74\u9f84", "\u6536\u5165"]
COV_NAMES = ["cov_sex", "cov_occupation", "cov_education", "cov_age",
             "cov_income"]
ID_HEADER = "\u5e8f\u53f7"


def screen_for_pii(df):
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(strings)} string column(s) of {len(df.columns)}")
    assert not strings, f"unexpected string column(s): {strings}"
    print("  every column holds numbers; no name, email, date, free text or "
          "geographic column in this file")


def convert():
    df = pd.read_excel(RAW, sheet_name=0)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    found = {}
    for c in df.columns:
        m = re.fullmatch(r"([A-Z]+)(\d+)", str(c).strip())
        if m and m.group(1) in CONSTRUCTS:
            found.setdefault(m.group(1), []).append(c)
    got = {k: len(v) for k, v in found.items()}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    assert got == want, f"construct counts are {got}, expected {want}"
    items = [c for cols in found.values() for c in cols]

    assert ID_HEADER in df.columns, "the serial column is gone"
    for h in COV_HEADERS:
        assert h in df.columns, f"covariate column {h!r} is gone"

    composites = [c for c in df.columns
                  if c not in items and c != ID_HEADER and c not in COV_HEADERS]
    assert len(composites) == 7, (len(composites), composites)
    for c in composites:
        s = pd.to_numeric(df[c], errors="coerce").dropna()
        assert ((s % 1) != 0).any(), (
            f"{c} holds no fractional value, so it may be an item rather than "
            f"a subscale mean -- recheck before dropping it")
    print(f"dropped {len(composites)} subscale-mean columns, each confirmed to "
          f"hold fractional values. One of them is an AI-technology-stimulus "
          f"mean whose ITEM BLOCK IS NOT IN THE DEPOSIT, so that construct "
          f"cannot be built as a table at all")

    assert df[ID_HEADER].nunique() == len(df), "the serial column is not unique"
    df = df.rename(columns={ID_HEADER: "id",
                            **dict(zip(COV_HEADERS, COV_NAMES))})
    cov_cols = sorted(COV_NAMES)

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, n, label) in CONSTRUCTS.items():
        cols = sorted(found[prefix], key=lambda c: int(re.sub(r"\D", "", str(c))))
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        stacked = df[cols].stack().dropna()
        assert pd.to_numeric(stacked, errors="coerce").notna().all(), name
        vals = pd.to_numeric(stacked)
        assert vals.between(LO, HI).all(), (name, sorted(vals.unique()))

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
                print(f"  [qc warn] {name} {c.name}: {c.detail[:135]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}  [{label}]")

    assert total == 24 * N_ROWS, total
    print(f"6 tables, {total} responses (24 items x {N_ROWS} respondents, "
          f"no missing cells)")


if __name__ == "__main__":
    convert()
