#!/usr/bin/env python3
# Source: https://zenodo.org/records/11638469
# DOI: 10.5281/zenodo.11638469 (data); paper 10.1145/3636555.3636923
#   Frochte, J., Neugebauer, M., Tousside, B., Asatryan, H., et al. (2024).
#   "Anonymized Responses to the Student Expectation of Learning Analytics
#   Questionnaire (SELAQ) in 2022 and 2023." Zenodo.
# Data: SELAQ_Responses_2023_Germany.csv, 566 bachelor students at Bochum
#   University of Applied Sciences; column_description.csv gives each item's
#   English and German wording.
# License: CC BY 4.0 (Zenodo record).
# Codebook: column_description.csv in the deposit.
#
# Item text: not shipped -- the wording is in column_description.csv, but no
#   rights-register row exists for the SELAQ (Whitelock-Wainwright et al.).
#
# Tables (SELAQ, 1-7 strongly disagree .. strongly agree; its two scales):
#   frochte_2024_selaq_ideal      1D..12D  ("Ideally, I would like this")
#   frochte_2024_selaq_predicted  1E..12E  ("I expect this to happen")
# Covariates: cov_study_track (as deposited), cov_semester (the free-text
#   semester where it is a whole number 1-20, else NA). id = SurveyID.

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
DATA_URL = ("https://zenodo.org/api/records/11638469/files/"
            "SELAQ_Responses_2023_Germany.csv/content")
ALLOWED = set(range(1, 8))
SPEC = {"frochte_2024_selaq_ideal": "D", "frochte_2024_selaq_predicted": "E"}


def sem(v):
    s = str(v).strip()
    return int(s) if s.isdigit() and 1 <= int(s) <= 20 else pd.NA


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content), dtype={"Semester": str})
    assert d.shape == (566, 27), d.shape
    assert d["SurveyID"].is_unique
    d["id"] = d["SurveyID"].astype(int)
    d["cov_study_track"] = d["Study_Track"]
    d["cov_semester"] = d["Semester"].map(sem).astype("Int64")
    covs = ["cov_study_track", "cov_semester"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, s in SPEC.items():
        items = [f"{i}{s}" for i in range(1, 13)]
        long = d.melt(id_vars=["id"] + covs, value_vars=items,
                      var_name="item", value_name="resp").dropna(
                          subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        assert not set(long["resp"]) - ALLOWED
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: ALLOWED for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        (OUT_DIR / f"{table}.csv").write_text(long.to_csv(index=False))
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
