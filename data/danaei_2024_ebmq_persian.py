#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0301831
# DOI: 10.1371/journal.pone.0301831
# Paper: Danaei, Z., Madadizadeh, F., Sheikhshoaei, F., & Dehdarirad, H.
#   (2024). Translation and cross-cultural adaptation of Persian version of
#   Evidence Based Medicine Questionnaire (EBMQ) in postgraduate medical
#   students in Iran. PLOS ONE 19(4): e0301831.
# Data: figshare 10.6084/m9.figshare.25238650, "data for sharing.xlsx",
#   400 rows x 41 columns.
#
# LICENCE verified on the DEPOSIT, not the article: the data is hosted
# off-site on figshare, so the article's licence does not reach it.
# api.figshare.com/v2/articles/25238650 reports CC BY 4.0.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30 (BATCH_LOG.md).
#
# FOUR output tables, 40 items, 16,000 responses, zero missing cells. 400
# postgraduate medical students at three Tehran universities, October-December
# 2022, proportionate stratified sample.
#
# THE DEPOSIT AND THE PAPER DISAGREE ABOUT HOW THE FIRST 22 ITEMS SPLIT, and
# the deposit wins because its own data settles it. The article describes
# "knowledge of information sources (8 items)" on a 4-point scale and
# "knowledge of EBM terms (14 items)" on a 5-point scale -- 22 in total. The
# deposit has 22 items in its C block, but they split 6 and 16, not 8 and 14:
#   * C1-C6 are named RESOURCES (the BMJ group's Evidence Based Medicine,
#     DARE, CEBM, the ACP Journal Club, BMJ Clinical Evidence, the Centre of
#     Reviews & Dissemination) and their observed range is 1-4.
#   * C7-C22 are statistical and methodological TERMS (systematic review,
#     meta-analysis, case-control study, RCT, relative and absolute risk,
#     odds ratio, p-value, level of evidence, number needed to treat,
#     confidence interval, heterogeneity, publication bias, sensitivity and
#     specificity, positive predictive value, clinical effectiveness) and
#     their observed range is 1-5.
# Content and scale agree with each other and disagree with the article's
# count, so the two blocks ship as 6 and 16 with the discrepancy recorded.
# The totals match either way: 22 + 8 + 10 = 40, the paper's own final count.
#
# THE TWO AWARENESS SCALES ARE DIFFERENT SCALES, which is why they are two
# tables rather than one 22-item block. Per the article, the resource scale
# runs 1 "unaware" to 4 "read and used in clinical decision making", and the
# term scale runs 1 "never heard of this term before" to 5 "understand it
# well enough to explain it to others". Merging them would put a 4-point and
# a 5-point scale on one `resp`.
#
# SPARSE LEVEL USE IS NOT A DIFFERENT SCALE. Several term items never attract
# a 2 (C19-C22 are observed only at 1, 4 and 5), which is what a familiarity
# item looks like in a sample that has mostly either not heard of a term or
# knows it well. Permitted values stay 1-5 for all sixteen.
#
# `id` is the deposit's `Respondent ID`, verified unique over all 400 rows.
# There are no covariate columns in the deposit at all.
#
# Item text: NOT SHIPPED, and the reason is that the headers are LABELS, not
# items. "C7: Aware of Systematic review" names what an item is about; it is
# not the question as administered, which was in Persian and is published
# nowhere. Shipping the labels as item_text would put a paraphrase in a field
# readers take for transcription. The instrument is also Hisham et al.'s
# (2018) EBMQ -- the authors translated it WITH PERMISSION FROM THE COPYRIGHT
# HOLDER, which is a grant to them and not onward to IRW. Registered as a
# hold on both counts.
#
# PII: screened over all 41 columns. Every one is numeric apart from the
# headers themselves.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("DANAEI_RAW", "data for sharing.xlsx")

N_ROWS = 400
TABLES = [
    ("danaei_2024_ebmq_sources", "C", 1, 6, 1, 4,
     "Awareness of six evidence-based-medicine information sources "
     "(1 unaware, 4 read and used in clinical decision making)"),
    ("danaei_2024_ebmq_terms", "C", 7, 22, 1, 5,
     "Familiarity with sixteen EBM and statistical terms (1 never heard of "
     "it, 5 understand it well enough to explain it to others)"),
    ("danaei_2024_ebmq_practice", "D", 1, 8, 1, 5,
     "Practice of evidence-based medicine, 5-point agreement"),
    ("danaei_2024_ebmq_barriers", "E", 1, 10, 1, 5,
     "Barriers to practising evidence-based medicine, 5-point agreement"),
]
HEADER = re.compile(r"^([CDE])(\d+):")


def convert():
    df = pd.read_excel(RAW)
    assert len(df) == N_ROWS, len(df)
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    assert not strings, f"unexpected string column(s): {strings}"
    print(f"PII screen: 0 string columns of {len(df.columns)}")

    codes = {}
    for c in df.columns:
        m = HEADER.match(str(c))
        if m:
            codes[(m.group(1), int(m.group(2)))] = c
    assert len(codes) == 40, len(codes)
    blocks = {}
    for (letter, n) in codes:
        blocks[letter] = blocks.get(letter, 0) + 1
    assert blocks == {"C": 22, "D": 8, "E": 10}, blocks
    print(f"40 items in three lettered blocks: {blocks}, matching the "
          f"article's final count of 40")

    # the split of C is the deposit's, not the article's -- assert the scales
    src = [codes[("C", i)] for i in range(1, 7)]
    trm = [codes[("C", i)] for i in range(7, 23)]
    assert int(df[src].max().max()) == 4, (
        "the first six C items no longer top out at 4; the 6/16 split rests "
        "on their 4-point scale, so re-derive before shipping")
    assert int(df[trm].max().max()) == 5, "the C7+ items no longer reach 5"
    print("the C block splits 6 (resources, observed 1-4) and 16 (terms, "
          "observed 1-5), against the article's stated 8 and 14; content and "
          "observed scale agree with each other, so the deposit wins")

    accounted = {"Respondent ID"} | set(codes.values())
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted source columns: {left_out}"
    assert df["Respondent ID"].nunique() == len(df), "the id is not unique"
    df = df.rename(columns={"Respondent ID": "id"})

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, letter, first, last, lo, hi, label in TABLES:
        cols = [codes[(letter, i)] for i in range(first, last + 1)]
        ren = {c: f"{letter}{i}" for i, c in zip(range(first, last + 1), cols)}
        assert int(df[cols].isna().sum().sum()) == 0, (name, "missing cells")
        vals = pd.to_numeric(df[cols].stack(), errors="coerce")
        assert vals.notna().all() and vals.between(lo, hi).all(), \
            (name, sorted(vals.unique()))

        long = df.melt(id_vars=["id"], value_vars=cols, var_name="item",
                       value_name="resp")
        long["item"] = long["item"].map(ren)
        long["resp"] = long["resp"].astype(int)
        assert long["id"].nunique() == N_ROWS
        assert long["item"].nunique() == len(cols)
        assert not long.duplicated(["id", "item"]).any()
        assert len(name) <= 40, name
        long = long[["id", "item", "resp"]]

        checks = run_qc(long, permitted_values={i: list(range(lo, hi + 1))
                                                for i in long["item"].unique()})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:135]}")

        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}  [{label[:52]}]")

    assert total == 40 * N_ROWS, total
    print(f"4 tables, {total} responses (40 items x {N_ROWS} postgraduate "
          f"medical students)")


if __name__ == "__main__":
    convert()
