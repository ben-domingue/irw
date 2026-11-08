#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0358990
# DOI: 10.1371/journal.pone.0358990
# Paper: Bando M, Asakura T, Sato H, Okajima I (2026). Reliability and
#   validity of the Japanese version of the Sleep Problem Acceptance
#   Questionnaire. PLoS ONE 21(10): e0358990.
# Data: OSF 10.17605/OSF.IO/8CGDB (public, CC BY 4.0, confirmed on the node):
#   SPAQ_data.csv with Codebook.pdf. 861 Japanese adults at Time 1; 371 of
#   them retook every questionnaire at Time 2 (columns suffixed _T2, "." =
#   not retaken). The codebook states responses are raw, not reverse-scored.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 6.
#
# SEVEN output tables, long over the two administrations (`wave` 1, 2):
#   bando_2026_spaq   Sleep Problem Acceptance Questionnaire, Japanese, 8
#     items 0-6 (1-4 activity engagement, 5-8 willingness, the latter
#     reverse-scored in the paper's analyses; stored as answered).
#   bando_2026_aaq2   AAQ-II, 7 items 1-7.
#   bando_2026_ais    Athens Insomnia Scale, 8 items 0-3.
#   bando_2026_dbas16 Dysfunctional Beliefs and Attitudes about Sleep-16,
#     16 items 0-10 (the codebook's variable list says 0-11; its measures
#     section and the data say 0-10).
#   bando_2026_srbq   Sleep-Related Behaviours Questionnaire, 15 items 0-4
#     (the codebook's heading misnames it; the paper uses it as the
#     safety-behaviours measure).
#   bando_2026_ics    Insomnia Catastrophizing Scale, 17 items 0-5 (ICS.N1-11
#     nighttime, ICS.D1-6 daytime).
#   bando_2026_psas   Pre-Sleep Arousal Scale, 16 items 1-5 (PSAS.S1-8
#     somatic, PSAS.C1-8 cognitive).
# Covariates: sex (1 male, 2 female, 3 other / prefer not to answer), age.
#   403 / 451 / 7.
# `id` is the deposit's ID (1-861, a row number).
#
# Item text: NOT SHIPPED. The SPAQ-J questionnaire PDF is on the same OSF
#   node (CC BY 4.0); the other six are published instruments.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://osf.io/download/7vxyk/"
RAW = os.environ.get("BANDO_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}

TABLES = {
    "spaq": ([f"SPAQ{i}" for i in range(1, 9)], range(0, 7)),
    "aaq2": ([f"AAQ{i}" for i in range(1, 8)], range(1, 8)),
    "ais": ([f"AIS{i}" for i in range(1, 9)], range(0, 4)),
    "dbas16": ([f"DBAS{i}" for i in range(1, 17)], range(0, 11)),
    "srbq": ([f"SRBQ{i}" for i in range(1, 16)], range(0, 5)),
    "ics": ([f"ICS.N{i}" for i in range(1, 12)] + [f"ICS.D{i}" for i in range(1, 7)], range(0, 6)),
    "psas": ([f"PSAS.S{i}" for i in range(1, 9)] + [f"PSAS.C{i}" for i in range(1, 9)], range(1, 6)),
}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_csv(src, encoding="utf-8-sig", na_values=["."])


def convert():
    df = load()
    assert df.shape == (861, 177), df.shape
    assert df["ID"].is_unique
    df["id"] = df["ID"].astype(int)
    df["cov_sex"] = df["sex"].map({1: "male", 2: "female", 3: "other or prefer not to answer"})
    df["cov_age"] = df["age"]
    assert df["cov_sex"].value_counts().to_dict() == {"female": 451, "male": 403, "other or prefer not to answer": 7}
    covs = ["cov_sex", "cov_age"]
    retest = df[[c for c in df.columns if c.endswith("_T2")]].notna().any(axis=1)
    assert retest.sum() == 371, retest.sum()

    for name, (items, values) in TABLES.items():
        parts = []
        for wave, suffix in [(1, ""), (2, "_T2")]:
            p = df[["id"] + covs + [i + suffix for i in items]].rename(columns={i + suffix: i for i in items})
            p = p.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
            p["wave"] = wave
            parts.append(p)
        long = pd.concat(parts, ignore_index=True)
        long = long[long["resp"].notna()].copy()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(values), name
        assert long.loc[long.wave == 1, "id"].nunique() == 861
        long = long[["id", "item", "resp", "wave"] + covs].sort_values(["id", "wave", "item"])
        checks = run_qc(long, permitted_values=list(values))
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = f"bando_2026_{name}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} wave2_ids={long.loc[long.wave == 2, 'id'].nunique()}")


if __name__ == "__main__":
    convert()
