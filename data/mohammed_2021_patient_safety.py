#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0245966
# DOI: 10.1371/journal.pone.0245966
#
# "Patient safety culture and associated factors among health care
# professionals at public hospitals in Dessie town, north east Ethiopia,
# 2019" (PLOS ONE, 2021). S1 File (SPSS .sav) contains raw item-level
# responses (5-point scale) from 411 health care professionals to the
# Hospital Survey on Patient Safety Culture (HSOPSC, 42 items across 12
# dimensions) plus a separate 5-item job satisfaction battery. The file
# also contains many derived/composite dimension scores (e.g.
# TeamworkwithinUnits, OverallPSCscoresum) which are excluded here -- only
# the 42 raw HSOPSC items and 5 raw job-satisfaction items are kept, each
# written as its own IRW file.

import os
import pandas as pd
import pyreadstat

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "automated_finding", "raw_downloads",
                    "mohammed_2021_pone0245966_s1data.sav")

HSOPSC_ITEMS = [
    "NEVERSAC", "PROCEDUR", "MISTAKES", "SAFETYPR", "MISTAKEI", "NOPOTENT",
    "HARMPATI", "GOODWORD", "POSITIVE", "PRESSURE", "DOINGTHI", "POSITIV1",
    "EVALUATE", "OVERLOOK", "SUPPORT", "WORKTOGA", "TREATEAC", "GETSBUSY",
    "FREELYSP", "EELFREE", "NOTAFRAI", "FEEDBACK", "INFORMED", "DISCUSS",
    "NOTFEELL", "EVENTRE1", "NOTWORRY", "ENOUGHST", "WORKLONG", "TEMPORAR",
    "CRISISMO", "WORKCLIM", "TOPPRIOR", "INTEREST", "COOPERAT", "TOGATHER",
    "COORDINA", "PLEASANT", "TRANSFER", "INFORMAT", "ACCROSSH", "SHIFTCHA",
]

JOBSAT_ITEMS = ["jobsat", "jobsats", "jobsatss", "jobsatsss", "jobsatssss"]

COV_RENAME = {
    "AGE": "cov_age",
    "SEX": "cov_sex",
    "PROFESSI": "cov_profession",
    "QUALIFIC": "cov_qualification",
    "UNIT": "cov_working_unit",
    "EXPERIEN": "cov_experience_years",
    "HOSPITAL": "cov_hospital",
}


def _load():
    df, meta = pyreadstat.read_sav(SRC)
    df = df.rename(columns={"ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id column is not unique per respondent"
    df = df.rename(columns=COV_RENAME)
    return df


def _write(df, item_cols, out_name, cov_cols):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]
    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]
    out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = _load()
    cov_cols = list(COV_RENAME.values())
    _write(df, HSOPSC_ITEMS, "mohammed_2021_patient_safety_culture", cov_cols)
    _write(df, JOBSAT_ITEMS, "mohammed_2021_job_satisfaction", cov_cols)


if __name__ == "__main__":
    convert()
