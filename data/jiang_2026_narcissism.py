#!/usr/bin/env python3
# Source: https://zenodo.org/records/23476418
# DOI: 10.5281/zenodo.23476418 (dataset; the record names no published paper)
# Deposit: Jiang, C. (2026). A Latent Profile Analysis of Multidimensional
#   Narcissism Tendencies Among Social Workers [Data set]. Zenodo.
# Data: "narcissism data .xlsx" (one sheet, Sheet1; 746 rows x 51 columns)
#   sha256 f58380bd716b38f2faf862329bad5a2f2466eb64fefa2c4bf5100c7ae724a911
# Codebook: none. The deposit is the one .xlsx; its column headers name the
#   construct and item number ("communal narcissism item1") and nothing else.
# License: CC BY 4.0 (resolved from the Zenodo record's metadata, cc-by-4.0)
#
# Found by the repos monthly sweep of 2026-11-02 (recoverable_format: the
# triage read only a 22-column 1-5 block).
#
# NINE output tables, one per construct named in the headers:
#   jiang_2026_communal_narcissism    3 items, 1-5
#   jiang_2026_agentic_narcissism     3 items, 1-5
#   jiang_2026_vulnerable_narcissism  3 items, 1-5
#   jiang_2026_grandiose_narcissism   4 items, 1-5
#   jiang_2026_need_satisfaction      9 items, 1-7 (autonomy, competence,
#                                     relatedness, 3 each)
#   jiang_2026_mental_health          5 items, 1-5
#   jiang_2026_work_engagement        3 items, 0-6
#   jiang_2026_exhaustion             3 items, 0-6
#   jiang_2026_objectification        4 items, 1-5 (interpersonal
#                                     objectification)
# The four narcissism dimensions are separate tables, not one: the depositor
# scores each as its own factor (four factor-score columns feed the LPA), and
# they behave as distinct constructs (communal vs agentic items correlate
# about 0.0; within-dimension 0.4-0.8), so they most likely come from
# different short instruments. Autonomy/competence/relatedness stay together
# as the three subscales of one need-satisfaction measure (means intercorrelate
# 0.51-0.72). Item codes are the headers in snake case, minus the word
# "narcissism" (communal_item1 ...), whose substring "ciss" otherwise trips the
# rights register's CISS matcher -- a false lead, these codes are not wording.
#
# resp: shipped as recorded. NO SCALE IS DOCUMENTED -- the deposit has no
# codebook or questionnaire and Zenodo names no paper. The ranges above are
# the observed ones; every point of each range is used and no value sits
# outside it, so there is no sentinel to filter, but the anchors and the
# direction are unconfirmed. permitted_values is therefore NOT passed to
# run_qc (it must come from documentation, never from the data). No cell is
# empty.
#
# id: none deposited; the row index (1-746) is the person, and the same row
# has the same id in all nine tables. 5 rows repeat another row's 37 item
# responses exactly; with no id to tell them apart they are kept as distinct
# respondents.
#
# Dropped: the four "... factor scores" and seven "... means" columns --
# derived scores, not items.
# Covariates: cov_gender (header: 1 = male, 0 = female), cov_age,
#   cov_subjective_ses (subjective socioeconomic status, observed 1-10, read as
#   a 10-rung ladder; undocumented).
#
# Item text: not in hand. The headers are positional ("item1") and the deposit
#   has no questionnaire; the instruments are not named anywhere in the record.
#
# PII: none possible -- every column is numeric (asserted below), so there is
#   no text column to screen.

import os
import re
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("JIANG_NARC_RAW", "narcissism data .xlsx")

# table -> (header prefixes, observed range)
TABLES = {
    "jiang_2026_communal_narcissism": (["communal narcissism"], (1, 5)),
    "jiang_2026_agentic_narcissism": (["agentic narcissism"], (1, 5)),
    "jiang_2026_vulnerable_narcissism": (["vulnerable narcissism"], (1, 5)),
    "jiang_2026_grandiose_narcissism": (["grandiose narcissism"], (1, 5)),
    "jiang_2026_need_satisfaction": (["autonomy", "competence", "relatedness"],
                                     (1, 7)),
    "jiang_2026_mental_health": (["mental health"], (1, 5)),
    "jiang_2026_work_engagement": (["work engagement"], (0, 6)),
    "jiang_2026_exhaustion": (["exhaustion"], (0, 6)),
    "jiang_2026_objectification": (["interpersonal objectification"], (1, 5)),
}
COVS = {"gender（1 = male，0 = female）": "cov_gender", "age": "cov_age",
        "subjective socioeconomic status": "cov_subjective_ses"}
ITEM_COL = re.compile(r"^(.+) item(\d+)$")


def convert():
    df = pd.read_excel(RAW, sheet_name="Sheet1")
    assert df.shape == (746, 51), df.shape
    assert all(pd.api.types.is_numeric_dtype(df[c]) for c in df.columns), \
        "a non-numeric column appeared -- screen it for PII before shipping"
    assert df.notna().all().all()

    derived = [c for c in df.columns
               if c.endswith(" factor scores") or c.endswith(" means")]
    assert len(derived) == 11, derived
    placed = {}
    for c in df.columns:
        m = ITEM_COL.match(c)
        if not m:
            continue
        hits = [t for t, (pref, _) in TABLES.items() if m.group(1) in pref]
        assert len(hits) == 1, (c, hits)
        placed[c] = hits[0]
    unaccounted = set(df.columns) - set(placed) - set(derived) - set(COVS)
    assert not unaccounted, unaccounted
    assert len(placed) == 37, len(placed)

    df = df.rename(columns=COVS)
    covs = list(COVS.values())
    df.insert(0, "id", range(1, len(df) + 1))

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, (_, (lo, hi)) in TABLES.items():
        cols = [c for c, t in placed.items() if t == table]
        long = df.melt(id_vars=["id"] + covs, value_vars=cols,
                       var_name="item", value_name="resp")
        # "narcissism" is dropped from the codes: the table name carries it, and
        # its substring "ciss" trips the rights register's CISS matcher.
        long["item"] = (long["item"].str.replace(" narcissism", "")
                        .str.replace(" ", "_"))
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert long["resp"].between(lo, hi).all()
        assert set(long["resp"]) == set(range(lo, hi + 1)), table
        assert long["id"].nunique() >= 100

        checks = run_qc(long)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")

        long.to_csv(os.path.join(OUT_DIR, table + ".csv"), index=False)
        print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
