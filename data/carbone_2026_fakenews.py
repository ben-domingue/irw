#!/usr/bin/env python3
# Source: https://osf.io/sgz2f/
# DOI: 10.1371/journal.pone.0348391
# Paper: Carbone D, Marcatto F, Ferrante D (2026). Thinking together: How group
#   argumentation boosts fake news recognition. PLoS One 21(5): e0348391.
# Data: OSF node sgz2f ("Thinking Together: How Group Argumentation Boosts Fake
#   News Recognition"), data/primary data.xlsx, sheet "Foglio1", 128 college
#   students in Italy. The article's Data Availability statement gives a
#   ?view_only= link, but the node itself is public (api.osf.io/v2/nodes/sgz2f:
#   public = true).
# License: CC0 1.0 on the DEPOSIT (node licence 563c1cf88c5e4a3877f9e96c =
#   "CC0 1.0 Universal" via api.osf.io/v2/licenses/); the article is CC BY 4.0.
#
# Worked from the cleaned leads list of 2026-11-07 (rank 18; source
# leads/plos_leads_2026-10-30.csv), leads batch 1.
#
# Design: each participant read four news items -- two fake ("Formaldehyde",
# "Thyroid") and two real ("Nutella", "Masks") -- and rated each one alone
# (phase 1). In phase 2 they reread each item and argued its truth either in
# writing on their own or in discussion with their group of three; which items
# got which condition was assigned per participant ("Form Arg", "ThyrArg",
# "NutArg", "MaskArg"), then they rated the item again.
#
# TWO output tables, each with the four news items as `item` (formaldehyde,
# thyroid, nutella, masks) and the two phases as `wave` (1, 2). Both questions
# are on the paper's 6-point scale, 1 "most likely no / most likely false" to
# 6 "most likely yes / most likely true".
#   carbone_2026_fakenews_truth  "Do you think this news is true or false?"
#   carbone_2026_fakenews_share  "If you happened to see this news on social
#                                 media, would you share it?" (Thyroid in
#                                 phase 2 holds 1-5 only as deposited)
# `treat` is the item's phase-2 condition: 1 = group argumentation, 0 =
#   individual written argumentation. It is a within-person assignment (it
#   varies by item), carried on both waves of the item.
# `cluster_id` is the deposit's Group number (1..45), the discussion group.
# Covariates: gender, age, group type ("3 PP" = a full group of three, "2 PP"
#   = a group of two). The paper's analysis sample is 111: it excluded the
#   groups left with two members by a no-show (the 14 "2 PP" rows here) and one
#   group with a bad connection (not identified in the deposit). All 128 are
#   shipped; cov_group_type marks the first exclusion.
# Dropped: Order (the Latin-square presentation order, 1-4; one code per
#   person, not per item, and its key is not given); the three phase-1-only
#   control questions -- interest to friends, emotional impact, intention to
#   look for more information -- each one question asked about four news items,
#   not scales; OtherPartKnowledge, FearOtherJudg and GroupInterPleas (single
#   post-session questions).
# `id` is the row index. The deposit's Code column is a participant-made
#   pseudonymous code and is not carried.
#
# Item text: NOT SHIPPED. The two question wordings and the scale anchors are
#   in the article's Procedure section; the news texts themselves are in the
#   article's S1 File. Not built in this batch.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://osf.io/download/qz4nv/"
RAW = os.environ.get("CARBONE_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
NEWS = {"Form": ("formaldehyde", "Form Arg"), "Thyr": ("thyroid", "ThyrArg"),
        "Nut": ("nutella", "NutArg"), "Mask": ("masks", "MaskArg")}
QUESTIONS = {"truth": "Truth", "share": "IntToShare"}
DROPPED = ["Code", "Order", "OtherPartKnowledge", "FearOtherJudg", "GroupInterPleas"] + [
    f"{q} {n}" for q in ("FriendsInterest", "EmotionalImp", "InfoSearch") for n in NEWS]


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=120)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src, sheet_name="Foglio1")


def convert():
    df = load()
    df.columns = [c.strip() for c in df.columns]
    assert df.shape == (128, 41), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and set(txt) == {"Code", "Gender", "Group type", "Form Arg", "ThyrArg", "NutArg",
                                                 "MaskArg"}
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cluster_id"] = df["Group number"].astype(int)
    df["cov_gender"] = df["Gender"].str.strip()
    df["cov_age"] = df["Age"]
    df["cov_group_type"] = df["Group type"].str.strip().map({"3 PP": "three", "2 PP": "two"})
    assert df["cov_group_type"].notna().all()
    covs = ["cov_gender", "cov_age", "cov_group_type"]
    used = {"Gender", "Age", "Group number", "Group type"} | set(DROPPED)
    for key, q in QUESTIONS.items():
        rows = []
        for short, (name, argcol) in NEWS.items():
            cond = df[argcol].str.strip().map({"group": 1, "individual": 0})
            assert cond.notna().all(), argcol
            used.add(argcol)
            for wave, suffix in [(1, " 1"), (2, " 2")]:
                col = f"{q} {short}{suffix}"
                used.add(col)
                p = df[["id", "cluster_id"] + covs].copy()
                p["item"], p["resp"], p["wave"], p["treat"] = name, df[col], wave, cond
                rows.append(p)
        long = pd.concat(rows, ignore_index=True)
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(range(1, 7))
        long = long[["id", "item", "resp", "wave", "treat", "cluster_id"] + covs]
        assert not long.duplicated(["id", "item", "wave"]).any()
        checks = run_qc(long, permitted_values={n: list(range(1, 7)) for n, _ in NEWS.values()})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {key} {c.name}: {c.detail[:150]}")
        out = f"carbone_2026_fakenews_{key}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert used == set(df.columns) - {"id", "cluster_id"} - set(covs), set(df.columns) - used
    print(f"dropped: {DROPPED}")


if __name__ == "__main__":
    convert()
