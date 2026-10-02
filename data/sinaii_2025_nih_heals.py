#!/usr/bin/env python3
# Source: https://zenodo.org/records/14806363
# DOI: 10.1371/journal.pmen.0000276
#   Vocci, M. C., Bagereka, P., Ameli, R., ... Sinaii, N. (2025).
#   "Development of the National Institute of Health Healing Experience of
#   All Life Stressors Short Form (NIH-HEALS-SF)." PLOS Mental Health.
#   Deposit: Sinaii, N. & National Institutes of Health (2025). "Development
#   and Psychometric Analysis of the NIH-HEALS Short Form." Zenodo.
#   Sample 1 is the 200-patient NIH-HEALS validation sample of Ameli et al.
#   (2018), PLOS ONE, 10.1371/journal.pone.0207820.
# Data: Zenodo 14806363, "BERGER- HEALS short form data for PLOS Mental
#       Health.xlsx", sheet "FOR ANALYSIS" (364 rows x 48 columns); sheet
#       "DATA DICTIONARY" documents every column.
# License: CC BY 4.0 (Zenodo record metadata). The article is CC0.
#
# Item text: not shipped. Both label levels checked: an .xlsx has no
#   variable or value labels; the deposit's DATA DICTIONARY sheet gives only
#   the response anchors, and points to the paper's appendix for the items.
#   The 35 NIH-HEALS stems are printed in Ameli et al. (2018, PLOS ONE,
#   CC BY) -- a paper_order mapping to q1..q35, so not cheap.
#
# Table (item codes are the source column names):
#   sinaii_2025_nih_heals  35 items, 1-5  NIH Healing Experience of All Life
#                          Stressors (NIH-HEALS), psychosocial-spiritual
#                          well-being. DATA DICTIONARY and paper: 5-point
#                          Likert, 1 = Strongly Disagree .. 5 = Strongly
#                          Agree. q6_rev, q23_rev, q28_rev, q34_rev are
#                          stored AFTER reverse-scoring (dictionary: "_rev
#                          ... reversed scoring so that 5 = Strongly
#                          Disagree"); TOT_HEALS equals the sum of the items
#                          as stored in all 338 complete rows (asserted), and
#                          the file carries no raw copy. Samples 2-4 also
#                          answered all 35 items (the paper's 9-item short
#                          form is scored from them), so all four samples
#                          share one instrument and one file, with cov_study.
#
# Cleaning: none needed. No fractional, sentinel or out-of-range item cells;
#   per-item missing cells are dropped in the melt. One sample-1 row
#   (id_code 144) is blank on every item, so the table has 363 ids.
# Dropped: TOT_HEALS9, HEALS9_ODD, HEALS9_EVEN, TOT_HEALS, HEALS_F1-F3
#   (scale scores); id_code (study participant code, replaced by row index).
# id: row index.
# Covariates: cov_study (subset: 1 = serious/life-limiting illness patients,
#   2 = COVID-19 healthcare workers, 3 = hereditary gastric cancer patients and
#   family, 4 = cancer patients); cov_age (years, floored: 32 ages in samples
#   1 and 3 are stored to the day, e.g. 35.247); cov_sex (1 male, 2 female;
#   one undocumented 3 kept as is); cov_race (2 Asian, 3 Black, 4 White;
#   1, 5, 6, 7, 8 = all others, per the dictionary); cov_ethnicity
#   (1 Hispanic, 2 non-Hispanic; two undocumented 3s kept as is).

import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/14806363/files/"
       "BERGER-%20HEALS%20short%20form%20data%20for%20PLOS%20Mental%20Health"
       ".xlsx/content")

TABLE = "sinaii_2025_nih_heals"
REV = {6, 23, 28, 34}
ITEMS = [f"q{i}_rev" if i in REV else f"q{i}" for i in range(1, 36)]
ALLOWED = set(range(1, 6))
COMPOSITES = {"TOT_HEALS9", "HEALS9_ODD", "HEALS9_EVEN", "TOT_HEALS",
              "HEALS_F1", "HEALS_F2", "HEALS_F3"}
COVS = {"subset": "cov_study", "age": "cov_age", "sex": "cov_sex",
        "race": "cov_race", "ethnicity": "cov_ethnicity"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="FOR ANALYSIS")


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = load()
    assert d.shape == (364, 48), d.shape

    # Balance the books.
    known = set(ITEMS) | COMPOSITES | set(COVS) | {"id_code"}
    assert set(d.columns) == known, set(d.columns) ^ known
    assert d["id_code"].is_unique

    ok = d[ITEMS].notna().all(axis=1) & d["TOT_HEALS"].notna()
    assert ok.sum() == 338
    assert (d.loc[ok, ITEMS].sum(axis=1) == d.loc[ok, "TOT_HEALS"]).all()

    assert d["subset"].value_counts().to_dict() == {
        "sample 1": 200, "sample 2": 78, "sample 3": 56, "sample 4": 30}
    d["subset"] = d["subset"].str.replace("sample ", "").astype(int)
    d["age"] = np.floor(d["age"])

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - ALLOWED
        assert not bad, (it, bad)
    long = long[["id", "item", "resp"] + cov_cols]
    for c in cov_cols:
        long[c] = long[c].astype("Int64")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() == 363  # one sample-1 row is all blank
    assert long["item"].nunique() == 35

    pv = {i: ALLOWED for i in ITEMS}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
