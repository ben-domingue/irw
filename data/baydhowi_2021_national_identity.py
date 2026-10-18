#!/usr/bin/env python3
# Source: https://zenodo.org/records/5642537
# DOI: none recorded on the deposit (no related identifiers).
#   Baydhowi, Purwono, U., & Siswadi, A. G. P. (2021). "Developing National
#   Identity Scale: As Indonesian Case." Zenodo.
# Data: Zenodo 5642537, "Data.xlsx", sheet 'Data Jurnal' (300 rows x 25
#       columns; Indonesian respondents).
# License: CC BY 4.0 (Zenodo record metadata, API).
#
# Item text: NOT shipped. The deposit holds one spreadsheet whose item
#   headers are bare item NUMBERS ("1", "2", "3(-)" ...) -- no stems, and
#   .xlsx carries no label level. The scale is the authors' own, under
#   development in this very paper, so there is no published instrument to
#   fall back on either; the wording is in the paper behind the title, which
#   the record gives no DOI for. That is where the text is.
#
# REVERSE-KEYED ITEMS: four headers carry a trailing "(-)" -- items 3, 5, 11
#   and 17. That marker is the source's own record of which items are
#   reverse-worded. The responses are shipped exactly as deposited (NOT
#   re-reversed: the file gives no indication that the authors had already
#   reflected them, and reflecting them here would be an undocumented
#   transformation). The marker is stripped from the item code and recorded
#   in this header instead, so the information is not lost -- an analyst
#   needs to know that ni_03, ni_05, ni_11 and ni_17 are negatively worded.
#
# ITEM CODES: the source numbers its items 1-20 but stores the columns out of
#   order (1, 2, 4, 13, 14, 3(-), 5(-), 7, ...). The code is built from the
#   source's OWN number, zero-padded -- ni_01..ni_20 -- so it is reversible
#   to the header and independent of column position. Nothing is assigned by
#   position.
#
# Tables:
#   baydhowi_2021_national_identity  ni_01-ni_20, 1-5.
#
# Dropped, with reasons:
#   No                           row number -> becomes `id`
#   Gender, Age, Institution, Religion  -> cov_*
# id: the file's own 'No' column.
# Covariates: cov_gender, cov_age, cov_institution, cov_religion (as given).

import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = "https://zenodo.org/api/records/5642537/files/Data.xlsx/content"
TABLE = "baydhowi_2021_national_identity"
ALLOWED = {1, 2, 3, 4, 5}
COVS = {"Gender": "cov_gender", "Age": "cov_age",
        "Institution": "cov_institution", "Religion": "cov_religion"}
HDR_RE = re.compile(r"^(\d{1,2})(\(-\))?$")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), sheet_name="Data Jurnal")
    d.columns = [str(c).strip() for c in d.columns]
    assert d.shape == (300, 25), d.shape

    ren, reversed_items = {}, []
    for c in d.columns:
        mm = HDR_RE.match(c)
        if mm:
            code = f"ni_{int(mm.group(1)):02d}"
            ren[c] = code
            if mm.group(2):
                reversed_items.append(code)
    assert len(set(ren.values())) == len(ren), "item code collision"
    assert len(ren) == 20, sorted(ren.values())
    assert sorted(reversed_items) == ["ni_03", "ni_05", "ni_11", "ni_17"], \
        reversed_items
    print(f"[items] 20 items ni_01-ni_20; reverse-worded per the source's "
          f"'(-)' marker: {', '.join(sorted(reversed_items))}")

    known = set(ren) | set(COVS) | {"No"}
    assert set(d.columns) == known, set(d.columns) ^ known
    for c in ["No"] + list(COVS):
        print(f"[drop-as-non-item] {c}")

    assert d["No"].is_unique and d["No"].notna().all()
    d = d.rename(columns={"No": "id", **COVS, **ren})
    codes = sorted(ren.values())
    cov_cols = list(COVS.values())
    for c in cov_cols:
        d[c] = d[c].astype(str).str.strip().replace({"nan": pd.NA})

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=codes,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - ALLOWED
        assert not bad, (it, bad)
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["item"].nunique() == 20 and long["id"].nunique() == 300

    checks = run_qc(long, permitted_values={c: ALLOWED for c in codes})
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
