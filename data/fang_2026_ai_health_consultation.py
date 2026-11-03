#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/KOFRAU
# DOI: 10.7910/DVN/KOFRAU (data; no article found)
# Deposit: Fang Z (2026). Survey data on user perceptions, algorithm aversion,
#   and use intentions toward AI health consultation tools in China. Harvard
#   Dataverse.
# Data: Data.xlsx (230 adults in China with prior use of AI health
#   consultation tools, Credamo online panel, February 2025) and Codebook.docx
#   (item wording, scale anchors, covariate codes).
# License: CC0 1.0 (verified on the Dataverse record).
#
# Found by the automated_finding repos sweep of 2026-11-02 (mode 3; Step 2b
# recoverable_format), worked from leads/repos_leads_2026-11-02.csv the same
# day (BATCH_LOG.md).
#
# SEVEN output tables, one per construct in the codebook, every item
#   1 strongly disagree .. 7 strongly agree (codebook: "All measurement items
#   were assessed using a seven-point Likert scale, ranging from 1 = Strongly
#   disagree to 7 = Strongly agree"):
#   fang_2026_aihealth_perf_risk     PPR1-5  perceived performance risk
#   fang_2026_aihealth_privacy       PPC1-6  perceived privacy concern
#   fang_2026_aihealth_inertia       INE1-3  inertia
#   fang_2026_aihealth_resist_change DRC1-4  dispositional resistance to change
#   fang_2026_aihealth_health_consc  HC1-4   health consciousness
#   fang_2026_aihealth_algo_aversion AA1-5   algorithm aversion
#   fang_2026_aihealth_intention     ITU1-4  intention to use
# Covariates (codebook): gender (0 female, 1 male), age band, education,
#   duration of prior use.
# `id` is the row index.
#
# Item text: not shipped. The codebook prints English stems for every item,
#   but the survey ran in China on Credamo and the administered (Chinese)
#   wording is not in the deposit; the items are adapted from published
#   scales with no rights reading.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("FANG_RAW", "Data.xlsx")
BLOCKS = {"perf_risk": ("PPR", 5), "privacy": ("PPC", 6), "inertia": ("INE", 3), "resist_change": ("DRC", 4),
          "health_consc": ("HC", 4), "algo_aversion": ("AA", 5), "intention": ("ITU", 4)}
COVS = {
    "GEN": ("cov_gender", {0: "female", 1: "male"}),
    "AGE": ("cov_age_band", {1: "under 20", 2: "20-29", 3: "30-39", 4: "40-49", 5: "50+"}),
    "EDU": ("cov_education", {1: "senior high school or lower", 2: "college degree", 3: "bachelor's degree",
                              4: "master's degree or higher"}),
    "DUR": ("cov_prior_use", {2: "0-6 months", 3: "6-12 months", 4: "1-1.5 years", 5: "1.5-2 years",
                              6: "2 years or more"}),
}


def convert():
    df = pd.read_excel(RAW)
    assert df.shape == (230, 35), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    df["id"] = range(1, len(df) + 1)
    covs = []
    for src, (dst, lab) in COVS.items():
        df[dst] = df[src].map(lab)
        assert df[dst].notna().all(), src
        covs.append(dst)
    out, used = {}, set(COVS)
    for name, (p, k) in BLOCKS.items():
        items = [f"{p}{i}" for i in range(1, k + 1)]
        used |= set(items)
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        assert set(long["resp"]) <= set(range(1, 8))
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(range(1, 8)) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out[f"fang_2026_aihealth_{name}"] = long
    left = set(df.columns) - used - {"id"} - set(covs)
    assert not left, left
    assert len(out) == len(BLOCKS) and all(len(t) <= 40 for t in out)
    os.makedirs(OUT_DIR, exist_ok=True)
    for t, long in out.items():
        long.to_csv(os.path.join(OUT_DIR, f"{t}.csv"), index=False)
        print(f"{t}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
