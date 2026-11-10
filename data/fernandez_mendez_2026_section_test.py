#!/usr/bin/env python3
# Source: https://zenodo.org/records/21060533
# DOI (data): 10.5281/zenodo.21060533
# Data: Fernandez-Mendez, L. M., Prieto, G., Rodan, A., Contreras, M. J., &
#   Diaz Gil, G. (2026). Dataset Section test. Rasch Analysis of a Section
#   Test in Health Science Students. Zenodo. "Datos TS.xlsx" (sheet Hoja1).
#   No article is linked from the record (checked 2026-11-10).
# License: CC BY 4.0, verified on the Zenodo record.
#
# Found by the second repos sweep of 2026-11-10 (lane C; triage flag good).
#
# ONE output table:
#   fernandez_mendez_2026_section_test  TS1..TS20, a 20-item multiple-choice
#     section (cross-section visualisation) test, scored 0/1 by the
#     depositors (TS<k>); resp_raw = the option chosen (TSo<k>, A-E; the
#     deposit misnames item 2's raw column "TS02"). Each item's correct
#     option is unambiguous from the data (every chooser of one letter is
#     scored 1, everyone else 0) except one cell: on TS11, 1 of the 10
#     students who chose D is scored correct. It ships as the depositors
#     scored it. The item sum equals the deposit's "TS Aciertos" on 318 of
#     321 rows (13 blank cells).
# Covariates: degree programme (code as deposited), age, gender (M = mujer,
#   H = hombre, O = other, shipped as female/male/other), handedness (D/Z/A
#   as deposited; "No contesta" left empty).
# `id` is the deposit's nº.
#
# Item text: NOT SHIPPED. The test figures are not deposited.

import os
import sys

import numpy as np
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")


def write(d, items, permitted, name, covs, codes=None, drop_values=()):
    codes = codes or items
    sub = d[["id"] + covs + items].rename(columns=dict(zip(items, codes)))
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    rawl = d[["id"] + RAWCOLS].rename(columns=dict(zip(RAWCOLS, codes))).melt(
        id_vars="id", var_name="item", value_name="resp_raw")
    rawl["resp_raw"] = rawl["resp_raw"].astype("string").str.strip()
    long = long.merge(rawl, on=["id", "item"], how="left", validate="one_to_one")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long[~long["resp"].isin(drop_values)]
    assert (long["resp"] == np.floor(long["resp"])).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(permitted), set(long["resp"])
    long = long[["id", "item", "resp", "resp_raw"] + covs]
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: permitted for c in codes})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")

RAW = os.environ.get("FERNANDEZ_RAW", "Datos TS.xlsx")
RAWCOLS = ["TSo1", "TS02"] + [f"TSo{k}" for k in range(3, 21)]


def convert():
    d = pd.read_excel(RAW)
    assert d.shape == (321, 46) and d["nº"].is_unique
    items = [f"TS{k}" for k in range(1, 21)]
    d["id"] = d["nº"]
    d["cov_programme"] = d["Titulación"]
    d["cov_age"] = pd.to_numeric(d["Edad"], errors="coerce")
    d["cov_gender"] = d["Género"].map({"M": "female", "H": "male", "O": "other"})
    d["cov_handedness"] = d["Lateralidad"].where(d["Lateralidad"] != "No contesta")
    write(d, items, [0, 1], "fernandez_mendez_2026_section_test",
          ["cov_programme", "cov_age", "cov_gender", "cov_handedness"])


if __name__ == "__main__":
    convert()
