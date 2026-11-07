#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0281002
# DOI: 10.1371/journal.pone.0281002
# Paper: Bullock J, Lane JE, Mikloušić I, Shults FL (2023). Modeling
#   nationalism, religiosity, and threat perception: During the COVID-19
#   pandemic. PLoS ONE 18(4): e0281002.
# Data: PLOS Supporting Information S1 File (journal.pone.0281002.s001), one
#   sheet, 2,018 respondents (an MTurk sample and a general sample) in 34
#   countries. Column headers are the full question text ("<item>:<prompt>").
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 2.
#
# Geography: the depositors blanked the headers of several columns
#   (REMOVED_ANON*) but left values in three of them -- a city (1,001 distinct
#   values, nested within country for 98% of cities), a two-character region
#   code, and a postal code. Per the 2026-10-20 ruling (geographic codes: drop
#   the column, ship the rest) all three are dropped, in no form. Checked
#   without printing values: no "@" in any of them, and the city column's
#   nesting in country is what identifies it as a place rather than a name.
#
# TEN output tables. Item codes are derived from the question order within
# each block (prefix_k), because the headers are full sentences; the k-th code
# is the k-th column of the block in the deposit, and each block's first header
# is asserted below so a reordered file fails rather than mislabels.
#   bullock_2023_national_identification  4 items, 1-7, prompt "about your
#     feelings toward your nation" ("I identify with my nation" ... "Being in my
#     nation is an important part of how I see myself")
#   bullock_2023_national_fusion          7 items, 1-7, prompt "about your
#     nation" ("I am one with my nation" ... "I make my nation strong"): the
#     identity-fusion items. The two are separate tables because the deposit
#     asks them under two different prompts.
#   bullock_2023_gender_roles             4 items, 1-5 agree/disagree ("When
#     jobs are scarce, men should have more right to a job than women" ...)
#   bullock_2023_group_feelings           6 items, 1-6 ("How do you feel
#     toward the following groups": Muslims, Christians, Jews, Atheists,
#     Immigrants, People of other races than my own)
#   bullock_2023_national_membership      8 items, 1-7 ("To be truly part of my
#     nation one must be born in the nation" ...)
#   bullock_2023_supernatural_belief      12 items, 1-7 ("There exists an
#     all-powerful, all-knowing loving God" ... "The universe has the ability
#     to affect the events in our lives")
#   bullock_2023_religious_identification 4 items and
#   bullock_2023_religious_fusion         7 items, 1-7: the same two sets with
#     "my religious [or nonreligious] group" in place of "my nation"
#   bullock_2023_bfi10                    BFI-10, 10 items, 1-5 ("Is
#     reserved" ... "Has an active imagination")
#   bullock_2023_threat                   14 items, 1-5 ("I feel like we are in
#     a culture war" ... "Our way of life is threatened because of the number
#     of ...")
# All stored as deposited; no reverse-keyed item is recoded.
# Covariates: sample (MTurk / General), age, gender (M/F/O), country of
#   residence, religious identity (the deposit's category).
# Dropped: the three geographic columns above and the five empty REMOVED_ANON
#   columns; Country (duplicates country of residence) and nationality;
#   education (codes 1-4, no labels); the "other religion" and news-source free
#   text; COVID-19 infection status; vote choice and the EU-referendum item;
#   the "would not like as neighbours" checklist (a marked box holds its option
#   number and an unmarked box is blank, so "not chosen" cannot be told from
#   "not answered"); left-right self-placement (2 items), religious attendance,
#   social-media time and news frequency (single items).
# `id` is the deposit's Index (unique).
#
# Item text: NOT SHIPPED. The stems are the column headers (in hand, quoted
#   above in part), but the blocks include published instruments (BFI-10,
#   identity-fusion and supernatural-belief scales) whose terms were not
#   checked in this batch.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0281002.s001"
RAW = os.environ.get("BULLOCK_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
# (table, prefix, first column index, n items, first-header start, permitted)
BLOCKS = [
    ("national_identification", "natid", 18, 4, "I identify with my nation", range(1, 8)),
    ("national_fusion", "natfus", 22, 7, "I am one with my nation", range(1, 8)),
    ("gender_roles", "gender_roles", 38, 4, "When jobs are scarce, men", range(1, 6)),
    ("group_feelings", "feel", 42, 6, "Muslims", range(1, 7)),
    ("national_membership", "natmem", 52, 8, "To be truly part of my nation one must be born", range(1, 8)),
    ("supernatural_belief", "super", 60, 12, "There exists an all-powerful", range(1, 8)),
    ("religious_identification", "relid", 73, 4, "I identify with my religious", range(1, 8)),
    ("religious_fusion", "relfus", 77, 7, "I am one with my religious", range(1, 8)),
    ("bfi10", "bfi", 84, 10, "Is reserved", range(1, 6)),
    ("threat", "threat", 94, 14, "I feel like we are in a culture war", range(1, 6)),
]


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=120)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src, sheet_name=0)


def convert():
    df = load()
    assert df.shape == (2018, 112), df.shape
    cols = list(df.columns)
    txt = [c for c in cols if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(cols)} examined")
    assert len(cols) > 0
    geo = ["REMOVED_ANON.3", "REMOVED_ANON.4", "REMOVED_ANON.5"]
    for g in geo:
        assert not df[g].astype(str).str.contains("@").any(), g
    assert df["Index"].nunique() == len(df)
    df["id"] = df["Index"].astype(int)
    df["cov_sample"] = df["Source"].str.strip()
    df["cov_age"] = df[cols[9]]
    df["cov_gender"] = df[cols[10]].astype(str).str.strip().replace({"nan": None})
    df["cov_country"] = df[cols[12]].astype(str).str.strip().replace({"nan": None})
    df["cov_religion"] = df[cols[15]].astype(str).str.strip().replace({"nan": None})
    assert cols[9].startswith("How old") and cols[10].startswith("What is your gender")
    assert cols[12].startswith("What is your country of residence") and cols[15].startswith("What term would")
    covs = ["cov_sample", "cov_age", "cov_gender", "cov_country", "cov_religion"]
    total = 0
    for name, prefix, start, n, head, perm in BLOCKS:
        block = cols[start:start + n]
        assert block[0].startswith(head), (name, block[0][:60])
        prompts = {c.split(":", 1)[1] if ":" in c else "" for c in block}
        assert len(prompts) == 1, (name, prompts)
        codes = {c: f"{prefix}_{k}" for k, c in enumerate(block, 1)}
        sub = df[["id"] + covs + block].rename(columns=codes)
        long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"])
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(perm), (name, set(long["resp"]))
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        items = list(codes.values())
        checks = run_qc(long, permitted_values={c: list(perm) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:150]}")
        out = f"bullock_2023_{name}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        total += len(long)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    print(f"total responses {total}")


if __name__ == "__main__":
    convert()
