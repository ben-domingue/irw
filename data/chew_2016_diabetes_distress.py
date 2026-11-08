#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0152095
# DOI: 10.1371/journal.pone.0152095
# Paper: Chew B-H, Vos R, Mohd-Sidik S, Rutten GEHM (2016). Diabetes-related
#   distress, depression and distress-depression among adults with type 2
#   diabetes mellitus in Malaysia. PLoS ONE 11(3): e0152095.
# Data: figshare 10.6084/m9.figshare.3103060, "EDDMQoL- Dataset
#   Depository.sav" (labelled). 700 adults with type 2 diabetes at three
#   public health clinics in Selangor, 2013.
# License: CC BY 4.0 (figshare license field, api.figshare.com/v2/articles/3103060).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 7.
#
# TWO output tables:
#   chew_2016_dds17  Diabetes Distress Scale, DDS1-DDS17, 1 not a problem ..
#     6 a very serious problem.
#   chew_2016_phq9   PHQ-9, PHQ1-PHQ9, 0 not at all .. 3 nearly every day.
#     PHQ10 (the unscored difficulty question, unlabelled) dropped.
# Checks: the DDS item sum equals the deposit's TotalDDS and the PHQ item sum
#   its TotalPHQ on every complete row (asserted); 697 DDS means and 684
#   with a PHQ total, as in Table 1.
# Covariates: age, gender, clinic. Ethnicity, religion, marital status and
#   education codes are unlabelled and dropped, as are the clinical and
#   laboratory variables.
# `id` is the row index (CodeNumber is a clinic-level running number that
#   repeats within one clinic).
#
# Item text: NOT SHIPPED. DDS-17 and PHQ-9 are published instruments (the
#   variable labels carry the English wording).

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://ndownloader.figshare.com/files/4823968"
RAW = os.environ.get("CHEW2016_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_chew2016_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, meta = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df, meta


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
    df, meta = load()
    assert len(df) == 700, df.shape
    vl = meta.variable_value_labels
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["Age"]
    df["cov_gender"] = df["Gender"].map(vl["Gender"])
    df["cov_clinic"] = df["CodeCentre"].map(vl["CodeCentre"])
    covs = ["cov_age", "cov_gender", "cov_clinic"]

    dds = [f"DDS{i}" for i in range(1, 18)]
    full = df[dds].notna().all(axis=1)
    assert (df.loc[full, dds].sum(axis=1) == df.loc[full, "TotalDDS"]).all()
    assert df["MeanTotalDDS"].notna().sum() == 697
    out = df.rename(columns={c: c.lower() for c in dds})
    save(out, covs, [c.lower() for c in dds], "chew_2016_dds17", range(1, 7))

    phq = [f"PHQ{i}" for i in range(1, 10)]
    full = df[phq].notna().all(axis=1)
    assert (df.loc[full, phq].sum(axis=1) == df.loc[full, "TotalPHQ"]).all()
    assert df["TotalPHQ"].notna().sum() == 684
    out = df.rename(columns={c: c.lower() for c in phq})
    save(out, covs, [c.lower() for c in phq], "chew_2016_phq9", [0, 1, 2, 3])


if __name__ == "__main__":
    convert()
