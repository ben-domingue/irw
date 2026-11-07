#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0132438
# DOI: 10.1371/journal.pone.0132438
# Paper: Kirkland T, Gruber J, Cunningham WA (2015). Comparing Happiness and
#   Hypomania Risk: A Study of Extraversion and Neuroticism Aspects. PLoS ONE
#   10(7): e0132438.
# Data: PLOS Supporting Information S1 File (journal.pone.0132438.s001, "Raw
#   Data. Data for all waves"), CSV, 1,019 rows; "." marks a missing cell.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 2.
#
# The file's `wave` is NOT a repeated measurement: the paper's three "waves of
# data collection" are three independent samples -- 352 undergraduates
# (course credit), 466 MTurk adults, 201 MTurk adults -- analysed together as
# replications. `subject` restarts in each sample (353 subject numbers occur
# in more than one sample, as different people), so `id` = sample * 1000 +
# subject and the sample is carried as cov_sample (1 undergraduate, 2 and 3
# MTurk). The same instruments were given to every sample, so each ships as
# one merged table. All rows ship, including the respondents the paper
# dropped for not completing every measure.
#
# FIVE output tables, item codes the deposit's own:
#   kirkland_2015_panas  Positive and Negative Activation Schedule, PANAS1-20,
#                        1-5 (trait: "how you feel on average")
#   kirkland_2015_shs    Subjective Happiness Scale, SHS1-4, 1-7
#   kirkland_2015_bfas   Big Five Aspect Scales, BFAS1-100, 1-5
#   kirkland_2015_hps    Hypomanic Personality Scale, HPS1-48, true-false,
#                        stored as the deposit's 1/2 codes (which code is
#                        "true" is not stated; within each item the coding is
#                        consistent)
#   kirkland_2015_asrm   Altman Self-Rating Mania Scale, ASRM1-5, 0-4
#                        (samples 2 and 3 only)
# All stored as deposited; no reverse-keyed item is recoded.
# Dropped: BDI1-BDI12 -- the paper describes a 13-item Beck Depression
#   Inventory short form scored 0-3, the file has 12 columns, and 448 of its
#   7,752 cells hold 6 or 7, which the paper does not explain.
# No covariates in the file beyond the sample.
#
# Item text: NOT SHIPPED. Header codes only; no codebook in the SI; all are
#   published instruments.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0132438.s001"
RAW = os.environ.get("KIRKLAND_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SAMPLE = {1: "undergraduate", 2: "mturk_2", 3: "mturk_3"}
SCALES = {
    "panas": ([f"PANAS{i}" for i in range(1, 21)], range(1, 6)),
    "shs": ([f"SHS{i}" for i in range(1, 5)], range(1, 8)),
    "bfas": ([f"BFAS{i}" for i in range(1, 101)], range(1, 6)),
    "hps": ([f"HPS{i}" for i in range(1, 49)], range(1, 3)),
    "asrm": ([f"ASRM{i}" for i in range(1, 6)], range(0, 5)),
}
DROPPED = [f"BDI{i}" for i in range(1, 13)]


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=120)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_csv(src, na_values=["."])


def convert():
    df = load()
    assert df.shape == (1019, 191), df.shape
    used = {"wave", "subject"} | set(DROPPED) | {c for v in SCALES.values() for c in v[0]}
    assert used == set(df.columns), set(df.columns) ^ used
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and not txt
    assert not df.duplicated(["wave", "subject"]).any()
    assert df["subject"].max() < 1000
    df["id"] = df["wave"].astype(int) * 1000 + df["subject"].astype(int)
    df["cov_sample"] = df["wave"].astype(int).map(SAMPLE)
    covs = ["cov_sample"]
    total = 0
    for key, (items, perm) in SCALES.items():
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= set(perm), (key, set(long["resp"]))
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(perm) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {key} {c.name}: {c.detail[:150]}")
        out = f"kirkland_2015_{key}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        total += len(long)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    print(f"total responses {total}; dropped {len(DROPPED)} BDI columns")


if __name__ == "__main__":
    convert()
