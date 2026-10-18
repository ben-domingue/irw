#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/PVTXHK (Harvard Dataverse)
# DOI: 10.7910/DVN/PVTXHK (dataset, 2020; Vuong, Wesley et al.). "Text4Hope - One Week Demographic and Perceived Stress
#   Scale Data Set" -- Alberta (Canada) subscribers to the Text4Hope COVID-19 text-message programme, first week of
#   enrolment (23-30 March 2020).
# Data: Text4Hope_PSS_Dataset.tab (an SPSS file served as original; read with pyreadstat), 6041 rows. The Perceived
#   Stress Scale (PSS-10) is stored twice: PSSQ1-10 as label strings (Never ... Very Often) and PSSQ1-10Value as
#   scored 0-4 codes. Never=0 ... Very Often=4; the Value columns equal the label code for items 1, 2, 3, 6, 9, 10 and
#   4 - label code for the positively worded items 4, 5, 7, 8, so they are already in the stress direction and all
#   ten correlate positively (0.31-0.63). Shipped as the deposit's Value codes (0 = least stress).
#   Imputed values removed: PSSQnValue is filled for 3-39 respondents per item where the label string is blank, so a
#   value is kept only where the label is present. 513 rows with ten blanks (PSSValid 'Invalid') drop out entirely.
#   Not shipped: PSSTotalScore, RoundedAverage, ItemsMissing, PSSValid, PSSCategory (derived).
#   Respondents with Age < 18 (121 of 6041) are dropped so that the sample is adult; Age blank (171) is kept.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none (no names, ids, contact fields, postal codes). The file has no respondent id; id = row index (1-based,
#   in the deposit's row order).
# Item text: not in the deposit, but the PSS-10 is a published instrument (Cohen et al. 1983).
#
# Table: vuong_2020_pss (10 items, 0-4). Covariates: cov_age, cov_gender, cov_ethnicity, cov_education,
#   cov_relationship, cov_employment, cov_housing (label strings, 'Prefer not to disclose' kept as is); date (Unix time
#   of the survey day, UTC midnight).
import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_C_2026-10-16"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}
LABEL = {"Never": 0, "Almost Never": 1, "Sometimes": 2, "Fairly Often": 3, "Very Often": 4}


def dv_fetch(doi: str, fname: str, raw_dir: Path, saveas: str = None, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset in its original format."""
    p = raw_dir / (saveas or fname)
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"] if f["label"] == fname][0]
        r = requests.get(f"https://{host}/api/access/datafile/{fid}", params={"format": "original"},
                         headers=UA, timeout=300)
        r.raise_for_status()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values). QC, validate, write."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert max(map(len, tables)) <= 40, name
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 8, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


def main() -> None:
    p = dv_fetch("10.7910/DVN/PVTXHK", "Text4Hope_PSS_Dataset.tab", RAW_ROOT / "pvtxhk",
                 saveas="Text4Hope_PSS_Dataset.sav")
    d, _ = pyreadstat.read_sav(str(p))
    assert len(d) == 6041
    d["id"] = range(1, len(d) + 1)
    d = d[~(d["Age"] < 18)].copy()  # keep adults and unknown age
    d["date"] = (pd.to_datetime(d["SurveyDate"], format="%d/%m/%Y") - pd.Timestamp("1970-01-01")).dt.total_seconds().astype(int)
    d = d.rename(columns={"Age": "cov_age", "Gender": "cov_gender", "Ethnicity": "cov_ethnicity",
                          "Education": "cov_education", "Relationship": "cov_relationship",
                          "Employment": "cov_employment", "HousingStatus": "cov_housing"})
    covs = ["cov_age", "cov_gender", "cov_ethnicity", "cov_education", "cov_relationship", "cov_employment",
            "cov_housing"]
    for c in covs[1:]:
        d[c] = d[c].replace("", pd.NA)
    d["cov_age"] = d["cov_age"].astype("Int64")
    cols = {}
    parts = []
    for i in range(1, 11):
        lab = d[f"PSSQ{i}"].map(LABEL)  # blank label -> NaN, so imputed Value cells are dropped
        v = d[f"PSSQ{i}Value"].where(lab.notna())
        code = (4 - lab) if i in (4, 5, 7, 8) else lab
        assert ((code == v) | v.isna()).all(), i  # Value agrees with label (reversed for 4, 5, 7, 8)
        cols[i] = f"pss_{i}"
        parts.append(pd.DataFrame({"id": d["id"], "item": f"pss_{i}", "resp": v, "date": d["date"]}
                                  ).join(d[covs]))
    t = pd.concat(parts).dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=list(cols.values()), ordered=True)
    t = t[["id", "item", "resp", "date"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    emit({"vuong_2020_pss": (t, {i: {0, 1, 2, 3, 4} for i in cols.values()})})


if __name__ == "__main__":
    main()
