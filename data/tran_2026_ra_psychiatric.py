#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0342909
# DOI: 10.1371/journal.pone.0342909
# Paper: Tran HTT, Duong TM, Nguyen TV, et al. (2026). Suicidal ideation and
#   interrelated psychiatric disturbances in rheumatoid arthritis: Evidence
#   from a Vietnamese cohort. PLoS ONE 21(3): e0342909.
# Data: PLOS SI S1 File (journal.pone.0342909.s008, rasuicide_dataset.xlsx;
#   also Harvard Dataverse 10.7910/DVN/KCQKHM, CC0 1.0). Sheets data / vars /
#   codes (the codebook). 187 RA patients, Bach Mai Hospital, Hanoi,
#   2024; clinician-administered interviews.
# License: CC BY 4.0 as PLOS SI; CC0 1.0 on Dataverse.
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# FIVE output tables, items as recorded (the vars sheet gives the English
#   item labels; item codes keep the deposit's names):
#   tran_2026_phq9   PHQ-9, 9 items, 0-3.
#   tran_2026_madrs  MADRS, 10 items, 0-6.
#   tran_2026_hama   HAM-A, 14 items, 0-4.
#   tran_2026_isi    Insomnia Severity Index, 7 items, 0-4.
#   tran_2026_eq5d   EQ-5D-5L descriptive system, 5 items, coded 0-4
#     (0 = no problems).
# Dropped: ASEX (sex-specific items, 509 empty cells), the ICD-10 depression
#   criteria checklist, MoCA domain sub-scores, knowledge items, short
#   free-text medical-history fields, clinical labs.
# Covariates: inpatient/outpatient, location (codes sheet labels). dem_edu
#   is not carried: it holds codes 1-6 but the codes sheet labels only 1-2.
#   The deposit carries no age or sex column.
# `id` = row index.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0342909.s008"
RAW = os.environ.get("TRAN2026_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_tran2026_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path, sheet_name="data")
    if not RAW:
        os.remove(path)
    return df


def save(df, covs, src, name, values):
    sub = df[["id"] + covs + src]
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(values), set(long["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def cols(df, prefix, n):
    out = [c for c in df.columns if c.startswith(prefix)]
    assert len(out) == n, (prefix, out)
    return out


def convert():
    df = load()
    assert len(df) == 187
    df = df.reset_index(drop=True).copy()
    df["id"] = df.index + 1
    df["cov_inpatient"] = df["dem_inoutpt"].map({1: "inpatient", 2: "outpatient"})
    df["cov_location"] = df["dem_location"].map({1: "urban", 2: "rural", 3: "mountainous", 4: "other"})
    covs = ["cov_inpatient", "cov_location"]
    save(df, covs, cols(df, "phq_", 9), "tran_2026_phq9", range(0, 4))
    save(df, covs, cols(df, "mont_", 10), "tran_2026_madrs", range(0, 7))
    save(df, covs, cols(df, "hal_", 14), "tran_2026_hama", range(0, 5))
    save(df, covs, cols(df, "isi_", 7), "tran_2026_isi", range(0, 5))
    save(df, covs, cols(df, "eq_", 5), "tran_2026_eq5d", range(0, 5))


if __name__ == "__main__":
    convert()
