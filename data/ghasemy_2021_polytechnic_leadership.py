#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/NTOCDZ
# DOI: 10.1177/21582440211047568
#   Ghasemy, M., Mohajer, L., Frombling, L., & Karimi, M. (2021). Faculty members in
#   polytechnics to serve the community and industry: conceptual skills and creating value
#   for the community as predictors of job satisfaction and work motivation. SAGE Open,
#   11(3).
# Data: Harvard Dataverse 10.7910/DVN/NTOCDZ (Ghasemy, Majid; 2020-10-13). "12- 228
#       polytech (no outlier).csv" (file 4137438, format=original) -- 228 polytechnic
#       academics (Malaysia) after the authors' outlier removal x Age_G, C_Tenure and 17
#       item columns: CVC1-4 (servant leadership: creating value for the community), CS1-4
#       (servant leadership: conceptual skills), JS2/4/6/8/10 (job satisfaction), WM1/2/7/8
#       (work motivation). The record describes the two servant-leadership dimensions and
#       the two outcomes; the item numbering gaps are the authors' (items not retained).
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Plain CSV, positional codes, no labels at either level, no
#   questionnaire deposited.
#
# Tables (1-5 as stored; the deposit documents no anchors). The poly_ infix keeps them apart
#   from ghasemy_2021_academics.py's tables (another 2021 Ghasemy deposit, same item codes):
#   ghasemy_2021_poly_creating_value  CVC1-CVC4
#   ghasemy_2021_poly_conceptual_skills  CS1-CS4
#   ghasemy_2021_poly_job_satisfaction  JS2, JS4, JS6, JS8, JS10
#   ghasemy_2021_poly_work_motivation  WM1, WM2, WM7, WM8
# Covariates (codes as stored, undocumented): cov_age_group (Age_G 1-5), cov_tenure
#   (C_Tenure 1-4).
# id: row index (no identifier).

import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "ntocdz"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/4137438?format=original"
P = "ghasemy_2021_poly_"
TABLES = {"creating_value": [f"CVC{i}" for i in range(1, 5)],
          "conceptual_skills": [f"CS{i}" for i in range(1, 5)],
          "job_satisfaction": ["JS2", "JS4", "JS6", "JS8", "JS10"],
          "work_motivation": ["WM1", "WM2", "WM7", "WM8"]}
COVS = {"Age_G": "cov_age_group", "C_Tenure": "cov_tenure"}


def fetch() -> Path:
    p = RAW_DIR / "data.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_csv(fetch())
    items = [c for v in TABLES.values() for c in v]
    assert d.shape == (228, 19) and set(d.columns) == set(items) | set(COVS)
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    names = [P + k for k in TABLES]
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for k, its in TABLES.items():
        name = P + k
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
