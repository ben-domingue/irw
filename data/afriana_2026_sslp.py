#!/usr/bin/env python3
# Source: https://zenodo.org/records/20568661
# DOI: 10.5281/zenodo.20568661 (data; no paper DOI on the record)
#   Afriana, J., & Permanasari, A. (2026). "Professional Development Needs of
#   School Science Laboratory Personnel: Insights From A Rasch Analysis."
#   Zenodo.
# Data: "SSLP_Raw Data 252.xlsx", 252 Indonesian school science laboratory
#   personnel x 29 competency items; SSLP_Codebook.xlsx names each item and
#   its domain (QDM quality documentation 1-7, OHS safety 8-13, WLM waste
#   14-16, CHS chemical handling 17-23, BLS basic lab skills 24-29) and the
#   1-5 agreement scale; item 21 is reverse-keyed (kept as deposited).
# License: CC BY 4.0 (Zenodo record).
# Codebook: SSLP_Codebook.xlsx in the deposit.
#
# Item text: not shipped -- the codebook gives short item descriptions, not
#   the wording; the questionnaire .docx has it, and no register row exists.
#
# Table: afriana_2026_sslp, item1-item29, 1-5, one table (the deposit's own
#   Rasch analysis treats the 29 items as one instrument).
# Covariates: cov_gender (M/F), cov_experience (codebook: 1 = <10 years,
#   2 = >=10 years). id = the deposit's respondent code (T1..T252).

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
DATA_URL = ("https://zenodo.org/api/records/20568661/files/"
            "SSLP_Raw%20Data%20252.xlsx/content")
TABLE = "afriana_2026_sslp"
ITEMS = [f"item{i}" for i in range(1, 30)]
ALLOWED = {1, 2, 3, 4, 5}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert d.shape == (252, 32), d.shape
    assert d["Teacher"].is_unique
    d["id"] = d["Teacher"].str.lstrip("T").astype(int)
    d["cov_gender"] = d["Gender"].map({"M": "male", "F": "female"})
    d["cov_experience"] = d["WorkExperience"].map({1: "<10 years",
                                                    2: ">=10 years"})
    assert d[["cov_gender", "cov_experience"]].notna().all().all()
    covs = ["cov_gender", "cov_experience"]
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
