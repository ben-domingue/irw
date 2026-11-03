#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0206647
# DOI: 10.1371/journal.pone.0206647
# Paper: Esmaeilzadeh S, Ashrafi-rizi H, Shahrzadi L, Mostafavi F (2018). A
#   survey on adolescent health information seeking behavior related to
#   high-risk behaviors in a selected educational district in Isfahan.
#   PLOS ONE 13(11): e0206647.
# Data: S2 Table (journal.pone.0206647.s003, "Raw data", .sav), 392 high-school
#   students aged 15-19, Isfahan, Iran. The English questionnaire is S1 Text
#   (journal.pone.0206647.s001); the value labels are transliterated Persian.
# License: CC BY 4.0 (article; the data is the article's own SI).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (slice 4, BATCH_LOG.md).
#
# PII: the questionnaire asked for an address or neighbourhood name (Q4); that
#   column is NOT in the deposit. The .sav has no text columns at all.
#
# FIVE output tables, the questionnaire's 5-point batteries (asked only of
# students who reported needing health information in the last six months,
# hence ~300 respondents each):
#   esmaeilzadeh_2018_info_for_whom    X10_1..7  for whom health information was
#     sought (myself, parents, siblings, ...), 1 very slightly .. 5 very greatly
#   esmaeilzadeh_2018_topic_curiosity  X11_1..6  curiosity about six high-risk
#     behaviour topics, 1 very slightly .. 5 very greatly
#   esmaeilzadeh_2018_info_sources     X12_1..12 use of twelve information
#     sources, 1 very slightly .. 5 very greatly
#   esmaeilzadeh_2018_info_attitudes   X18_1..5  attitudes to seeking health
#     information, 1 strongly disagree .. 5 strongly agree (the .sav's value
#     labels; the printed questionnaire lists the anchors the other way round)
#   esmaeilzadeh_2018_quality_criteria X20_1..16 how often sixteen criteria are
#     used to judge information quality, 1 never .. 5 always
# NOT SHIPPED: X19_1..8 (obstacles). Its value labels run 1 "kam" (low),
#   2 "besyar kam" (very low), 3 moderate, 4 high, 5 very high, and the printed
#   questionnaire offers the same disordered row of anchors, so the order of
#   codes 1 and 2 cannot be read as a scale. Also X6/X8/X14 (yes/no), X7, X9,
#   X13, X15, X16, X17 (single questions or nominal choices), and the three
#   derived 0-100 scores (konjkavi100, negaresh100, mavane100).
# Covariates: sex (girl/boy, value labels), age.
# Dropped: Educate (constant 4 "university", which contradicts a high-school
#   sample), Income (half missing, free-entered amounts).
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. The English questionnaire (S1 Text) has every stem,
#   but the administration was in Persian, and the Persian wording is not in
#   the deposit (the .sav has value labels only, transliterated; no variable
#   labels on any item).

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ESMAEILZADEH_RAW", "journal.pone.0206647.s003.sav")
BLOCKS = {
    "info_for_whom": ("X10_", 7, "besyar kam", "besyar ziad"),
    "topic_curiosity": ("X11_", 6, "besyar kam", "besyar ziad"),
    "info_sources": ("X12_", 12, "besyar kam", "besyar ziad"),
    "info_attitudes": ("X18_", 5, "kamelan mokhalef", "kamelan movafegh"),
    "quality_criteria": ("X20_", 16, "hargez", "hamishe"),
}
NOT_SHIPPED = ["X6", "X7", "X8", "X9", "X13", "X14", "X15", "X16", "X17"] + [f"X19_{i}" for i in range(1, 9)] + \
              ["konjkavi100", "negaresh100", "mavane100", "Educate", "Income"]


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert df.shape == (392, 70), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    vl = meta.variable_value_labels
    assert vl["Sex"] == {1.0: "girl", 2.0: "boy"}
    assert vl["X19_1"][1.0] == "kam" and vl["X19_1"][2.0] == "besyar kam"  # the disordered battery
    df["id"] = range(1, len(df) + 1)
    df["cov_sex"] = df["Sex"].map({1.0: "girl", 2.0: "boy"})
    df["cov_age"] = df["Age"]
    covs = ["cov_sex", "cov_age"]
    used = {"Sex", "Age"} | set(NOT_SHIPPED)
    total = 0
    for block, (pfx, k, lo, hi) in BLOCKS.items():
        items = [f"{pfx}{i}" for i in range(1, k + 1)]
        for c in items:
            assert vl[c][1.0] == lo and vl[c][5.0] == hi, (c, vl[c])
        used |= set(items)
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {1, 2, 3, 4, 5}
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {block} {c.name}: {c.detail[:160]}")
        name = f"esmaeilzadeh_2018_{block}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")
    assert used | {"id"} | set(covs) == set(df.columns), set(df.columns) - used
    print(f"total responses {total}; not shipped: {NOT_SHIPPED}")


if __name__ == "__main__":
    convert()
