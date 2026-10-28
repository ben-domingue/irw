#!/usr/bin/env python3
# Source: https://zenodo.org/records/22744099
# DOI: 10.5281/zenodo.22744099
# Deposit: Rumangkit, S. (2026). Dataset Questionnaire Ecotourism Experiences,
#   Ecotourism Satisfaction, and Ecotourism Intention [Dataset]. Zenodo.
# Data: Dataset_Ecotourism Experience and Integrated Marketing
#   Communication_AJHTL.xlsx, sheet "Raw_Data_100_Respondents"
# License: CC BY 4.0 (stated on the Zenodo deposit page)
#
# Four batteries on one five-point agreement scale, from the same 100
# respondents: ecotourism experience (ECE, 5 items), integrated marketing
# communication (IMC, 5), ecotourism satisfaction (ECS, 4) and ecotourism
# intention (ECI, 4). Shipped as four tables, one per construct.
#
# Item text: NOT shipped. The deposit is a single spreadsheet with no
# questionnaire, codebook or README, the item codes are positional
# (ECE1..ECE5), and no publication is linked from the record -- only the
# file name points at one (AJHTL, the African Journal of Hospitality, Tourism
# and Leisure). So the wording is in that paper, wherever it appears, and
# nothing in this deposit carries it.
#
# N is exactly 100, the floor, and the scales are 4-5 items: thin but inside
# the rules. No duplicate response rows; within-battery correlations run
# 0.54-0.63 and between-battery correlations are near zero.
#
# PII: screened, clean. The demographic columns are banded (age group, income
# band, occupation category), and Respondent_ID is a sequential survey number.

import os
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

RAW = os.environ.get("RUMANGKIT_RAW",
                     "Dataset_Ecotourism Experience and Integrated Marketing Communication_AJHTL.xlsx")

COVS = {
    "Gender": "cov_gender",
    "Age_Group": "cov_age_group",
    "Occupation": "cov_occupation",
    "Monthly_Income": "cov_monthly_income",
    "Ecotourism_Type": "cov_ecotourism_type",
}

TABLES = {
    "rumangkit_2026_ecotourism_experience": "ECE",
    "rumangkit_2026_ecotourism_imc": "IMC",
    "rumangkit_2026_ecotourism_satisfaction": "ECS",
    "rumangkit_2026_ecotourism_intention": "ECI",
}
EXPECTED = {"ECE": 5, "IMC": 5, "ECS": 4, "ECI": 4}


def convert():
    df = pd.read_excel(RAW, sheet_name="Raw_Data_100_Respondents")
    assert df["Respondent_ID"].nunique() == len(df), "Respondent_ID not unique"
    df = df.rename(columns={"Respondent_ID": "id", **COVS})
    cov_cols = sorted(COVS.values())

    groups = {name: [c for c in df.columns if c.startswith(pre)]
              for name, pre in TABLES.items()}
    for name, cols in groups.items():
        assert len(cols) == EXPECTED[TABLES[name]], (name, cols)

    item_cols = {c for cols in groups.values() for c in cols}
    accounted = item_cols | set(COVS.values()) | {"id"}
    left_out = [c for c in df.columns if c not in accounted]
    assert not left_out, f"unaccounted columns: {left_out}"

    os.makedirs(OUT_DIR, exist_ok=True)
    written = set()
    for name, cols in sorted(groups.items()):
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert long["resp"].between(1, 5).all(), (name, long["resp"].unique())
        long["resp"] = long["resp"].astype(int)
        assert name not in written and len(name) <= 40, name
        written.add(name)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
