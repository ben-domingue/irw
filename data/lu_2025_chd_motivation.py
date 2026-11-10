#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/m7k8638rmc
# DOI: 10.17632/m7k8638rmc (data; no paper DOI on the record)
#   Lu, Y. (2025). "Coronary Heart Disease - Motivation for Health
#   Behavior_Data_Lu." Mendeley Data.
# Data: stage1-749.xlsx (first-round assessment, n = 749) and
#   stage2-347.xlsx (second-round assessment, n = 347, a separate sample: the
#   record says IDs are numbered "in each round"). The test-retest file
#   (n = 35) is not used. The record description is the codebook.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: not shipped -- codes only (mo1..mo18, se1.., oe1..); no
#   questionnaire in the deposit. SSEE / SOEE (Resnick) and the MCLHB-DRR
#   general-motivation subscale are published third-party scales.
#
# SCALE: 1-5 on every item shipped.
#
# Tables:
#   lu_2025_chd_motivation_s1  mo1-mo18 (the developed motivation scale,
#                              18-item draft), stage 1, 749 patients
#   lu_2025_chd_motivation_s2  the 12 retained mo items (mo3, mo4, mo6, mo7,
#                              mo10-13, mo15-18), stage 2, 347 patients.
#                              Not merged with s1: different samples and a
#                              different (reduced) form, and the deposit does
#                              not state that the 12 were re-administered
#                              unchanged.
#   lu_2025_mcl_general        mognr1-4 (general motivation dimension of the
#                              Motivation to Change Lifestyle and Health
#                              Behaviors for Dementia Risk Reduction Scale), stage 2
#   lu_2025_ssee               se1-4 (Short Self-Efficacy for Exercise), stage 2
#   lu_2025_soee               oe1-5 (Short Outcome Expectation for Exercise), stage 2
# Not shipped: movas (single 0-10 visual analogue item); gender (1/2 codes,
#   unlabelled in the record).
# Covariates: cov_age, cov_education (labels from the record).
# id: ID in stage 2; row index + 1 in stage 1, where 8 ID values occur twice
#   on rows that differ in age and education (different patients).

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASE = "https://data.mendeley.com/public-files/datasets/m7k8638rmc/files/"
S1 = BASE + "37eaee68-062d-4083-80eb-9db0673bde67/file_downloaded"
S2 = BASE + "3617eec5-c74c-4ed7-902b-95a568b10634/file_downloaded"
EDU = {1: "primary school or below", 2: "junior high school",
       3: "high school/technical secondary school", 4: "associate degree",
       5: "bachelor's degree", 6: "postgraduate degree"}
MO12 = ["mo3", "mo4", "mo6", "mo7", "mo10", "mo11", "mo12", "mo13",
        "mo15", "mo16", "mo17", "mo18"]
TABLES = [  # (table, stage, items)
    ("lu_2025_chd_motivation_s1", 1, [f"mo{i}" for i in range(1, 19)]),
    ("lu_2025_chd_motivation_s2", 2, MO12),
    ("lu_2025_mcl_general", 2, [f"mognr{i}" for i in range(1, 5)]),
    ("lu_2025_ssee", 2, [f"se{i}" for i in range(1, 5)]),
    ("lu_2025_soee", 2, [f"oe{i}" for i in range(1, 6)]),
]
ALLOWED = {1, 2, 3, 4, 5}


def load(url, shape):
    r = requests.get(url, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert d.shape == shape, d.shape
    if d["ID"].is_unique:
        d["id"] = d["ID"].astype(int)
    else:  # stage 1: 8 IDs used twice, by people of different age/edu
        d = d.reset_index(drop=True)
        d["id"] = d.index + 1
    d["cov_age"] = d["age"]
    d["cov_education"] = d["edu"].map(EDU)
    assert d["cov_education"].notna().all()
    return d


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stages = {1: load(S1, (749, 22)), 2: load(S2, (347, 30))}
    cov_cols = ["cov_age", "cov_education"]
    for table, st, cols in TABLES:
        d = stages[st]
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert not set(long["resp"]) - ALLOWED
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: ALLOWED for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:130]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
