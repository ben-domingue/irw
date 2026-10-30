#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0324415
# DOI: 10.1371/journal.pone.0324415
# Paper: Zhang, D., Qi, Z., Wu, L., Mao, Y., Wang, J., Zhang, Y., Wang, R., &
#   Liu, A. (2025). Fear of falling and depression in older adults: The
#   mediating role of attitudes toward aging and social networks.
#   PLOS ONE 20(11).
# Data: figshare 10.6084/m9.figshare.29994334 -- data.xlsx, one sheet,
#   1,117 rows x 66 columns. Downloaded from
#   https://ndownloader.figshare.com/files/57453586
#
# LICENCE verified on the DEPOSIT, not the article: the Data Availability
# statement points off-site to figshare ("openly stored on the Figshare
# platform"), and an article's licence cannot grant a separate deposit's.
# api.figshare.com/v2/articles/29994334 reports CC BY 4.0. The article is also
# CC BY 4.0, so they agree -- but it had to be asked, which is the same check
# that hocine_2016_psychosocial_stressors needed in this batch.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# FOUR output tables -- four separate published instruments, each named by the
# paper's Methods section and each on its own response scale, so no merge
# question arises:
#   FE1-FE14    Modified Falls Efficacy Scale (MFES), Chinese version. 14 items
#               (the paper: "9 covering indoor activities and 5 covering
#               outdoor activities"), each "rated on an 11-point scale from
#               0 (no confidence) to 10 (complete confidence)".
#   Depre1-15   Geriatric Depression Scale-15 (GDS-15). 15 items, 0/1.
#   AAQ1-AAQ24  Attitudes to Ageing Questionnaire, the Chinese revision of
#               Huang, Wang, Liu & Laidlaw (2010). 24 items across Psychological
#               Growth, Physical Change and Psychosocial Loss, 5-point Likert.
#   SI1-SI6     Lubben Social Network Scale-6 (LSNS-6). 6 items, 6-point
#               (0-5), two domains (family network, friends network).
#
# THE AAQ VALUES ARE ALREADY REVERSE-ADJUSTED, and the deposit says so in an
# unusual place -- the sheet name. It reads
# "补充完整版1117-龙岗调研数据2(已调整过老化态度)", whose parenthetical is
# "aging attitudes have already been adjusted". The paper independently states
# that "Items in the Psychosocial Loss domain are reverse scored". So for those
# items the number in `resp` is NOT the category the respondent selected; it is
# the authors' direction-corrected value. Said in the table description,
# because a reverse-item analysis of this table would otherwise double-reverse
# them. The script asserts the sheet name still carries that marker, so a
# re-deposit without it fails here rather than shipping a silently different
# thing.
#
# GDS-15 NONRESPONSE IS WHOLE-SCALE, NOT ITEM-LEVEL, which is why it is safe to
# drop: every one of the 15 Depre columns has exactly 2 missing cells, i.e. two
# respondents skipped the entire GDS and nobody skipped individual items. The
# script asserts that shape (exactly 2 per column, and the missing rows
# identical across all 15) rather than just calling dropna, because
# item-level missingness would be a different fact worth knowing. The other
# three instruments have no missing cells at all.
#
# `id` is the deposit's own ID, verified unique over all 1,117 rows.
#
# STUDY SITE IS NOT SHIPPED, and there is nothing to strip: the sheet name
# contains 龙岗 (Longgang, a district of Shenzhen), but that is a sheet name,
# not a column, and no row-level geography exists in the file. Noted because
# the site is in the provenance rather than in the data.
#
# Covariates: sex, age, residence type, marital status, education, living
# arrangement. Age is the exact year and ranges 60-102 -- kept because the
# sample is 1,117 and the file carries no geography, so a single year is not a
# re-identification handle here.
#
# Item text: NOT SHIPPED for any of the four, on rights, and all four are
# named third-party instruments with no wording anywhere in the deposit (the
# columns are bare codes) and none printed in the article. Register rows are
# written for the three that had none; the LSNS-6 and MFES are both common in
# ageing research, so those rows will be hit again.
#
# PII: screened over all 66 columns. Every one is numeric -- no names, emails,
# dates, free text or row-level geography.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ZHANG_FOF_RAW", "data.xlsx")

N_ROWS = 1117
# the parenthetical marking the AAQ reverse-adjustment
SHEET_MARKER = "已调整过老化态度"

# prefix -> (table, n_items, lo, hi)
BLOCKS = {
    "FE": ("zhang_2025_mfes", 14, 0, 10),
    "Depre": ("zhang_2025_gds15", 15, 0, 1),
    "AAQ": ("zhang_2025_aaq", 24, 1, 5),
    "SI": ("zhang_2025_lsns6", 6, 0, 5),
}
COVS = {"Sex": "cov_sex", "Age": "cov_age", "Live": "cov_residence_type",
        "Marrige": "cov_marital_status", "Education": "cov_education",
        "Living_with": "cov_living_arrangement"}
DROP = {"ID": "record number -- becomes id"}


def screen_for_pii(df):
    txt = [c for c in df.columns
           if pd.api.types.is_string_dtype(df[c])
           and pd.to_numeric(df[c], errors="coerce").isna().any()]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert not txt, f"unexpected text column(s) -- screen them: {txt}"
    assert all(pd.to_numeric(df[c], errors="coerce").notna().all()
               for c in df.columns if c not in
               [c for c in df.columns if df[c].isna().any()]), "non-numeric"
    print("  every column is numeric; no row-level geography (the study site "
          "appears only in the sheet name, which is not data)")


def check_gds_missingness(df, cols):
    """Whole-scale nonresponse is droppable; item-level would be a different
    fact. Assert the shape instead of trusting dropna to be harmless."""
    per = {c: int(df[c].isna().sum()) for c in cols}
    assert set(per.values()) == {2}, f"GDS-15 missingness is not uniform: {per}"
    rows = [frozenset(df.index[df[c].isna()]) for c in cols]
    assert len(set(rows)) == 1, "GDS-15 missing cells are not the same 2 rows"
    print(f"GDS-15: exactly 2 missing cells per item, and the same 2 "
          f"respondents in every one -- whole-scale nonresponse, not "
          f"item-level; those 2 ids are absent from that table only")


def convert():
    xl = pd.ExcelFile(RAW)
    sheet = xl.sheet_names[0]
    assert SHEET_MARKER in sheet, (
        f"the sheet name no longer carries the AAQ reverse-adjustment marker "
        f"{SHEET_MARKER!r}: {sheet!r}. The AAQ description depends on it.")
    print(f"sheet {sheet!r} carries the AAQ reverse-adjustment marker")
    df = xl.parse(sheet)
    assert len(df) == N_ROWS, len(df)
    screen_for_pii(df)

    found = {}
    for c in df.columns:
        m = re.match(r"^([A-Za-z]+)(\d+)$", str(c))
        if m and m.group(1) in BLOCKS:
            found.setdefault(m.group(1), []).append(c)
    for p, (_, n, _, _) in BLOCKS.items():
        got = len(found.get(p, []))
        assert got == n, (p, got, n)

    accounted = set(COVS) | set(DROP)
    for cols in found.values():
        accounted |= set(cols)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"

    check_gds_missingness(df, found["Depre"])
    for p in ("FE", "AAQ", "SI"):
        assert int(df[found[p]].isna().sum().sum()) == 0, (p, "missing cells")

    assert df["ID"].nunique() == len(df), "ID is not unique"
    df = df.rename(columns={"ID": "id", **COVS})
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for p, (name, n, lo, hi) in BLOCKS.items():
        cols = sorted(found[p], key=lambda c: int(re.sub(r"\D", "", str(c))))
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)

        assert long["resp"].between(lo, hi).all(), (name, long["resp"].unique())
        assert long["id"].nunique() >= 100, (name, long["id"].nunique())
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name

        long = long[["id", "item", "resp"] + cov_cols]

        # gate before writing -- the contract check requires the validator to
        # run in-script, not just on the output file
        checks = run_qc(long, permitted_values={i: list(range(lo, hi + 1))
                                                for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")

    assert total == 59 * N_ROWS - 30, total
    print(f"4 tables, {total} responses (59 items x {N_ROWS} respondents, "
          f"less the 30 cells of whole-scale GDS-15 nonresponse)")


if __name__ == "__main__":
    convert()
