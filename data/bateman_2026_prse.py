#!/usr/bin/env python3
# Source: https://zenodo.org/records/19137231
# DOI: none found (Zenodo deposit only; Crossref search on the title found no
#   paper as of 2026-10-02).
#   Bateman, A. (2026). "Examining Validity Evidence for a Positively Worded
#   Rosenberg Self-Esteem Scale and its Association with Depression Symptoms
#   in a Physically Active Jamaican Sample." Zenodo dataset.
# Data: Zenodo 19137231, "Positively Worded Rosenberg Self-Esteem Scale-Study
#       1_Study 2-Data.xlsx", sheet "Study 2 Data" (314 rows x 19 columns).
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text: not shipped. The .xlsx has no labels at either level (plain
#   headers, no value labels). The original RSE wording is public; the
#   positively worded rewrites exist only in the (unlocated) paper.
#
# Tables (item codes are the source column names):
#   bateman_2026_prse        10 items  Positively worded Rosenberg
#                            Self-Esteem Scale ("P-RSE_1".."P-RSE_10").
#   bateman_2026_depression   7 items  depression-symptom items DEP_1..DEP_7.
#                            The deposit does not name the instrument.
#   Response ranges are NOT documented anywhere in the deposit (no codebook,
#   no paper), so no permitted-value set is asserted; values are only
#   checked to be whole numbers. Observed: P-RSE 1-4, DEP 0-3.
#
# The "Study 1 Data" sheet is NOT used: it is the same 314 respondents.
#   Its (Age, RSE_1..RSE_10) rows are, as a multiset, identical to Study 2's
#   (Age, P-RSE_1..P-RSE_10) rows (asserted), just reordered and relabelled.
#   Shipping both would duplicate every response.
#
# -99 = missing (Age and some items) -> NA.
# id: row index of the Study 2 sheet (no respondent id in the file).
# Covariates: cov_age, cov_gender (coded 0/1 in the file; the deposit does
#   not say which is which).

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/19137231/files/Positively%20Worded%20"
       "Rosenberg%20Self-Esteem%20Scale-Study%201_Study%202-Data.xlsx/content")

PRSE = [f"P-RSE_{i}" for i in range(1, 11)]
DEP = [f"DEP_{i}" for i in range(1, 8)]
TABLES = {"bateman_2026_prse": PRSE, "bateman_2026_depression": DEP}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    x = pd.ExcelFile(io.BytesIO(r.content))
    assert x.sheet_names == ["Study 1 Data", "Study 2 Data"], x.sheet_names
    return x.parse("Study 1 Data"), x.parse("Study 2 Data")


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    s1, d = load()
    assert s1.shape == (314, 11) and d.shape == (314, 19), (s1.shape, d.shape)

    # Study 1 is Study 2 reordered: refuse to run if that ever stops holding.
    rse = [f"RSE_{i}" for i in range(1, 11)]
    a = sorted(map(tuple, s1[["Age"] + rse].values))
    b = sorted(map(tuple, d[["Age"] + PRSE].values))
    assert a == b

    assert set(d.columns) == {"Age", "Gender"} | set(PRSE) | set(DEP)
    d = d.mask(d == -99)
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns={"Age": "cov_age", "Gender": "cov_gender"})
    cov_cols = ["cov_age", "cov_gender"]

    names = []
    for table, its in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload")
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
