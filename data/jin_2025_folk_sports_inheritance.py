#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0336798
# DOI: 10.1371/journal.pone.0336798
# Paper: Jin, X., & Hou, Y. (2025). A comparative study on folk sports
#   inheritance in China and South Korea: influencing factors and mediating
#   roles. PLOS ONE 20(11): e0336798.
# Data: journal.pone.0336798.s001 (S1 File, "Sample Data-China", 336 rows) AND
#   .s002 (S2 File, "Sample Data-South Korea", 331 rows), 37 columns each.
# License: CC BY 4.0 -- Supporting Information of the article itself.
# 667 valid responses from inheritors, participants, researchers and
# educators, and administrators of folk sports (370 distributed in China via
# Wenjuanxing, 350 in South Korea via Google Forms).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# FIVE output tables, 32 items, 21,344 responses, zero missing cells. The
# paper: five-point, 1 strongly disagree, 2 disagree, 3 neutral, 4 agree,
# 5 strongly agree -- all five labels published, which is unusual in this
# batch and is why item text would have been worth having.
#
# BOTH COUNTRY FILES SHIP AS ONE TABLE PER CONSTRUCT, which is the point of
# the study. The lead counted only the Chinese file (336 respondents); the
# Korean file has the IDENTICAL 37 columns, so the two concatenate cleanly
# into the comparison the article is actually about. Checked rather than
# assumed: the column lists are compared element by element below, and the
# join is refused if they ever differ. Contrast wang_2023_eco_* in this same
# batch, where two files of identical SHAPE turned out to number five shared
# items differently -- here the headers are the same strings.
#
# `cov_country` carries the split, and `id` is prefixed CN/KR because both
# files number their respondents from 1.
#
# THE SECTION LETTERS MAP TO THE PAPER'S FIVE CONSTRUCTS BY COUNT AND ORDER.
# The article never mentions lettered sections; it lists five constructs with
# 7, 6, 6, 7 and 6 observed variables, totalling 32. The deposit's blocks are
# B(7), C(6), D(6), E(7), F(6) in that order, totalling 32, after A1-A4 which
# are demographics on their own small scales. The count sequence 7-6-6-7-6 is
# not symmetric, so the alignment is forced by order:
#   B  7  Inheritance subject        E  7  Inheritance environment
#   C  6  Inheritance object         F  6  Inheritance effect
#   D  6  Inheritance intermediary
#
# THE FOUR DEMOGRAPHIC COLUMNS ARE DROPPED. A1 (2 levels), A2 (4), A3 (4) and
# A4 (3) have the same level counts in both countries, but the article's
# Table 1 is not in its readable text and nothing names them. One of them is
# almost certainly the respondent group the stratification is built on
# (inheritors / participants / researchers and educators / administrators --
# four categories, matching A2 or A3), which would be a genuinely valuable
# covariate; which one, and in what order, cannot be established, so none
# ships. That is the most costly covariate drop in this batch and it is a
# drop rather than a guess.
#
# Item text: NOT SHIPPED. Neither supporting file carries wording -- both are
# data -- and the article does not print the 32 observed variables. An
# availability gap.
#
# PII: screened over all 74 columns of the two files. Every one is numeric.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW_CN = os.environ.get("JIN_CN", "journal.pone.0336798_S1_File.xlsx")
RAW_KR = os.environ.get("JIN_KR", "journal.pone.0336798_S2_File.xlsx")

N_CN, N_KR = 336, 331
LO, HI = 1, 5

CONSTRUCTS = {
    "B": ("jin_2025_folk_inheritance_subject", 7, "Inheritance subject"),
    "C": ("jin_2025_folk_inheritance_object", 6, "Inheritance object"),
    "D": ("jin_2025_folk_inheritance_intermediary", 6,
          "Inheritance intermediary"),
    "E": ("jin_2025_folk_inheritance_environment", 7,
          "Inheritance environment"),
    "F": ("jin_2025_folk_inheritance_effect", 6, "Inheritance effect"),
}
DEMOGRAPHICS = ["A1", "A2", "A3", "A4"]
ITEM = re.compile(r"^([BCDEF])(\d+)$")


def load(path, n, country, prefix, id_col):
    df = pd.read_excel(path)
    assert len(df) == n, (country, len(df))
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert not strings, f"{country}: unexpected string column(s): {strings}"
    assert df[id_col].nunique() == len(df), f"{country}: {id_col} not unique"
    df = df.rename(columns={id_col: "_no"})
    df["id"] = prefix + df["_no"].astype(int).astype(str)
    df["cov_country"] = country
    return df


def convert():
    cn = load(RAW_CN, N_CN, "China", "CN", "CHINA-NO.")
    kr = load(RAW_KR, N_KR, "South Korea", "KR", "KOREA-NO.")
    shared = [c for c in cn.columns if c not in ("id", "cov_country", "_no")]
    assert shared == [c for c in kr.columns
                      if c not in ("id", "cov_country", "_no")], (
        "the two country files no longer have identical column lists -- do "
        "NOT concatenate them until the difference is understood; see "
        "wang_2023_eco_* in this batch for what that can hide")
    print(f"PII screen: 0 string columns across both files "
          f"({2 * len(shared) + 2} columns)")
    print(f"both country files carry the identical {len(shared)} columns, "
          f"compared element by element -- safe to concatenate")

    blocks = {}
    for c in shared:
        m = ITEM.match(str(c))
        if m:
            blocks.setdefault(m.group(1), []).append(str(c))
    got = {k: len(v) for k, v in blocks.items()}
    want = {k: v[1] for k, v in CONSTRUCTS.items()}
    assert got == want, f"block counts are {got}, expected {want}"
    assert sum(got.values()) == 32, sum(got.values())
    print(f"section letters mapped to the paper's five constructs by the "
          f"count sequence 7-6-6-7-6, which is not symmetric: {got}")

    accounted = set(DEMOGRAPHICS) | {c for v in blocks.values() for c in v}
    left_out = [c for c in shared if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    print(f"dropped {len(DEMOGRAPHICS)} demographic columns "
          f"({', '.join(DEMOGRAPHICS)}): the article's Table 1 is not in its "
          f"readable text and nothing names them. One is probably the "
          f"respondent-group stratifier, which would be valuable -- but "
          f"which, and in what order, cannot be established")

    df = pd.concat([cn, kr], ignore_index=True)
    assert df["id"].nunique() == N_CN + N_KR

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for prefix, (name, n, label) in CONSTRUCTS.items():
        cols = sorted(blocks[prefix], key=lambda c: int(c[1:]))
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all() and vals.between(LO, HI).all(), \
            (name, sorted(vals.unique()))

        long = df.melt(id_vars=["id", "cov_country"], value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_CN + N_KR
        assert long["item"].nunique() == n
        assert not long.duplicated(["id", "item"]).any()
        assert len(long) == n * (N_CN + N_KR), (name, len(long))
        assert len(name) <= 40, name
        long = long[["id", "item", "resp", "cov_country"]]

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
              f"items={n} resp={long['resp'].min()}-{long['resp'].max()}  "
              f"[{label}]")

    assert total == 32 * (N_CN + N_KR), total
    print(f"5 tables, {total} responses (32 items x {N_CN + N_KR} "
          f"respondents in two countries)")


if __name__ == "__main__":
    convert()
