#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0344126
# DOI: 10.1371/journal.pone.0344126
# Development and psychometric validation of the insect fear questionnaire
# for school-aged children in Iran (Latifi et al., PLOS ONE 2026)
# SI: journal.pone.0344126_S1_Dataset.sav (S2 in article numbering), CC BY 4.0

import os

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0344126.s002"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Q4_Location": "cov_location",
    "Q5_Grade": "cov_grade",
    "Q6_Education_area": "cov_education_area",
    "Q7_schooltype": "cov_schooltype",
    "Q8_Going_school": "cov_going_school",
    "Q9_Age": "cov_age",
    "Q10_Gender": "cov_gender",
    "Q11_Jobfather": "cov_job_father",
    "Q12_Jobmother": "cov_job_mother",
    "Q13_FatherEducation": "cov_education_father",
    "Q14_MotherEducation": "cov_education_mother",
    "Q15_Number_children": "cov_num_children",
    "Q16_Rank_child": "cov_rank_child",
    "Q17_Fobia_family": "cov_family_phobia",
    "Q18_how_fear": "cov_how_fear",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp_path = "/tmp/_latifi_2026_s1.sav"
    with open(tmp_path, "wb") as f:
        f.write(r.content)
    df, _ = pyreadstat.read_sav(tmp_path)
    os.remove(tmp_path)
    return df


def convert():
    df = fetch_data()

    df = df.rename(columns={"ID": "id"})
    assert df["id"].nunique() == len(df), "id column not unique"

    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    item_cols = [f"Q{i}" for i in range(1, 33)]
    assert all(c in df.columns for c in item_cols)

    long = df.melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    # Insect Fear Questionnaire is scored 1-5; check per-item distribution
    # for out-of-range/sentinel values before finalizing.
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "latifi_2026_insect_fear.csv")
    long.to_csv(out_path, index=False)
    print(f"latifi_2026_insect_fear.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
