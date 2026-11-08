#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0239936
# DOI: 10.1371/journal.pone.0239936
# Paper: Zeilinger EL, Stiehl KAM, Bagnall H, Scior K (2020). Intellectual
#   disability literacy and its connection to stigma: A multinational
#   comparison study in three European countries. PLoS ONE 15(10): e0239936.
# Data: Figshare 10.6084/m9.figshare.12972884,
#   Datafile_ID_Literacy_Stigma_Austria_Germany_UK.sav (file 24715076), 1,046
#   adults from the general population of Austria, Germany and the UK who read
#   a vignette about "James", a young man with a mild intellectual
#   disability, presented with or without the diagnostic label.
# License: CC BY 4.0 (the Figshare item's licence field).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 5.
#
# FOUR output tables, all 1 "disagree strongly" - 7 "agree strongly" (4
#   "unsure"), item codes the deposit's (lower-cased, dot kept):
#   zeilinger_2020_idls_causes      James3.1-3.22, Intellectual Disability
#     Literacy Scale causal beliefs (overly spoilt, virus, ..., isolation
#     from extended family).
#   zeilinger_2020_idls_interventions James4.1-4.22, IDLS beliefs about
#     helpful interventions (take more responsibility, ..., be more
#     religious).
#   zeilinger_2020_social_distance  James5.1-5.5, willingness to live next
#     door to / spend an evening / work closely / make friends / have
#     marry into the family someone like James. Shipped as answered; the
#     deposit's "reversed" copies (8 - x) are dropped.
#     (The paper describes the IDLS social distance part as 4 items; the
#     deposit holds these 5, and all 5 are shipped.)
#   zeilinger_2020_emotional_reactions James2.2-2.9, emotional reactions to
#     James (I feel for him, angry, uncomfortable, insecure, irritated, sorry
#     for him, annoyed, the need to help him).
# Four isolated 0 cells and two 888 cells in the James2 block (one each per
#   item, outside the labelled 1-7) are dropped as entry slips/sentinels.
# Covariates: country of residence, vignette condition (labelled /
#   unlabelled), age, gender, education (three levels), any contact with
#   people with ID.
# Dropped: the participant code (mixed panel codes such as "PW658" and
#   numbers; replaced by the row index), the free-text answer to "What would
#   you say is going on with James?" and its coding, the derived subscale
#   scores, religion.
# `id` is the row index.
#
# Item text: NOT SHIPPED. The variable labels are short paraphrases; the
#   SI S1 File holds the labelled vignettes. The IDLS is a published scale
#   (Scior & Furnham).

import io
import os
import re
import sys
import tempfile

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://ndownloader.figshare.com/files/24715076"
RAW = os.environ.get("ZEILINGER_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=300)
        r.raise_for_status()
        f = tempfile.NamedTemporaryFile(suffix=".sav", delete=False)
        f.write(r.content)
        f.close()
        src = f.name
    df, meta = pyreadstat.read_sav(src)
    return df, meta


def convert():
    df, meta = load()
    assert df.shape == (1046, 90), df.shape
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    lab = meta.variable_value_labels
    df["cov_country"] = df["residence"].map(lab["residence"])
    df["cov_condition"] = df["Study_questionnaire"].map(lab["Study_questionnaire"])
    df["cov_age"] = df["age"]
    df["cov_gender"] = df["gender"].map(lab["gender"])
    df["cov_education"] = df["Educ3levels"].map(lab["Educ3levels"])
    df["cov_id_contact"] = df["IDContact"].map(lab["IDContact"])
    covs = [c for c in df.columns if c.startswith("cov_")]
    blocks = {
        "idls_causes": [f"James3.{i}" for i in range(1, 23)],
        "idls_interventions": [f"James4.{i}" for i in range(1, 23)],
        "social_distance": [f"James5.{i}" for i in range(1, 6)],
        "emotional_reactions": [f"James2.{i}" for i in range(2, 10)],
    }
    for i in range(1, 6):
        ok = df[f"James5.{i}"].isna() | (8 - df[f"James5.{i}"] == df[f"James5.{i}reversed"])
        assert ok.mean() > 0.99
    for name, items in blocks.items():
        assert all(c in df.columns for c in items)
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        bad = ~long["resp"].isin(range(1, 8))
        if name == "emotional_reactions":
            assert bad.sum() == 6 and set(long.loc[bad, "resp"]) <= {0, 888}
            assert long.loc[bad].groupby("item").size().max() == 1
        else:
            assert not bad.any(), (name, long.loc[bad, "resp"].unique())
        long = long[~bad]
        long["resp"] = long["resp"].astype(int)
        long["item"] = long["item"].str.lower()
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c.lower(): list(range(1, 8)) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = f"zeilinger_2020_{name}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
