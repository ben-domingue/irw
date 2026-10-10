#!/usr/bin/env python3
# Source: https://zenodo.org/records/17696018
# DOI: 10.5281/zenodo.17696018 (dataset; no paper is linked from the record)
#   Sejna, Erik (2025). School-Related Social Anxiety (SAQ-C), Academic Self-Concept, and
#   Social Integration [Data set]. Zenodo.
# Data: "DATA for Measuring SA research.xlsx" -- 740 lower-secondary students (ages 13-15)
#       x ID, Sex (1 male, 2 female), Grade, SA01-SA08, AS01-AS09, SI01-SI10. The record
#       description is the codebook: SA01-SA04 = SAQ-C "Speaking with Teachers", SA05-SA08
#       = SAQ-C "Criticism & Embarrassment" (Caballo et al. 2012, 2016); AS01-AS09
#       academic self-concept and SI01-SI10 social integration from a multidimensional
#       school well-being questionnaire based on the Dutch Schoolvragenlijst; all items on
#       5-point Likert scales, higher = more of the construct.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. Spreadsheet headers are positional codes (SA01, AS01, SI01) with
#   no value labels (xlsx); the record names the source instruments but deposits no wording.
#
# Tables:
#   sejna_2025_saqc                 SA01-SA08 (two SAQ-C dimensions; one instrument)
#   sejna_2025_academic_self_concept AS01-AS09
#   sejna_2025_social_integration   SI01-SI10
# Imputation dropped: 73 item cells hold fractional values, and every one equals its
#   column's mean over the integer cells (mean imputation), so those cells are dropped.
#   Two Sex cells are likewise the column mean and become missing.
# SAQ-C entry errors: the record says 5-point, but none of the eight SA items uses 5 in 740
#   pupils except SA02, twice; those two cells are dropped (isolated to one item). The block
#   is effectively answered on 1-4 (recorded as a data note).
# id: row index. The deposit's ID is not unique (534 appears twice, on two different
#   response patterns), so it is not used.
# Covariates: cov_sex (1 male, 2 female), cov_grade (as stored, 1-2).

import os
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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "z17696018"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/17696018/files/"
       "DATA%20for%20Measuring%20SA%20research.xlsx/content")
TABLES = {"sejna_2025_saqc": [f"SA{i:02d}" for i in range(1, 9)],
          "sejna_2025_academic_self_concept": [f"AS{i:02d}" for i in range(1, 10)],
          "sejna_2025_social_integration": [f"SI{i:02d}" for i in range(1, 11)]}
COVS = {"Sex": "cov_sex", "Grade": "cov_grade"}


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def drop_mean_imputed(s: pd.Series) -> tuple:
    frac = s.notna() & (s % 1 != 0)
    mu = s[~frac & s.notna()].mean()
    assert np.allclose(s[frac], mu), (s.name, s[frac].unique(), mu)
    return s.mask(frac), int(frac.sum())


def main() -> None:
    d = pd.read_excel(fetch())
    items = [c for v in TABLES.values() for c in v]
    assert d.shape == (740, 30) and set(d.columns) == {"ID"} | set(COVS) | set(items)
    assert d["ID"].nunique() == 739
    print("  [skip] ID: not unique (534 twice); row index used")
    n_imp = 0
    for c in items + ["Sex"]:
        d[c], k = drop_mean_imputed(d[c])
        n_imp += k
    print(f"  dropped {n_imp} mean-imputed cells")
    assert n_imp == 75
    # SAQ-C block: no 5 on any of the 8 items across 740 pupils except two on SA02 --
    # isolated to one item, so treated as entry errors and dropped
    sa = TABLES["sejna_2025_saqc"]
    five = d[sa] == 5
    assert int(five.sum().sum()) == 2 and five["SA02"].sum() == 2
    d[sa] = d[sa].mask(five)
    print("  dropped 2 cells of 5 on SA02 (no other SAQ-C item uses 5)")
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    d["cov_sex"] = d["cov_sex"].astype("Int64")
    covs = list(COVS.values())
    names = list(TABLES)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, its in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(range(1, 6)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100
        pv = {i: set(range(1, 6)) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        total += len(t)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert total == int(d[items].notna().sum().sum()), "books do not balance"


if __name__ == "__main__":
    main()
