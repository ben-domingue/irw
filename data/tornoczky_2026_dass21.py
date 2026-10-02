#!/usr/bin/env python3
# Source: https://zenodo.org/records/22031833
# DOI: none found (Zenodo deposit only; no related identifier on the record,
#   and Crossref title/author searches found no paper as of 2026-10-02).
#   Tornóczky, G. J., & Szabo, A. (2026). "Validation of the 21 item
#   Hungarian Depression, Anxiety, and Stress Scale." Zenodo.
# Data: Zenodo 22031833, DASS21_HU_N782_Clean.xlsx, sheet "Data" (782 rows x
#       67 columns; Hungarian adults, Qualtrics online survey). The workbook
#       also carries a "Codebook" and a "Notes" sheet; the response ranges
#       below are taken from that codebook.
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text: not shipped. The data sheet has plain headers (dass_01 ..
#   panas_na_20) and no value labels; the Codebook sheet describes each
#   block ("DASS-21 items, standard item order", PANAS PA/NA item numbers)
#   but gives no stems. The wording is in the published Hungarian DASS-21,
#   WHO-5, SWLS and PANAS.
#
# Tables (item codes are the source column names; ranges from the deposit's
# Codebook sheet):
#   tornoczky_2026_dass21  dass_01-dass_21, 0-3 (0 = did not apply at all).
#                          Standard DASS-21 item order. Exported by Qualtrics
#                          as 1-4 and recoded to 0-3 by the depositors
#                          (Notes sheet).
#   tornoczky_2026_who5    who5_1-who5_5, 0-3. NOTE: administered on a
#                          4-point scale (Qualtrics 1-4, recoded 0-3), not the
#                          WHO-5's standard 6-point 0-5 format.
#   tornoczky_2026_swls    swls_1-swls_5, 1-7.
#   tornoczky_2026_panas   20 items, 1-5: panas_pa_nn (positive affect,
#                          items 1,3,5,9,10,12,14,16,17,19) and panas_na_nn
#                          (negative affect, items 2,4,6,7,8,11,13,15,18,20).
#                          Kept as one table, the instrument as administered.
#
# Cleaning: none needed -- no missing item cells (the depositors' case
#   selection kept only complete DASS/WHO-5/SWLS/PANAS records), all values
#   whole and inside the documented sets.
# Dropped: dass_depression, dass_anxiety, dass_stress, dass_total,
#   who5_total, swls_total, panas_pa, panas_na (live SUM formulas over the
#   items); age_group and partnered (derived from age / marital_status,
#   per the codebook).
# id: row index. participant_id ("P001".."P782") is a sequential code the
#   depositors assigned during cleaning; it equals the row order (asserted)
#   and is replaced. The depositors removed IP, GPS, Qualtrics response IDs,
#   timestamps and free text before deposit (Notes sheet); none remain.
# Covariates: cov_sex (1 male, 2 female), cov_age, cov_marital_status
#   (1 single, 2 in a relationship, 3 married, 4 divorced, 5 widowed,
#   6 other), cov_education (1 primary or vocational, 2 secondary,
#   3 tertiary, 4 doctoral), cov_residence (1 capital, 2 large city, 3 town,
#   4 small town, 5 village).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/22031833/files/"
       "DASS21_HU_N782_Clean.xlsx/content")

PA = (1, 3, 5, 9, 10, 12, 14, 16, 17, 19)
PANAS = [f"panas_{'pa' if i in PA else 'na'}_{i:02d}" for i in range(1, 21)]
TABLES = {
    "tornoczky_2026_dass21": ([f"dass_{i:02d}" for i in range(1, 22)],
                              range(0, 4)),
    "tornoczky_2026_who5": ([f"who5_{i}" for i in range(1, 6)], range(0, 4)),
    "tornoczky_2026_swls": ([f"swls_{i}" for i in range(1, 6)], range(1, 8)),
    "tornoczky_2026_panas": (PANAS, range(1, 6)),
}
COMPOSITES = {"dass_depression", "dass_anxiety", "dass_stress", "dass_total",
              "who5_total", "swls_total", "panas_pa", "panas_na"}
DERIVED = {"age_group", "partnered"}
COVS = {"sex": "cov_sex", "age": "cov_age",
        "marital_status": "cov_marital_status",
        "education": "cov_education", "residence": "cov_residence"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        return pd.read_excel(path, sheet_name="Data")
    finally:
        os.unlink(path)


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = load()
    assert d.shape == (782, 67), d.shape

    # Balance the books.
    items = {c for its, _ in TABLES.values() for c in its}
    known = items | COMPOSITES | DERIVED | set(COVS) | {"participant_id"}
    assert set(d.columns) == known, set(d.columns) ^ known
    assert list(d["participant_id"]) == [f"P{i:03d}" for i in
                                         range(1, 783)]
    assert ((d["age"] >= 26) + 1 == d["age_group"]).all()
    assert (d["partnered"] == d["marital_status"].isin([2, 3])
            .astype(int)).all()

    d = d.drop(columns=["participant_id"]).reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, allowed) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        assert long["resp"].notna().all()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        allowed = set(allowed)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
