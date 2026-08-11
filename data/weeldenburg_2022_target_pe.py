#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0274964
# DOI: 10.1371/journal.pone.0274964
# SI file (S1 Dataset): https://doi.org/10.1371/journal.pone.0274964.s001
# SI questionnaire (S1 Questionnaire, MTP-Q text): https://doi.org/10.1371/journal.pone.0274964.s002
#
# Weeldenburg G, Borghouts L, Laak Tvd, Remmers T, Slingerland M, Vos S
# (2022) TARGETing secondary school students' motivation towards physical
# education: Extending the TARGET framework. PLoS ONE 17(9): e0274964.
#
# Two distinct, well-documented instruments are in the raw .sav file and
# shipped here as separate tables:
#
#  1. Mastery Teaching Perception Questionnaire (MTP-Q) -- 26 items across
#     five TARGET-framework subscales (Task 6, Authority 5, Recognition 5,
#     Grouping 5, Evaluation 5), 5-point Likert (1=strongly disagree,
#     5=strongly agree). Shipped as one table (weeldenburg_2022_targetmtpq).
#  2. Behavioural Regulations in PE Questionnaire (BRPEQ, modified 12-item
#     version) -- autonomous motivation (IntrinsicMot 2, IdentifiedReg 2),
#     controlled motivation (IntrojectedReg 2, ExternalReg 2), and
#     amotivation (4 items). Same 5-point Likert scale. Shipped as
#     weeldenburg_2022_brpeq_motivation.
#
# `Respondent` is the true per-student identifier (verified unique,
# nunique()==len(df)=3150) -- NOT `School`/`Leraar`(teacher)/`Niveau`, which
# are group-level covariates, resolving the retriage low-confidence-id flag.
#
# Excluded entirely (no documented mapping in the paper's Methods/SI
# questionnaire text): AUT_mean/CONT_mean/AMOT_mean/TASK_mean/AUTH_mean/
# RECOG_mean/GROU_mean/EVAL_mean/TARGET_score (all composite means, not raw
# responses), QCL_2/QCL_3/TSC_2/TSC_3 (undocumented, ambiguous), the
# onderwijsniveau_*/leerjaar_* dummy-encoded duplicates of Niveau/Leerjaar,
# filter_$ (SPSS housekeeping var), and interact.* (pairwise interaction
# terms among subscale means -- derived, not raw).

import os

import pandas as pd
import pyreadstat

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SRC_URL = ("https://journals.plos.org/plosone/article/file"
           "?id=10.1371/journal.pone.0274964.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

MTPQ_PREFIXES = ["Task_", "Authority_", "Recognition_", "Grouping_", "Evaluation_"]
BRPEQ_PREFIXES = ["IntrinsicMot_", "IdentifiedReg_", "IntrojectedReg_", "ExternalReg_", "Amotivation_"]

COV_RENAME = {
    "School": "cov_school",
    "Leraar": "cov_teacher",
    "Geslacht": "cov_gender",
    "Leeftijd": "cov_age",
    "Niveau": "cov_education_level",
    "Leerjaar": "cov_grade_year",
}


def fetch_raw() -> pd.DataFrame:
    import tempfile

    import requests

    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    df, _meta = pyreadstat.read_sav(path)
    os.remove(path)
    return df


def build_scale(df: pd.DataFrame, cov_names: list, prefixes: list) -> pd.DataFrame:
    item_cols = [c for c in df.columns if any(c.startswith(p) for p in prefixes)]
    long = df.melt(
        id_vars=["id"] + cov_names,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)
    out_cols = ["id", "item", "resp"] + cov_names
    return long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    raw = fetch_raw()

    raw = raw.rename(columns={"Respondent": "id"})
    assert raw["id"].nunique() == len(raw), "Respondent is not a unique person id"

    raw = raw.rename(columns=COV_RENAME)
    cov_names = list(COV_RENAME.values())

    mtpq = build_scale(raw, cov_names, MTPQ_PREFIXES)
    out_name1 = "weeldenburg_2022_targetmtpq.csv"
    mtpq.to_csv(os.path.join(OUT_DIR, out_name1), index=False)
    print(f"{out_name1}: rows={len(mtpq)} ids={mtpq['id'].nunique()} "
          f"items={mtpq['item'].nunique()} resp={mtpq['resp'].min():.0f}-{mtpq['resp'].max():.0f}")

    brpeq = build_scale(raw, cov_names, BRPEQ_PREFIXES)
    out_name2 = "weeldenburg_2022_brpeq_motivation.csv"
    brpeq.to_csv(os.path.join(OUT_DIR, out_name2), index=False)
    print(f"{out_name2}: rows={len(brpeq)} ids={brpeq['id'].nunique()} "
          f"items={brpeq['item'].nunique()} resp={brpeq['resp'].min():.0f}-{brpeq['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
