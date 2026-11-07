#!/usr/bin/env python3
# Source: https://osf.io/cjzt6/
# DOI: 10.1371/journal.pone.0332297
# Paper: Banerjee R, Wright M, Bianco F (2025). Emotional adjustment and peer
#   relationships: The role of behavioural reputation and classroom social
#   climate. PLoS One 20(9): e0332297.
# Data: OSF node cjzt6 (public), sepq.csv with "sepq codebook.csv" (every
#   column defined, item wording and response anchors included) and
#   OSF readme.txt. 1,439 pupils aged 7-13 in 60 classrooms of 26 schools in
#   England and Wales.
# License: CC BY 4.0 on the DEPOSIT (OSF node licence "CC-By Attribution 4.0
#   International"); the article is CC BY 4.0.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 3.
#
# ONE output table: banerjee_2025_sepq -- the pupils' self-report
#   questionnaire as administered, q1-q43, 0-3. Per the codebook, q1-q37 are
#   rated "0 = almost never to 3 = nearly all the time" and q38-q43 "0 = not
#   at all true to 3 = very true". It covers positive and negative peer
#   experiences, anger, anxiety, depressive symptoms and self-worth (the
#   deposit's pospeer/negpeer/ang/anx/dep/self means); q13, q19, q29 and q37
#   ("I like reading books", "I have fun in PE lessons", "I like school
#   assemblies", "I like playing computer games with my friends") belong to
#   none of those and ship as administered.
# `id` = "<classroom>_<Code>" (Code is the pupil's number within the
#   classroom); `cluster_id` is the classroom.
# Covariates: gender (codebook: 1 male, 2 female), school, school year group
#   (".5" marks a combined-year class).
# Dropped: the peer-nomination counts at both time points (ML, LL, COOP,
#   DISRUP, SHY, FIGHT, LEAD and their .2 copies -- counts of nominations
#   RECEIVED, not the pupil's responses), their within-class z-scores, the six
#   subscale means, the social-preference scores and the climate groupings.
#
# Item text: NOT SHIPPED. The full wording of all 43 items and both anchor
#   sets are in the deposit's codebook; the instrument was not identified
#   against published scales in this batch.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://osf.io/download/ea2uq/"
RAW = os.environ.get("BANERJEE_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ITEMS = [f"q{i}" for i in range(1, 44)]


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=120)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_csv(src)


def convert():
    df = load()
    assert df.shape == (1439, 86), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and not txt
    assert not df.duplicated(["classroom", "Code"]).any()
    df = df.copy()
    df["id"] = df["classroom"].astype(int).astype(str) + "_" + df["Code"].astype(int).astype(str)
    df["cluster_id"] = df["classroom"].astype(int)
    df["cov_gender"] = df["Gender"].map({1: "male", 2: "female"})
    df["cov_school"] = df["schoolcode"].astype(int)
    df["cov_year_group"] = df["year"]
    covs = ["cov_gender", "cov_school", "cov_year_group"]
    long = df[["id", "cluster_id"] + covs + ITEMS].melt(id_vars=["id", "cluster_id"] + covs, var_name="item",
                                                       value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= {0, 1, 2, 3}
    long = long[["id", "item", "resp", "cluster_id"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1, 2, 3] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:150]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "banerjee_2025_sepq.csv"), index=False)
    print(f"banerjee_2025_sepq: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
