#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/IEHI3U
# DOI: 10.1371/journal.pone.0223098
# Paper: Lusk JL (2019). Consumer beliefs about healthy foods and diets. PLoS
#   ONE 14(10): e0223098.
# Data: Harvard Dataverse doi:10.7910/DVN/IEHI3U, file data_to_share_2.csv
#   (datafile 3792855, format=original), 1,290 U.S. respondents, with "CRA
#   Survey Codebook.pdf" (variable definitions and response codes) and the
#   topline results. The survey was run for the Corn Refiners Association.
# License: CC0 1.0 on the DEPOSIT (Dataverse dataset licence); the article is
#   CC BY 4.0.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 2.
#
# FIVE output tables, item codes the deposit's own, codes per the codebook:
#   lusk_2019_natural_processing  Q9_*, 12 items: "If a food was produced with
#     the following processes or practices, would you consider the food to be
#     natural or not natural?" 1 Natural, 2 Neither natural or not, 3 Not
#     natural (fermentation, added enzymes, chopped, ...)
#   lusk_2019_natural_farming     Q13_*, 9 items, the same 1-3 scale for
#     farming practices ("seeds created with genetic engineering or GMOs",
#     "hybrid seeds", ..., "organically grown crops")
#   lusk_2019_natural_beliefs     Q14_1-8, 1-5 agreement ("Natural food is
#     healthier", "Natural food is better for the environment", ...). Q14_9
#     ("Click somewhat disagree if you're paying attention") is the attention
#     check and is dropped; every respondent in the deposit answered it 2.
#   lusk_2019_healthy_foods       Q18_*, 15 items: "Do you consider each of
#     the following foods to be healthy or unhealthy for you?" 1 Healthy,
#     2 Neither healthy nor unhealthy, 3 Unhealthy (fresh fruit, frozen fruit,
#     canned fruit, ...)
#   lusk_2019_healthy_beliefs     Q28_1-8, agreement ("Healthy food is more
#     natural", ...). Q28_9 ("Individual needs determine whether various foods
#     are healthy for an individual") is dropped: all 1,290 respondents hold
#     the same code (27), so it carries no information and was most likely a
#     second screen behind the codebook's "respondents who met exclusionary
#     criteria". The deposit codes this scale 24 (Strongly disagree)
#     to 28 (Strongly agree), Qualtrics' own numbering; resp = code - 23, so
#     1-5 like Q14, and the original code is not otherwise informative.
# Covariates: gender, age group, education group, region, race, Hispanic,
#   vegetarian, political ideology (1-5, as given), from the deposit's own
#   coded columns.
# Dropped: the survey weight (wts); ResponseId (a Qualtrics response id) and
#   Duration; state (finer geography than the region kept); the click-map
#   coordinates (Q11/Q12/Q34-Q62 *_x/_y), slider and ranking items, the
#   check-up-to-3 lists and their dummies, free text, and every derived
#   dummy (age*, inc*, edu dummies, party dummies, qq*/v*/vv*).
# `id` is the deposit's ID ("an internal code used to track participants").
#
# Item text: NOT SHIPPED. The wording and response labels are in the
#   deposit's codebook PDF (study-authored, CC0); not built in this batch.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://dataverse.harvard.edu/api/access/datafile/3792855?format=original"
RAW = os.environ.get("LUSK_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BLOCKS = {"natural_processing": ("Q9_", 12, range(1, 4), 0), "natural_farming": ("Q13_", 9, range(1, 4), 0),
          "natural_beliefs": ("Q14_", 7, range(1, 6), 0), "healthy_foods": ("Q18_", 15, range(1, 4), 0),
          "healthy_beliefs": ("Q28_", 8, range(1, 6), 23)}
SCREENS = ["Q14_9", "Q28_9"]
AGE = {"age18_24": "18-24", "age25_34": "25-34", "age35_44": "35-44", "age45_54": "45-54", "age55_64": "55-64",
       "age65_74": "65-74", "age75p": "75+"}
REGION = {"northeast": "Northeast", "midwest": "Midwest", "south": "South", "west": "West"}


def from_dummies(df, mapping):
    sub = df[list(mapping)]
    assert (sub.sum(axis=1) == 1).all(), list(mapping)
    return sub.idxmax(axis=1).map(mapping)


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_csv(src)


def convert():
    df = load()
    assert df.shape == (1290, 439), df.shape
    assert df["ID"].nunique() == len(df)
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined")
    assert len(df.columns) > 0
    for c in SCREENS:  # constant in the deposit: the sample was screened on them
        assert df[c].nunique() == 1, c
    df = df.copy()
    df["id"] = df["ID"].astype(int)
    df["cov_female"] = df["female"]
    df["cov_age_group"] = from_dummies(df, AGE)
    df["cov_region"] = from_dummies(df, REGION)
    df["cov_education"] = df["edu"]
    df["cov_white"], df["cov_black"], df["cov_hispanic"] = df["white"], df["black"], df["hispanic"]
    df["cov_vegetarian"] = df["vegetarian"]
    df["cov_conservative"] = df["conservative"]
    covs = ["cov_female", "cov_age_group", "cov_region", "cov_education", "cov_white", "cov_black",
            "cov_hispanic", "cov_vegetarian", "cov_conservative"]
    total = 0
    for name, (prefix, n, perm, shift) in BLOCKS.items():
        items = [c for c in df.columns if c.startswith(prefix) and c[len(prefix):].isdigit() and c not in SCREENS]
        assert len(items) == n, (name, items)
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"])
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int) - shift
        assert set(long["resp"]) <= set(perm), (name, set(long["resp"]))
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(perm) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:150]}")
        out = f"lusk_2019_{name}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        total += len(long)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    print(f"total responses {total}")


if __name__ == "__main__":
    convert()
