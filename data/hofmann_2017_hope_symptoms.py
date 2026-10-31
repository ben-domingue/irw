#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0179415
# DOI: 10.1371/journal.pone.0179415
# Paper: Hofmann, S., Hess, S., Klein, C., Lindena, G., Radbruch, L., &
#   Ostgathe, C. (2017). Patients in palliative care -- Development of a
#   predictive model for anxiety using routine data. PLOS ONE 12(8): e0179415.
# Data: journal.pone.0179415.s001 (S1 File, "HOPE core data set 2007-2011",
#   .sav). 9,924 adult patients at admission to German palliative care
#   services (units, hospices, hospital wards, outpatient services), 2007-2011,
#   from the Hospice and Palliative Care Evaluation (HOPE) benchmarking system.
# License: CC BY 4.0 (the article; the data is its own Supporting Information
#   file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30, worked from
# leads/plos_leads_2026-10-30.csv on 2026-10-31 (BATCH_LOG.md).
#
# ONE output table, hofmann_2017_hope_symptoms: the 15 symptom-and-problem
# items of the HOPE core data set, each rated 0-3 at admission BY THE CARE
# TEAM, not the patient (`rater` is "care_team" on every row; sample tagged
# Observational rating). The 15: pain, nausea, vomiting, dyspnea, constipation,
# weakness, loss of appetite, tiredness, wound care, assistance with ADL,
# organization of care, feeling depressed, anxiety, tension,
# disorientation/confusion -- i.e. the HOPE symptom checklist's physical,
# nursing and psychological problems.
#
# WHAT 0 MEANS, AND WHY IT SHIPS. The .sav's value labels on every one of the
# 15 are {0: 'no data', 1: 'yes'}, which cannot be the coding of a column that
# takes 0, 1, 2 and 3. The paper's Methods settle it: "Symptom scores of
# anxiety were dichotomized into none or mild intensity versus moderate or
# severe intensity", i.e. the HOPE four-step rating none/mild/moderate/severe
# = 0/1/2/3. Two further facts separate 0 from "no data": every item has a
# distinct missing state (pain is NaN on 73 rows, organization_of_care on
# 439), so absence is already expressed as NaN; and 0 is the modal value on
# the rarer symptoms (vomiting 0 on 78%) and a minority on the common ones
# (weakness 0 on 12%), which is the shape of "none" and not of a
# documentation gap. The value labels are the deposit's template label for its
# yes/no medication columns applied to the wrong block, and the description
# says so. Rows missing an item are simply absent for that item.
#
# Not shipped: the 15 medication columns (-1/1 yes/no, "non or no data"), the
# demographic and clinical columns other than those below, and nothing else --
# there are 40 columns in all.
#
# `id` is the row index (one admission per row, no patient id in the file).
#
# Covariates: gender (deposit labels), age at admission in whole years (the
# file carries a fractional age; floored -- a fractional age is not
# identifying in a 9,924-patient national pool and the integer is what a user
# wants), ECOG performance status 0-4, living situation, type of palliative
# care service, cancer vs non-cancer disease, brain metastases, level of
# nursing-care support. The deposit's -1/999 'no data' codes become NaN.
#
# Item text: NOT SHIPPED. Both label levels were read: the variable labels are
# the bare symptom names ("pain", "nausea", "loss_appetite") and the value
# labels are the wrong template (see above), so neither carries the HOPE
# checklist's administered wording. The HOPE core documentation (hope-clara.de)
# is where the German item wording lives; a hold rather than a rights ruling.

import os
import sys

import numpy as np
import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("HOFMANN_RAW", "S1_File.sav")
N_ROWS = 9924
NAME = "hofmann_2017_hope_symptoms"

ITEMS = ["pain", "nausea", "vomiting", "dyspnea", "constipation", "weakness",
         "loss_appetite", "tiredness", "wound_care", "assistance_adl",
         "organization_of_care", "feeling_depressed", "anxiety", "tension",
         "disorientation_confusion"]
MEDS = ["non_opioids", "WHO_2", "WHO_3", "co_analgetics", "sedatives_anxiolytics",
        "antidepressants", "neuroleptics", "antiemetics", "corticosteroids", "cardiacs",
        "gastric_protection", "laxatives", "antibiotics", "diuretics", "other_drugs"]


def na_codes(s, codes):
    return s.where(~s.isin(codes))


def convert():
    df, meta = pyreadstat.read_sav(RAW, apply_value_formats=False)
    assert len(df) == N_ROWS and len(df.columns) == 40, df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} of {len(df.columns)} columns are text: {txt}")
    assert not txt, "unexpected text column"
    vl = meta.variable_value_labels
    for c in ITEMS:
        assert vl[c] == {0.0: "no data", 1.0: "yes"}, (c, vl[c])   # the mislabel the header explains
        assert set(df[c].dropna().unique()) == {0, 1, 2, 3}, (c, df[c].unique())
    for c in MEDS:
        assert set(df[c].unique()) == {-1, 1}, c
    print("modal share of 0:", {c: round((df[c] == 0).mean(), 2) for c in ("vomiting", "weakness", "anxiety")})
    print("missing per item:", {c: int(df[c].isna().sum()) for c in ITEMS})

    df["id"] = range(1, N_ROWS + 1)
    cov = pd.DataFrame({
        "id": df["id"],
        "cov_gender": na_codes(df["gender"], [-1]).map({1: "female", 2: "male"}),
        "cov_age": np.floor(df["age"]),
        "cov_ecog": na_codes(df["ECOG"], [-1]),
        "cov_living_situation": na_codes(df["living_situation"], [-1]).map(
            {1: "alone", 2: "nursing_home", 3: "with_relatives", 4: "other"}),
        "cov_service_type": df["pal_care_service"].map(
            {1: "palliative_care_unit", 2: "hospital_other_unit", 3: "hospice", 4: "outpatient_service"}),
        "cov_cancer": df["Type_disease"].map({1: 1, 2: 0}),
        "cov_brain_tumor": df["brain_metastases"].astype(int),
        "cov_nursing_care_level": na_codes(df["level_nursing_care_support"], [999]),
    })
    assert abs((cov["cov_gender"] == "female").mean() - 0.519) < 0.01   # paper: 51.9% female
    assert abs(df["age"].mean() - 68.8) < 0.1                            # paper: mean 68.8
    cov["cov_age"] = cov["cov_age"].astype("Int64")
    cov_cols = [c for c in cov.columns if c != "id"]

    wide = df[["id"] + ITEMS]
    long = wide.melt(id_vars=["id"], value_vars=ITEMS, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long.merge(cov, on="id", how="left")
    long["rater"] = "care_team"
    long = long[["id", "item", "resp"] + cov_cols + ["rater"]]
    assert long["id"].nunique() == N_ROWS and long["item"].nunique() == 15
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [0, 1, 2, 3] for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items=15 resp=0-3")
    dropped = [c for c in df.columns if c not in ITEMS and c != "id"]
    print(f"{len(dropped)} non-item columns: {dropped}")


if __name__ == "__main__":
    convert()
