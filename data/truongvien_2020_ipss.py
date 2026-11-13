#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/CMOHLS (Harvard Dataverse)
# DOI: 10.7910/DVN/CMOHLS (data)
#   Truong Vien N (2020). Replication Data for: Hospital-Based Prostate Cancer Screening in
#   Vietnamese men with lower urinary tract symptoms: A Classification and Regression Tree Model.
#   Harvard Dataverse.
# License: CC0 1.0 (Dataverse)
# Data: PCa_STATA.xlsx (format=original), 260 men aged >= 50 with self-reported lower urinary tract
#   symptoms at MEDIC Medical Center, Ho Chi Minh City, 2017-2018 (case-control, biopsy-confirmed).
#
# Table: truongvien_2020_ipss -- c1..c7, the seven International Prostate Symptom Score items,
#   0-5 (not at all .. almost always; item 7 nocturia 0-5 times), as stored. The deposit's total
#   (tongdiemIPSS) equals the item sum in 259 of 260 rows; items are taken as authoritative.
# Not shipped: PSA, risk-factor yes/no flags, IPSS/PSA groupings.
# id: row number (the file's id repeats for one pair of different men, id 59).
# Covariates: cov_age (tuoi).
# Item text: not shipped -- the deposit carries codes only; the IPSS is a published instrument.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://dataverse.harvard.edu/api/access/datafile/5740871?format=original"


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert len(d) == 260
    items = [f"c{i}" for i in range(1, 8)]
    print("total == item sum:", (d[items].sum(axis=1) == d["tongdiemIPSS"]).sum(), "of", len(d))
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["tuoi"]
    t = d[["id", "cov_age"] + items].melt(id_vars=["id", "cov_age"], var_name="item", value_name="resp")
    t = t.dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(0, 5).all()
    t = t[["id", "item", "resp", "cov_age"]].sort_values(["id", "item"])
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails
    t.to_csv(OUT / "truongvien_2020_ipss.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
