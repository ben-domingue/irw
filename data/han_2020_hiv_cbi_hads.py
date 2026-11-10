#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/b6ht48w4hm
# DOI: 10.17632/b6ht48w4hm (data; no paper DOI on the record)
#   Han, S. (2020). "Dataset of nurse-delivered cognitive behavioral
#   intervention on depression, anxiety and medication adherence for persons
#   living with HIV in China: a clinical controlled trial." Mendeley Data.
# Data: "raw data.xls", Sheet1 (420 rows = 140 participants x 3 waves:
#   baseline, after the 10-week intervention, 6-month follow-up).
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: not shipped -- codes only (HADS1..HADS14); HADS (Zigmond &
#   Snaith) is a register `block` instrument.
#
# SCALE: HADS1-HADS14 stored 1-4, i.e. the scored 0-3 plus one: the odd items
#   sum to the deposit's `Anxiety` column and all 14 to `HADS` on every
#   complete row (asserted), so items are already in their scored direction
#   (HADS reverse-keys some items in scoring). Kept as deposited.
#
# Tables:
#   han_2020_hads   HADS1-HADS14 (odd = anxiety, even = depression, as the
#                   deposit's subscale sums show), `wave` 1-3. One table, as
#                   most HADS tables in IRW.
# `Group` (1/2) is the trial arm, but which code is the CBI arm is not
#   labelled in the deposit, so it ships as cov_group, not `treat`.
# Not shipped: PHQ4 (a total), self-reported adherence (3 binary single
#   items), VAS, MPR, CD4, viral load, the deposit's sums.
# Dropped covariates: Gender, Household registry, Ethnicity, Education level,
#   Religion, Employment, Marital status, Transmission mode -- all numeric
#   codes with no labels in the deposit.
# Covariates: cov_group, cov_age, cov_years_since_diagnosis. id = ID.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = ("https://data.mendeley.com/public-files/datasets/b6ht48w4hm/files/"
            "362f6149-055e-4c9d-a9e7-d634bbb42d4f/file_downloaded")
TABLE = "han_2020_hads"
ITEMS = [f"HADS{i}" for i in range(1, 15)]
ALLOWED = {1, 2, 3, 4}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert d.shape == (420, 42), d.shape
    assert not d.duplicated(["ID", "Wave"]).any()
    assert d.groupby("ID").size().eq(3).all()
    comp = d.dropna(subset=ITEMS)
    assert (comp[ITEMS].sum(axis=1) == comp["HADS"]).all()
    assert (comp[ITEMS[0::2]].sum(axis=1) == comp["Anxiety"]).all()
    assert (comp[ITEMS[1::2]].sum(axis=1) == comp["Depression"]).all()
    # arm and baseline descriptors are person-level
    for c in ("Group", "Age", "Years of HIV diagnosis"):
        assert d.groupby("ID")[c].nunique().le(1).all(), c

    d["id"] = d["ID"].astype(int)
    d["wave"] = d["Wave"].astype(int)
    d["cov_group"] = d["Group"].astype(int)
    d["cov_age"] = d["Age"]
    d["cov_years_since_diagnosis"] = d["Years of HIV diagnosis"]
    cov_cols = ["cov_group", "cov_age", "cov_years_since_diagnosis"]
    long = d.melt(id_vars=["id", "wave"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert not set(long["resp"]) - ALLOWED
    long = long[["id", "item", "resp", "wave"] + cov_cols]
    long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item", "wave"]).any()
    checks = run_qc(long, permitted_values={c: ALLOWED for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {c.name}: {c.detail[:130]}")
    (OUT_DIR / f"{TABLE}.csv").write_text(long.to_csv(index=False))
    print(f"[write] {TABLE}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
