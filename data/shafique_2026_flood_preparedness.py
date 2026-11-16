#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Data_and_materials_for_Risk_Governance_and_Public_Participation_as_Pathways_to_Household_Disaster_Preparedness_Behavior_A_Mediation_Analysis_of_Institutional_Trust_and_Community_Resilience_in_Rural_Pakistan/34874724
# DOI: 10.6084/m9.figshare.34874724.v2 (data; no paper DOI on the record)
#   Shafique Z (2026). Data and materials for: Risk Governance and Public
#   Participation as Pathways to Household Disaster Preparedness Behavior.
#   figshare.
# Data: Jalalpur_Pirwala_2025_Flood_Data.xlsx (370 households x 57 columns),
#   enumerator-administered after the 2025 floods in Jalalpur Pirwala,
#   Punjab, Pakistan. The deposit's other workbooks are PLS-SEM/fsQCA/NCA
#   outputs.
# License: CC BY 4.0 (figshare record).
# Codebook: "Full Questionnaire Flood.docx" (bilingual English/Urdu; screening,
#   demographics and every scale item with its code; 1 = strongly disagree ..
#   5 = strongly agree).
#
# Counts: 370 rows; no N stated on the record, so not checked against a source.
# Tables (1-5, codes as in the questionnaire):
#   shafique_2026_risk_governance         PRGQ1-5  perceived risk governance quality
#   shafique_2026_public_participation    PP1-5
#   shafique_2026_institutional_trust     IT1-5
#   shafique_2026_community_resilience    CR1-6
#   shafique_2026_preparedness_behavior   HDPB1-6  household disaster preparedness
# id = Sr No. (1-370, unique).
# Not shipped: UC_Area (union council) and Flood_Severity_Zone (geographic codes,
#   dropped per the 2026-10-20 ruling); the flood-exposure, warning, housing and
#   access questions (single items, not scales).
# Covariates: gender, age group, marital status, education, occupation,
#   household income band, household size band, vulnerable members (text
#   categories as deposited).
# Item text: not shipped -- English and Urdu wording is in the questionnaire
#   docx; study-authored items, left for an itemtext pass.

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
DATA_URL = "https://ndownloader.figshare.com/files/70942704"
SPEC = {
    "shafique_2026_risk_governance": ("PRGQ", 5),
    "shafique_2026_public_participation": ("PP", 5),
    "shafique_2026_institutional_trust": ("IT", 5),
    "shafique_2026_community_resilience": ("CR", 6),
    "shafique_2026_preparedness_behavior": ("HDPB", 6),
}
COVS = {"Gender": "cov_gender", "Age_Group": "cov_age_group",
        "Marital_Status": "cov_marital_status", "Education": "cov_education",
        "Occupation": "cov_occupation",
        "Monthly_Household_Income": "cov_household_income",
        "Household_Size": "cov_household_size",
        "Vulnerable_Members": "cov_vulnerable_members"}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Data")
    assert d.shape == (370, 57), d.shape
    assert d["Sr No."].is_unique
    d = d.drop(columns=["UC_Area", "Flood_Severity_Zone"])
    d = d.rename(columns={"Sr No.": "id", **COVS})
    covs = list(COVS.values())
    allowed = set(range(1, 6))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for table, (pre, n) in SPEC.items():
        cols = [f"{pre}{i}" for i in range(1, n + 1)]
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
