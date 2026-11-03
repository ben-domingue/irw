#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0173295
# DOI: 10.1371/journal.pone.0173295
# Paper: Leal-Soto, F., & Ferrer-Urbina, R. (2017). Three-factor structure for
#   Epistemic Belief Inventory: A cross-validation study. PLOS ONE 12(3):
#   e0173295.
# Data: journal.pone.0173295.s002 (S1 File, "Data set", .sav), 1,785 Chilean
#   secondary and university students from Iquique and Arica.
# License: CC BY 4.0 (the article; the data is its own Supporting
#   Information file).
#
# Found by the PLOS recycled-terms discovery pass of 2026-10-30
# (recoverable_format, column-selection sub-bucket), worked from
# leads/plos_leads_2026-10-30.csv on 2026-11-02 (BATCH_LOG.md).
#
# ONE output table, leal_soto_2017_ebi: ce1..ce28, the 28-item Epistemic
# Belief Inventory (Schraw, Bendixen & Dunkle 2002) in Spanish, 1-5. Every
# item column carries the variable label "Creencias epistemológicas"
# (epistemic beliefs); no value labels. Items are shipped as deposited.
# ce2Rec and ce22Rec are the deposit's own reverse-scored copies of ce2 and
# ce22 (each equals 6 - original on every row) and are not shipped.
#
# Covariates: age (edad), sex (sexo: 1 Hombre / 2 Mujer, value labels) and
# city of data collection (origen: 1 Iquique / 2 Arica, value labels).
# `submuestra` is the deposit's random ~40% split-half flag for cross-
# validation, not a respondent attribute; dropped.
#
# `id` is the row index (the deposit has no id column).
#
# Item text: NOT SHIPPED. The .sav carries one generic variable label on all
#   28 items and no value labels (both levels checked); the Spanish stems are
#   not in the article or its SI. The EBI is a named published instrument.

import os
import sys

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LEAL_RAW", "journal.pone.0173295.s002.sav")
NAME = "leal_soto_2017_ebi"
N_ROWS = 1785


def convert():
    df, meta = pyreadstat.read_sav(RAW)
    assert len(df) == N_ROWS
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) == 34 and txt == []
    items = [f"ce{i}" for i in range(1, 29)]
    vl = meta.variable_value_labels
    assert vl["sexo"] == {1.0: "Hombre", 2.0: "Mujer"} and vl["origen"] == {1.0: "Iquique", 2.0: "Arica"}
    assert all(c not in vl for c in items)
    assert (df["ce2Rec"] == 6 - df["ce2"]).all() and (df["ce22Rec"] == 6 - df["ce22"]).all()

    df["id"] = range(1, N_ROWS + 1)
    df["cov_age"] = df["edad"]
    df["cov_sex"] = df["sexo"].map({1.0: "male", 2.0: "female"})
    df["cov_city"] = df["origen"].map({1.0: "Iquique", 2.0: "Arica"})
    cov_cols = ["cov_age", "cov_sex", "cov_city"]
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
    accounted = set(items) | {"edad", "sexo", "origen", "submuestra", "ce2Rec", "ce22Rec"}
    assert set(meta.column_names) == accounted
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}; "
          "dropped submuestra, ce2Rec, ce22Rec")


if __name__ == "__main__":
    convert()
