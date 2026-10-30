#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0347530
# DOI: 10.1371/journal.pone.0347530
# Paper: Ren, L., Liu, Y., Siyal, A. W., Zhang, X., & Pu, T. (2026). Color
#   outside the lines: how does amoral management influence employees'
#   creative unethicality? PLOS ONE 21(4): e0347530.
# Data: journal.pone.0347530.s001 (S1 File, .xlsx), 249 rows x 26 columns.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 249 R&D employees at three intelligent-equipment manufacturers in eastern
# China, the surviving respondents of a three-wave design (350 sampled, 285
# valid at stage 1, 267 at stage 2, 249 at stage 3).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# FOUR output tables, 20 items, 4,980 responses, zero missing cells. The
# paper: five points, 1 "completely disagree" to 5 "completely agree".
#
# THE PREFIXES ARE NOT DEFINED IN THE ARTICLE, AND THE ITEM COUNTS ARE WHAT
# IDENTIFY THEM. The deposit heads its columns am/md/jcr/cu with no legend and
# the article never prints the prefixes. But it does give an item count per
# construct, and the four counts are distinct and match the four blocks
# exactly -- am 4, md 5, jcr 5, cu 6 against amoral management 4, moral
# decoupling 5, job creativity requirement 5, creative unethicality 6. With
# 4/5/5/6 and initials that match the construct names letter for letter
# (am/md/jcr/cu), the assignment is forced rather than guessed. The one
# ambiguity the counts cannot resolve is md versus jcr, both 5 -- the initials
# settle that, and the article's one printed example item per construct agrees
# with the direction of each block's content.
#
# ONE BLOCK IS NOT SELF-REPORT. The article's example item for creative
# unethicality is "Develops innovative ways to skirt ethical rules" -- third
# person, i.e. supervisor-rated, where the other three blocks are written in
# the first person. The deposit gives one row per employee either way, so `id`
# is the employee throughout, but cu responses are somebody else's judgements
# of that employee. Said in the description: pooling cu with the self-reports
# would mix two raters.
#
# ALL FIVE COVARIATES SHIP LABELLED, every one pinned against a published
# number:
#     gender   154 ones = 61.8% against "males 62%"      -> 1 male, 0 female
#     edu      181 at code 4, the paper's exact count for bachelor's degree
#     posi     155 at code 1, the paper's exact count for ordinary staff; and
#              codes 2+3 = 84 = 33.7%, the paper's exact figure for junior and
#              middle managers combined
#     tenure   96 at code 3 = 38.6% against "4-6 years, 39%"; 90 at code 4 =
#              36.1% against "7-10 years, 36%"
#     age      mean 34.09 and range 23-57 against "mean 34, range 23-57"
# `age` ships in years rather than as a band, which is the deposit's own
# resolution and is not a date of birth.
#
# JCR'S OBSERVED RANGE IS NARROWER THAN THE SCALE: its five items run 2-5 or
# 3-5 rather than 1-5. That is R&D employees agreeing that creativity is part
# of their job, not a different scale, so permitted values stay 1-5.
#
# `id` is the deposit's `no`, 1..249, verified unique.
#
# Item text: NOT SHIPPED. The article prints exactly ONE representative item
# per construct and attributes the full scales to Quade et al. (2022), Fehr et
# al. (2019), Yuan & Woodman (2010) and Mai et al. (2022). Four items out of
# twenty is not a table, and the other sixteen are third-party. Both barriers
# at once.
#
# PII: screened over all 26 columns. Every one is numeric; age is in years.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("REN_RAW", "journal.pone.0347530_S1_File.xlsx")

N_ROWS = 249
LO, HI = 1, 5

CONSTRUCTS = {
    "am": ("ren_2026_amoral_management", 4, "Amoral management (supervisor's "
           "non-involvement in ethical issues), employee-rated"),
    "md": ("ren_2026_moral_decoupling", 5, "Moral decoupling, self-rated"),
    "jcr": ("ren_2026_job_creativity_requirement", 5,
            "Job creativity requirement, self-rated"),
    "cu": ("ren_2026_creative_unethicality", 6,
           "Creative unethicality, SUPERVISOR-rated"),
}
COVS = {"gender": "cov_gender", "age": "cov_age", "edu": "cov_education",
        "posi": "cov_position", "tenure": "cov_tenure_band"}
# published numbers that license labelling the codes -- see the header
PINNED = [("gender", 1, 154), ("edu", 4, 181), ("posi", 1, 155),
          ("tenure", 3, 96), ("tenure", 4, 90)]


def convert():
    df = pd.read_excel(RAW)
    assert len(df) == N_ROWS, len(df)
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert not strings, f"unexpected string column(s): {strings}"
    print(f"PII screen: 0 string columns of {len(df.columns)}; age is in "
          f"years, not a date of birth")

    blocks = {}
    for c in df.columns:
        m = re.fullmatch(r"([a-z]+)(\d+)", str(c).strip())
        if m and m.group(1) in CONSTRUCTS:
            blocks.setdefault(m.group(1), []).append(c)
    got = {k: len(v) for k, v in blocks.items()}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    assert got == want, f"block counts are {got}, expected {want}"
    print(f"blocks identified by count and initials: {got} against the "
          f"paper's amoral management 4 / moral decoupling 5 / job creativity "
          f"requirement 5 / creative unethicality 6")

    accounted = {"no"} | set(COVS)
    for cols in blocks.values():
        accounted |= set(cols)
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"

    for col, code, n in PINNED:
        got_n = int((df[col] == code).sum())
        assert got_n == n, (
            f"{col}={code} has {got_n} rows, not the published {n} -- the "
            f"covariate labels rest on this, so do not ship them labelled")
    assert round(df["age"].mean()) == 34 and \
        (df["age"].min(), df["age"].max()) == (23, 57), "age no longer matches"
    print("covariates pinned: gender 1=male (154, 61.8% vs 'males 62%'), "
          "edu 4=bachelor's (181 exact), posi 1=ordinary staff (155 exact, and "
          "2+3=84=33.7% exact for junior+middle managers), tenure 3=4-6 years "
          "(38.6%) and 4=7-10 years (36.1%), age mean 34 range 23-57")

    assert df["no"].nunique() == len(df), "no is not unique"
    df = df.rename(columns={"no": "id", **COVS})
    cov_cols = sorted(COVS.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, n, label) in CONSTRUCTS.items():
        cols = sorted(blocks[prefix], key=lambda c: int(re.sub(r"\D", "", c)))
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
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}  [{label}]")

    assert total == 20 * N_ROWS, total
    print(f"4 tables, {total} responses (20 items x {N_ROWS} employees)")


if __name__ == "__main__":
    convert()
