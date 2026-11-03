#!/usr/bin/env python3
# Source: https://zenodo.org/records/7109117
# DOI: 10.5281/zenodo.7109117 (data); paper 10.12688/f1000research.125266.1
# Paper: Esteves Pairazaman AT, Parreño Tipian JM, Ramos Jaco AG, Luján
#   Orbegón TA, Mamani Mamani NE, Trujillo Román RI, et al. (2022). Knowledge
#   and attitude of the people in San Juan de Miraflores towards the disposal
#   of medicines. F1000Research 11:1187.
# Data: DATA.sav (385 adults, San Juan de Miraflores district, Lima, Peru),
#   with "DATA KEY Knowledge and attitude.txt" and the Spanish (administered)
#   and English questionnaires in the same deposit.
# License: CC BY 4.0 (verified on the Zenodo record).
#
# Found by the automated_finding repos sweep of 2026-11-02 (mode 3), worked
# from leads/repos_leads_2026-11-02.csv the same day (BATCH_LOG.md).
#
# TWO output tables (named "meds" for the 40-character table-name cap):
#   esteves_pairazaman_2022_meds_knowledge  P6..P14, nine
#     multiple-choice knowledge questions scored 0 = incorrect, 1 = correct
#     (value labels in the .sav; the items sum to TotalKnowledgeScore).
#   esteves_pairazaman_2022_meds_attitude  A1..A6 (questionnaire
#     items 15-20), 1 strongly disagree .. 5 strongly agree (value labels in
#     the .sav and the data key); the items sum to TotalScoreAttitude.
# NOT shipped: Tablets/Ointments/Cough_syrup/Inhalers are byte-for-byte
#   copies of P9..P12 (checked below); the composites TotalKnowledgeScore,
#   Levelofknowledge, TotalScoreAttitude, TypeofAttitude.
# Covariates (value labels in the .sav): sex, age band, civil status,
#   education, occupation. `id` is the deposit's own row number N°.
#
# PII: no text columns at all (checked below).
#
# Item text: not shipped. The Spanish (administered) and English wording of
#   all 15 items, and the keyed option of every knowledge item, are in the
#   deposit's two .docx questionnaires (study-authored items). Not attempted
#   in this batch: the knowledge items are scored, so the option rows would
#   have to describe "correct"/"incorrect" rather than the four printed
#   options, which needs a rule decision first.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("ESTEVES_RAW", "DATA.sav")
KNOW = [f"P{i}" for i in range(6, 15)]
ATT = [f"A{i}" for i in range(1, 7)]
DUPS = {"Tablets": "P9", "Ointments": "P10", "Cough_syrup": "P11", "Inhalers": "P12"}
COMPOSITES = {"TotalKnowledgeScore", "Levelofknowledge", "TotalScoreAttitude", "TypeofAttitude"}
COVS = {"Sex": "cov_sex", "Age": "cov_age_band", "Statuscivil": "cov_civil_status",
        "Levelofeducation": "cov_education", "Professionoroccupation": "cov_occupation"}


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert df.shape == (385, 29), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and txt == []
    for a, b in DUPS.items():
        assert (df[a] == df[b]).all(), a
    assert (df[KNOW].sum(axis=1) - df["TotalKnowledgeScore"]).abs().max() == 0
    assert (df[ATT].sum(axis=1) - df["TotalScoreAttitude"]).abs().max() == 0
    assert df["N°"].is_unique
    df["id"] = df["N°"].astype(int)
    for src, dst in COVS.items():
        lab = meta.variable_value_labels[src]
        df[dst] = df[src].map(lab)
        assert df[dst].notna().all(), src
    df["cov_sex"] = df["cov_sex"].map({"Masculino": "male", "Femenino": "female"})
    covs = list(COVS.values())
    out = {}
    for name, items, permitted in [("knowledge", KNOW, [0, 1]), ("attitude", ATT, [1, 2, 3, 4, 5])]:
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        assert set(long["resp"]) <= set(permitted)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: permitted for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        out[f"esteves_pairazaman_2022_meds_{name}"] = long
    used = set(KNOW) | set(ATT) | set(DUPS) | COMPOSITES | set(COVS) | {"N°"}
    left = set(df.columns) - used - {"id"} - set(covs)
    assert not left, left
    assert len(out) == len(set(out))
    os.makedirs(OUT_DIR, exist_ok=True)
    for t, long in out.items():
        long.to_csv(os.path.join(OUT_DIR, f"{t}.csv"), index=False)
        print(f"{t}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
