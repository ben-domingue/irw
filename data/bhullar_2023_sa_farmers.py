#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0265634
# DOI: 10.1371/journal.pone.0265634
# Paper: Bhullar N, Nengovhela NB, Mudau L, Villano RA, Koomson I, Burrow HM
#   (2023). Psychological profiles of South African smallholder farmers.
#   PLoS ONE 18(2): e0265634.
# Data: Figshare 10.6084/m9.figshare.19354313 (CC BY 4.0, confirmed on the
#   API record): "BCS_Final Data Beef Farmers N=471.sav" and "BCS_Final Data
#   Poultry Farmers N=426.sav", KoboToolbox survey with item wording in the
#   variable labels. The paper analyses both samples (471 beef, 426 poultry).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 6.
#
# The two samples answered the same questionnaire (identical item columns),
# so each table stacks them with cov_study = beef / poultry and ids
# prefixed "beef_" / "poultry_" (row index; the KoboID is dropped).
# SIX output tables, all 1-5:
#   bhullar_2023_expected_benefits  B1-B5, B6b, B7, B8 (8; very unlikely -
#     very likely).
#   bhullar_2023_farming_concerns  C1-C36 (36 sources of concern; the
#     paper's personal-capability and farm-related concerns). C37 write-in
#     dropped.
#   bhullar_2023_self_efficacy  D1-D8, D10-D12 (the paper's 11-item
#     adaptation of the New General Self-Efficacy Scale; no D9 deposited).
#   bhullar_2023_tpb  theory-of-planned-behaviour items: attitudes (E6b,
#     E9, E10, E12, E13), subjective norms (E1-E3), perceived behavioural
#     control (E5, E7); 10 items, the paper's three short scales.
#   bhullar_2023_bfi10  BFI-10, 10 items as answered (Fa1-Fa10; the
#     deposit's reversed copies rFa*/Fa*r are not used).
#   bhullar_2023_ztpi  ZTPI future (Fb1-Fb13) and present (Fb14-Fb21)
#     subscales, 21 items as answered (rFb6/rFb8 copies not used).
# Checks: the deposit's SUMAgreeableness equals Fa2 + reversed Fa7 on every
#   row (asserted), so the Fa2..Fa10 columns stored after the scale means
#   are raw items. 76% of beef farmers men, 54.5% of poultry farmers women
#   (paper) -- 358/471 and 232/426 here.
# Covariates: gender, age, education, race. All farm-business, household
#   and free-text questions dropped; G12 (single language item) dropped.
#
# Item text: NOT SHIPPED. Variable labels hold the full wording (CC BY);
#   the benefits and concerns items are study-written or adapted. Cheap for
#   those; BFI-10, ZTPI and NGSE are published instruments.

import io
import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
FILES = {"beef": "https://ndownloader.figshare.com/files/34376336",
         "poultry": "https://ndownloader.figshare.com/files/34376339"}
RAW = os.environ.get("BHULLAR_RAW_DIR")  # holds beef.sav, poultry.sav
HDR = {"User-Agent": "IRW-Finder/1.0"}

TABLES = {
    "expected_benefits": ["B1", "B2", "B3", "B4", "B5", "B6b", "B7", "B8"],
    "farming_concerns": [f"C{i}" for i in range(1, 37)],
    "self_efficacy": [f"D{i}" for i in range(1, 9)] + ["D10", "D11", "D12"],
    "tpb": ["E1_Norms", "E2_Norms", "E3_Norms", "E5_PBC", "E7_PBC", "E6b_Attitudes",
            "E9_Attitudes", "E10_Attitudes", "E12_Attitudes", "E13_Attitudes"],
    "bfi10": ["Fa1_extra", "Fa2_agree", "Fa3_cons", "Fa4_neuro", "Fa5_open",
              "Fa6_extra", "Fa7_agree", "Fa8_cons", "Fa9b_neuro", "Fa10_open"],
    "ztpi": [f"Fb{i}_FT" for i in range(1, 14)] + ["Fb14_PT", "Fb15_PT", "Fb16b_PT"]
            + [f"Fb{i}_PT" for i in range(17, 22)],
}
EDU = {"no_schooling": "no schooling", "primary": "primary", "seconday": "secondary",
       "high_school": "high school", "tertiary__fet_": "tertiary or FET"}


def load(study):
    if RAW:
        path = os.path.join(RAW, f"{study}.sav")
    else:
        r = requests.get(FILES[study], headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, f"_bhullar_{study}_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, _ = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df


def convert():
    parts = []
    for study, n in [("beef", 471), ("poultry", 426)]:
        d = load(study)
        assert len(d) == n, (study, len(d))
        assert (d["SUMAgreeableness"] == d["Fa2_agree"] + d["rFa7_agree"]).all()
        d["id"] = [f"{study}_{i}" for i in range(1, n + 1)]
        d["cov_study"] = study
        parts.append(d)
    df = pd.concat(parts, ignore_index=True)
    assert (df.loc[df.cov_study == "beef", "Gender"] == "male").sum() == 358
    assert (df.loc[df.cov_study == "poultry", "Gender"] == "female").sum() == 232
    df["cov_gender"] = df["Gender"]
    df["cov_age"] = df["Age"]
    df["cov_education"] = df["Education"].map(EDU)
    df["cov_race"] = df["Ethnicity"]
    covs = ["cov_study", "cov_gender", "cov_age", "cov_education", "cov_race"]

    for name, items in TABLES.items():
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        long["resp"] = long["resp"].astype(int)
        assert set(long["resp"]) <= {1, 2, 3, 4, 5}, name
        long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        checks = run_qc(long, permitted_values=[1, 2, 3, 4, 5])
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = f"bhullar_2023_{name}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
