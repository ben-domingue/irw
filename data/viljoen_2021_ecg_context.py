#!/usr/bin/env python3
# Source: https://zivahub.uct.ac.za/articles/dataset/Clinically_contextualised_ECG_interpretation/14297708
# DOI (data): 10.25375/uct.14297708
# DOI (paper): 10.1186/s12909-021-02854-x
# Data: Viljoen, C., Millar, R. S., Manning, K., Hoevelmann, J., & Burch, V.
#   (2021). Clinically contextualised ECG interpretation. University of Cape
#   Town ZivaHub (figshare), "clinically contextualised ECG
#   interpretation.xlsx". Paper: Viljoen et al. (2021), BMC Medical
#   Education, 21, 417.
# License: CC BY-NC 4.0 (ZivaHub record, via the figshare API). Derived
#   licence keeps the NC term. Paper CC BY 4.0.
#
# Found by the second repos sweep of 2026-11-10 (lane C, "ECG
#   interpretation"; triage flag good).
#
# Design (deposit description): 176 participants -- 67 junior (4th-year) and
#   55 senior (6th-year) medical students and 54 residents at UCT -- answered
#   the same 25 ECG MCQs twice: Test 1 without and Test 2 with a clinical
#   vignette. Checked: 176 and the 67/55/54 split reproduce; 4 participants
#   have no test answers at all and drop out (172 in the table).
#
# ONE output table:
#   viljoen_2021_ecg_context  50 items scored 0/1 (1 = correct): the 25 ECG
#     diagnoses as named in the deposit (sinus_arrhythmia ... hyperkalaemia;
#     AV_block_1st_degree shortened to AV_block_1st, see convert()),
#     Test 1) and the same 25 with the suffix _scen (Test 2, with vignette).
#     item_family = the diagnosis, pairing each ECG's two administrations.
#   prolonged_QT_scen is NOT shipped: the file has two candidate Test 2
#     columns for that ECG (prolonged_QT_scen, 58 blanks; and
#     prolonged_QT_seen_scen, complete) and nothing says which is the
#     answer. Test 1 prolonged_QT ships.
# Covariates: cohort (junior student / senior student / resident).
# Dropped: the exposure survey ("when last seen", "seen") -- 25 categorical
#   recency questions, not a scale.
# `id` is the deposit's participant number.
#
# Item text: NOT SHIPPED. The ECG tracings and vignettes are not deposited.

import os
import sys

import numpy as np
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")


def write(d, items, permitted, name, covs, codes=None, drop_values=()):
    codes = codes or items
    sub = d[["id"] + covs + items].rename(columns=dict(zip(items, codes)))
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long[~long["resp"].isin(drop_values)]
    assert (long["resp"] == np.floor(long["resp"])).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(permitted), set(long["resp"])
    long["item_family"] = long["item"].str.replace("_scen$", "", regex=True)
    long = long[["id", "item", "resp"] + covs + ["item_family"]]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in codes})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")

RAW = os.environ.get("VILJOEN_RAW", "clinically contextualised ECG interpretation.xlsx")


def convert():
    d = pd.read_excel(RAW)
    assert d.shape == (176, 103) and d["participant"].is_unique
    assert d["cohort"].value_counts().to_dict() == {"junior student": 67, "senior student": 55, "resident": 54}
    t1 = list(d.columns[52:77])
    t2 = list(d.columns[77:102])
    assert t1[0] == "sinus_arrhythmia" and t1[-1] == "hyperkalaemia"
    assert all(c.endswith("_scen") for c in t2)
    t2 = [c for c in t2 if c != "prolonged_QT_scen"]
    assert len(t2) == 24
    d = d.copy()
    d["id"] = d["participant"]
    d["cov_cohort"] = d["cohort"]
    # irw_lint_covariates reads "..._degree" as a covariate name; the ECG is a
    # first-degree AV block, so the code is shortened (reversibly) to AV_block_1st.
    codes = [c.replace("AV_block_1st_degree", "AV_block_1st") for c in t1 + t2]
    write(d, t1 + t2, [0, 1], "viljoen_2021_ecg_context", ["cov_cohort"], codes=codes)


if __name__ == "__main__":
    convert()
