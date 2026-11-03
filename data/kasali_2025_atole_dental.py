#!/usr/bin/env python3
# Source: https://zenodo.org/records/14645272
# DOI: 10.5281/zenodo.14645272 (data); paper 10.1186/s12909-025-08296-z
# Paper: Kaşali K, Özkal Eminoğlu D, Demirer Üstündağ Ş (2025). Validity and
#   reliability study of the dental students of attitudes towards online
#   learning scale. BMC Medical Education 25:1704. (The paper's Data Availability
#   statement cites a sibling record, zenodo.14244844; this record's 181
#   students, 48/133 gender split and year-of-study counts 16/17/21/69/58
#   match the paper's Table 2 exactly.)
# Data: data.xlsx, 181 dental students, Atatürk University, Turkey, 2024.
# License: CC BY 4.0 (verified on the Zenodo record; the article is CC BY).
#
# Found by the automated_finding repos sweep of 2026-11-02 (mode 3), worked
# from leads/repos_leads_2026-11-02.csv the same day (BATCH_LOG.md).
#
# ONE output table:
#   kasali_2025_atole_dental  Turkish adaptation for dental students of the
#     Medical School Students' Attitudes Towards Online Learning scale, 22
#     items: Item1..Item11 (the deposit's "1st factor: attitudes towards online
#     dental education") and Item12..Item22 ("attitudes towards online
#     learning"), each 1 strongly disagree .. 5 strongly agree (paper:
#     "responses ranging from 'Strongly Disagree (1)' to 'Strongly Agree (5)'").
#     The two subscale totals in the deposit are not shipped.
# Covariates: gender (1 = male, 2 = female: 48/133, matching the paper's
#   Table 2), year of study (1-5, matching Table 2's counts).
# NOT carried: the consent column (one value), and "why did you choose
#   dentistry" (multi-select Turkish reasons).
# `id` is the deposit's own row number.
#
# Item text: not shipped. The deposit and paper carry no item wording; the
#   scale is an adaptation of a published instrument.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("KASALI_RAW", "data.xlsx")
ITEMS = [f"Item{i}" for i in range(1, 23)]


def convert():
    df = pd.read_excel(RAW)
    df.columns = [str(c).strip() for c in df.columns]
    assert df.shape == (181, 29), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0
    for c in txt:  # consent + reason-for-dentistry only; both carry fixed option text
        assert df[c].nunique() <= 25, c
    f1 = [c for c in df.columns if c.startswith("1st factor")][0]
    f2 = [c for c in df.columns if c.startswith("2st factor")][0]
    assert (df[ITEMS[:11]].sum(axis=1) - df[f1]).abs().max() == 0
    assert (df[ITEMS[11:]].sum(axis=1) - df[f2]).abs().max() == 0
    assert df["Gender"].value_counts().to_dict() == {2: 133, 1: 48}
    assert df["no"].is_unique
    df["id"] = df["no"]
    df["cov_gender"] = df["Gender"].map({1: "male", 2: "female"})
    df["cov_year_of_study"] = df["Classroom"].astype(int)
    covs = ["cov_gender", "cov_year_of_study"]
    long = df[["id"] + covs + ITEMS].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    consent = [c for c in df.columns if c.startswith("I have read")]
    used = set(ITEMS) | {f1, f2, "no", "Gender", "Classroom", "why did you choose dentistry"} | set(consent)
    left = set(df.columns) - used - {"id"} - set(covs)
    assert not left, left
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, "kasali_2025_atole_dental.csv"), index=False)
    print(f"kasali_2025_atole_dental: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
