#!/usr/bin/env python3
# Source: https://yorksj.figshare.com/articles/dataset/Multidimensional_Perfectionism_is_Related_to_Burnout_in_Surgeons_-_Data_and_Code/29533175/2
# DOI: 10.25421/yorksj.29533175 (data); paper 10.1177/13591053261449051
#   Hill AP, Madigan DJ, Chintapatla S, Chitsabesan P (2026). Multidimensional
#   perfectionism is related to burnout in surgeons. Journal of Health
#   Psychology.
# Data: "Hill et al (2025) - data.sav" (339 UK surgeons x 46 columns) and the
#   deposit's SPSS syntax, which gives the scoring used below.
# License: CC BY 4.0 (figshare record).
# Codebook: none beyond the SPSS value labels and the syntax file.
#
# Counts: 339 respondents in the file. The syntax drops 37 cases with >5%
#   missing and then univariate/multivariate outliers; the paper analyses 298.
#   All 339 rows ship (IRW keeps the deposit, not the analysis sample).
# id: the file's ID repeats on two pairs of clearly different people (168 and
#   281: different ethnicity, specialty, years qualified), so id = row index.
#
# Tables (items as deposited; no reverse-scoring applied):
#   hill_2026_mps15  brief Multidimensional Perfectionism Scale, 15 items, 1-7
#                    (Strongly Disagree..Strongly Agree). Syntax: SOP = items
#                    1,3,5,7,9; SPP = 2,4,6,8,10; OOP = 11-15 reverse-keyed.
#   hill_2026_mbi    Maslach Burnout Inventory, 22 items, 1-7 (Never..Everyday;
#                    the published 0-6 frequency scale stored +1). Syntax:
#                    EX = 1,2,3,6,8,13,14,16,20; DP = 5,10,11,15,22;
#                    PA = 4,7,9,12,17,18,19,21.
# Covariates: GMC registration (yes/no), age, sex, marital status, ethnicity
#   (coded), specialty, grade, years qualified -- all value-labelled codes as
#   deposited.
# Item text: not shipped -- the file has value labels (response anchors) but no
#   variable labels for any item; MBI wording is Mind Garden copyright and the
#   brief MPS wording is in the published scale, not the deposit.

import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/56139539"

COVS = {"GMC": "cov_gmc_registered", "Age": "cov_age", "Sex": "cov_sex",
        "Maritial_status": "cov_marital_status", "Ethnicity": "cov_ethnicity",
        "Specialty": "cov_specialty", "Grade": "cov_grade",
        "Yrs_qualified": "cov_years_qualified"}
SPEC = {
    "hill_2026_mps15": ([f"MPS_{i}" for i in range(1, 16)], range(1, 8)),
    "hill_2026_mbi": ([f"MBI_{i}" for i in range(1, 23)], range(1, 8)),
}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content)
        f.flush()
        d, _ = pyreadstat.read_sav(f.name)
    assert d.shape == (339, 46), d.shape
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    used = {"ID"} | set(COVS)
    for cols, _ in SPEC.values():
        used |= set(cols)
    assert used == set(d.columns) - {"id"}, set(d.columns) - used
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (cols, vals) in SPEC.items():
        allowed = set(vals)
        long = d[["id"] + cols + covs].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp"
        ).dropna(subset=["resp"])
        assert not set(long["resp"]) - allowed, table
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: allowed for c in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
