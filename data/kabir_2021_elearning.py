#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0259281
# DOI: 10.1371/journal.pone.0259281
# Paper: Kabir H, Nasrullah SM, Hasan MK, Ahmed S, Hawlader MDH, Mitra DK
#   (2021). Perceived e-learning stress as an independent predictor of
#   e-learning readiness: Results from a nationwide survey in Bangladesh.
#   PLoS ONE 16(10): e0259281.
# Data: Zenodo 10.5281/zenodo.5068463 "E-learning Data Archive" (CC BY 4.0,
#   confirmed on the record), E-learning_dataset.xls. 1,162 university
#   students, online Google Form survey, 2020.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 6.
#
# TWO output tables:
#   kabir_2021_elearning_readiness  39 items, 1 strongly disagree to 5
#     strongly agree (availability of technology 6, use of technology 11,
#     self-confidence 12, acceptance 7, training 3). The item sum equals the
#     deposit's sum_readiness_scale on every row (asserted).
#   kabir_2021_elearning_stress  the 14-item perceived e-learning stress
#     scale (PLSS, adapted from Cohen's PSS-14), 0-4. STORED AS DEPOSITED,
#     i.e. already scored: the plain item sum equals the deposit's
#     sum_stress_scale on every row (asserted), so the seven positive items
#     the paper reverse-scores (1, 2, 3, 8, 11, 12, 14) are deposited
#     reversed. Those seven carry an "r" suffix in the item code.
# Covariates (text in the deposit): gender, degree, residence, age band,
#   division (Dhaka / outside), institution type. 52.15% female (paper).
# `id` is the row index.
#
# Item text: NOT SHIPPED. Wording is not in the deposit; the readiness
#   items are in the paper's Table 2 (CC BY), the PLSS is PSS-derived.

import io
import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://zenodo.org/api/records/5068463/files/E-learning_dataset.xls/content"
RAW = os.environ.get("KABIR_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV"]
REVERSED = {1, 2, 3, 8, 11, 12, 14}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        src = io.BytesIO(r.content)
    return pd.read_excel(src)


def save(df, covs, items, name, values):
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(values)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df = load()
    assert df.shape == (1162, 80), df.shape
    df["id"] = range(1, len(df) + 1)
    cmap = {"Gender": "cov_gender", "Degree": "cov_degree", "Residence": "cov_residence",
            "Age": "cov_age_band", "Division": "cov_division", "Type_institution": "cov_institution_type"}
    for a, b in cmap.items():
        df[b] = df[a]
    covs = list(cmap.values())
    assert round((df["cov_gender"] == "Female").mean() * 100, 2) == 52.15

    ready = [f"readiness_item_{i}" for i in range(1, 40)]
    assert (df[ready].sum(axis=1) == df["sum_readiness_scale"]).all()
    df = df.rename(columns={c: c.replace("readiness_item_", "ready") for c in ready})
    save(df, covs, [f"ready{i}" for i in range(1, 40)], "kabir_2021_elearning_readiness", range(1, 6))

    src = [f"stress_item_{r}" for r in ROMAN]
    assert (df[src].sum(axis=1) == df["sum_stress_scale"]).all()
    new = [f"plss{i}r" if i in REVERSED else f"plss{i}" for i in range(1, 15)]
    df = df.rename(columns=dict(zip(src, new)))
    save(df, covs, new, "kabir_2021_elearning_stress", range(0, 5))


if __name__ == "__main__":
    convert()
