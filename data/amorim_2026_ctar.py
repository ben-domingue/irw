#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/34515174
# DOI: 10.6084/m9.figshare.34515174.v2 (data; no paper DOI on the record)
#   Amorim, S. C. D., Sa Filho, A. S., Oliveira, L. V. F., et al. (2026).
#   "Dataset - Effects of physical activity on test anxiety in students: a
#   randomized clinical trial." figshare.
# Data: "Data from a randomized clinical trial.xlsx", sheet 1: 237 Brazilian
#   students aged 13-17 (rows above the "Application of the exclusion
#   criteria" block, which lists excluded students and is not used), with
#   body composition, HRV, steps and the Cognitive Test Anxiety Scale-Revised
#   (CTAR-25) items A1-A25; sheet "Codes" decodes sex, school, arm.
# License: CC BY 4.0 (figshare record).
# Codebook: the "Codes" sheet inside the data file.
#
# Item text: not shipped -- codes only (A1..A25); wording is in the published
#   CTAR (Cassady & Finch).
#
# Table: amorim_2026_ctar, A1-A25, 1-4, one administration (the deposit does
#   not say whether before or after the intervention; it sits after the pre-
#   and post-intervention HRV blocks). The deposit's CTAR25 total is asserted
#   equal to the item sum and not shipped.
# Covariates: cov_group (intervention/control), cov_sex, cov_age, cov_grade
#   (8-12), cov_school (code 1-7; the Codes sheet names public schools, not
#   carried). "Identification name" is a per-class number, not a name; id =
#   the deposit's Code.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/71181649"
TABLE = "amorim_2026_ctar"
ITEMS = [f"A{i}" for i in range(1, 26)]
ALLOWED = {1, 2, 3, 4}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name=0, header=1)
    stop = d.index[d["A1"].astype(str) == "A1"]
    assert len(stop) == 1
    d = d.loc[: stop[0] - 1].dropna(subset=["Code "])
    assert len(d) == 237, len(d)
    total = d.columns[87]
    assert str(total).startswith("CTAR25")
    x = d[ITEMS].astype(float)
    assert (x.sum(axis=1) == d[total].astype(float)).all()
    d["id"] = d["Code "].astype(int)
    assert d["id"].is_unique
    d["cov_group"] = d["Physical Activity Intervention (1) Control (2)"].map(
        {1: "intervention", 2: "control"})
    d["cov_sex"] = d["Sex (1=male; 2= female) "].map({1: "male", 2: "female"})
    d["cov_age"] = d["Age"].astype(int)
    grade = [c for c in d.columns if str(c).startswith("Series")][0]
    d["cov_grade"] = d[grade].astype(int) + 7
    d["cov_school"] = d["Schools"].astype(int)
    covs = ["cov_group", "cov_sex", "cov_age", "cov_grade", "cov_school"]
    assert d[covs].notna().all().all()
    long = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item",
                  value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert not set(long["resp"]) - ALLOWED
    long = long[["id", "item", "resp"] + covs]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    checks = run_qc(long, permitted_values={c: ALLOWED for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {c.name}: {c.detail[:130]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{TABLE}.csv").write_text(long.to_csv(index=False))
    print(f"[write] {TABLE}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
