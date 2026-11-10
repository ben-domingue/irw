#!/usr/bin/env python3
# Source: https://zenodo.org/records/23808632
# DOI: 10.5281/zenodo.23808632 (no paper DOI on the record)
#   Komalasari, Y., M. Mamoriska Harahap, S., & Hidayat, A. (2026). "Initial
#   Trust in Digital Vehicle Financing: Evidence from Potential ACC One Users."
#   Zenodo.
# Data: "ACC ONE DATA 160 CLEAN (1).xlsx", sheet 'Form Responses 1' (160 rows x
#   24 columns; Google Form export, Indonesian prospective users of a
#   vehicle-financing app).
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# Item text: not shipped -- headers are construct codes only (IT1..BI3); the
#   questionnaire wording is not in the deposit. Both levels checked: the
#   xlsx has no stem row, no codebook sheet.
#
# SCALE: plain 1-5 on every item (no extra category). The anchors are not
#   stated in the deposit; within-construct correlations are all positive
#   (IT .69-.73, PFR .53-.72, BI .76-.87), so each block runs one way.
#
# Tables (one per construct, per the record's abstract):
#   komalasari_2026_initial_trust     IT1-IT3
#   komalasari_2026_financial_risk    PFR1-PFR3 (perceived financial risk)
#   komalasari_2026_behav_intention   BI1-BI3
# Dropped, with reasons:
#   TP1-TP2     information transparency, 2 items (under the 3-item floor)
#   Timestamp   submission time
# Covariates: age band, gender, occupation, monthly income band, vehicle
#   financing status, fintech use frequency, vehicle type, financing purpose,
#   and the four yes/no screening questions, as the form's own labels.
# id: row index + 1 (the export carries no respondent identifier).

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
DATA_URL = ("https://zenodo.org/api/records/23808632/files/"
            "ACC%20ONE%20DATA%20160%20CLEAN%20%281%29.xlsx/content")
SCALES = {
    "komalasari_2026_initial_trust": ["IT1", "IT2", "IT3"],
    "komalasari_2026_financial_risk": ["PFR1", "PFR2", "PFR3"],
    "komalasari_2026_behav_intention": ["BI1", "BI2", "BI3"],
}
COVS = [  # (header prefix, cov name)
    ("Age", "cov_age_band"),
    ("Have you obtained or are you currently", "cov_acc_financing_now"),
    ("Have you ever applied for vehicle financing", "cov_acc_one_applied"),
    ("Do you use digital financial services", "cov_uses_digital_finance"),
    ("Consider using the ACC One app", "cov_considers_acc_one"),
    ("Gender", "cov_gender"),
    ("Occupation", "cov_occupation"),
    ("Income Average", "cov_income_band"),
    ("Status Vehicle", "cov_financing_status"),
    ("Fintech Usage Frequency", "cov_fintech_frequency"),
    ("Type of Vehicle", "cov_vehicle_type"),
    ("Primary Purpose", "cov_financing_purpose"),
]
ALLOWED = {1, 2, 3, 4, 5}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Form Responses 1")
    d.columns = [str(c).strip() for c in d.columns]
    assert d.shape == (160, 24), d.shape

    ren = {}
    for pre, name in COVS:
        hit = [c for c in d.columns if c.startswith(pre)]
        assert len(hit) == 1, (pre, hit)
        ren[hit[0]] = name
    items = [c for cols in SCALES.values() for c in cols]
    known = set(ren) | set(items) | {"Timestamp", "TP1", "TP2"}
    assert set(d.columns) == known, set(d.columns) ^ known
    print("[drop] Timestamp, TP1, TP2")

    d = d.rename(columns=ren).reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    cov_cols = [n for _, n in COVS]
    for c in cov_cols:
        d[c] = d[c].astype(str).str.strip().replace({"nan": pd.NA})

    for table, cols in SCALES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                      var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
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
