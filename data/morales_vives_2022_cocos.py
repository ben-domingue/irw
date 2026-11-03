#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0262698
# DOI: 10.1371/journal.pone.0262698
# Paper: Morales-Vives, F., Dueñas, J.-M., Ferrando, P. J., Vigil-Colet, A., &
#   Varea, M. D. (2022). COmpliance with pandemic COmmands Scale (COCOS): The
#   relationship between compliance with COVID-19 measures and
#   sociodemographic and attitudinal variables. PLOS ONE 17(1): e0262698.
# Data: Zenodo 10.5281/zenodo.5828250, file data_zenodo.sav: 1,410 residents
#   of Spain aged 15-76 (28% adolescents 15-17), 2021.
# License: CC BY 4.0, verified ON THE DEPOSIT (Zenodo record metadata
#   license id cc-by-4.0); the article is also CC BY 4.0.
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# ONE output table, morales_vives_2022_cocos: COCOS_1..COCOS_27, the 27-item
# COCOS developed in this study, "27 Likert-type items with five response
# options (1 = completely disagree to 5 = completely agree)". Shipped as
# deposited. COCOS_aquiescence and COCOS_factor1 are derived scores, not
# shipped.
#
# Covariates (all from the .sav value labels): age, sex (Man / Woman; "I
# prefer not to say" -> missing; 835 of 1,410 = 59.2% women, the paper's
# figure), civil status, has children, household income band, vaccinated,
# had COVID-19, chronic disease. Not shipped: Intention_vaccination and
# Severe_simptoms (asked conditionally), Optimism (a single 0-10 rating), and
# the 14 binary attitude/information-source questions (Mask .. Other_channels)
# -- the paper analyses them as separate predictors, not as a scale.
#
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. The .sav has no variable or value labels on any
#   COCOS item (both levels checked; covariates are labelled); the 27 Spanish
#   items are printed in the article only as a table image.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("COCOS_RAW", "data_zenodo.sav")
NAME = "morales_vives_2022_cocos"
N_ROWS = 1410


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 54 and txt == []
    items = [f"COCOS_{i}" for i in range(1, 28)]
    vl = meta.variable_value_labels
    assert not any(meta.column_names_to_labels.get(c) or c in vl for c in items)
    assert int((df["Sex"] == 2).sum()) == 835

    df["id"] = range(1, N_ROWS + 1)
    yn = {0.0: "no", 1.0: "yes"}
    cov = {
        "cov_age": df["Age"],
        "cov_sex": df["Sex"].map({1.0: "man", 2.0: "woman"}),
        "cov_civil_status": df["Civil_status"].map(vl["Civil_status"]),
        "cov_children": df["Children"].map(yn),
        "cov_household_income_eur": df["Incomes"].map(vl["Incomes"]),
        "cov_vaccinated": df["Vaccinated"].map(yn),
        "cov_had_covid": df["Infected_COVID"].map(yn),
        "cov_chronic_disease": df["Chronic_disease"].map(yn),
    }
    assert vl["Sex"][3.0] == "I prefer not to say"
    assert vl["Incomes"][5.0] == "Más de 5500"
    for k, v in cov.items():
        df[k] = v
    cov_cols = list(cov)
    long = df[["id"] + cov_cols + items].melt(id_vars=["id"] + cov_cols, var_name="item",
                                              value_name="resp")
    assert long["resp"].notna().all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) == {1, 2, 3, 4, 5}
    long = long[["id", "item", "resp"] + cov_cols]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: [1, 2, 3, 4, 5] for c in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    cov_src = {"Age", "Sex", "Civil_status", "Children", "Incomes", "Vaccinated", "Infected_COVID",
               "Chronic_disease"}
    dropped = [c for c in meta.column_names if c not in set(items) | cov_src]
    print(f"dropped {len(dropped)}: {dropped}")
    assert len(dropped) == 54 - 27 - 8
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
