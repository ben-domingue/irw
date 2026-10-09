#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/RODZ9I
# DOI: 10.1080/23276665.2021.1934052
#   Nicholson-Crotty, S., Nicholson-Crotty, J., Li, D., & Christensen, R. (2021). Exploring
#   the conditionality of public service motivation: evidence from a priming experiment.
#   Asia Pacific Journal of Public Administration, 44(3), 234-248.
# Data: Harvard Dataverse 10.7910/DVN/RODZ9I (Christensen, Nicholson-Crotty,
#       Nicholson-Crotty, Li; 2021). "APJPA_datashare.dta" (file 4725167, format=original)
#       -- 456 US public employees (police and non-police) randomised to no recall /
#       positive recall / negative recall, then the 16-item international PSM scale
#       (Kim et al. 2013: APS1-4 attraction to public service, CPV1-4 commitment to public
#       values, COM1-4 compassion, SS1-4 self-sacrifice), 1-7 with value labels 1 strongly
#       disagree .. 7 strongly agree.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. The .dta variable labels repeat the variable names (APS1 "APS1"),
#   so the stems are absent at that level; the value labels carry only the 1-7 agreement
#   anchors. The wording is Kim et al.'s (2013) published scale, not deposited.
#
# Table:
#   nicholson_crotty_2021_psm   APS1-SS4, 1-7 (one PSM instrument, four dimensions; the
#                               run_qc multi_scale warning on the four prefixes is expected).
# Skipped: PSM (a factor score), SDO (an SDO factor score; no SDO items deposited), cntrl /
#   best / worst (dummies of treatment).
# cov_condition: treatment, 0 no recall (control) / 1 positive recall / 2 negative recall
#   (three arms, so not a 0/1 treat column).
# Covariates: cov_police (0/1), cov_public_years, cov_age, cov_ideology (poli, 1 very
#   conservative .. 5), cov_education (educ, 1-4), cov_black (0/1), cov_female (0/1).
# id: row index (the file has no identifier).

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

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "rodz9i"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/4725167?format=original"
NAME = "nicholson_crotty_2021_psm"
ITEMS = [f"{p}{i}" for p in ("APS", "CPV", "COM", "SS") for i in range(1, 5)]
COVS = {"treatment": "cov_condition", "police": "cov_police", "public_yrs": "cov_public_years",
        "age": "cov_age", "poli": "cov_ideology", "educ": "cov_education", "blk": "cov_black",
        "female": "cov_female"}
SKIP = {"PSM": "factor score", "SDO": "factor score", "cntrl": "treatment dummy",
        "best": "treatment dummy", "worst": "treatment dummy"}


def fetch() -> Path:
    p = RAW_DIR / "data.dta"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, _ = pyreadstat.read_dta(str(fetch()))
    assert d.shape == (456, 29)
    accounted = set(ITEMS) | set(COVS) | set(SKIP)
    assert accounted == set(d.columns), set(d.columns) ^ accounted
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    assert ((d["treatment"] == 0) == (d["cntrl"] == 1)).all()
    assert ((d["treatment"] == 1) == (d["best"] == 1)).all()
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        if (d[c].dropna() % 1 == 0).all():
            d[c] = d[c].astype("Int64")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    assert t["resp"].isin(range(1, 8)).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert set(t["item"]) == set(ITEMS) and not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100 and len(t) == int(d[ITEMS].notna().sum().sum())
    pv = {i: set(range(1, 8)) for i in ITEMS}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.warnings:
        print(f"    [validate warn] {f.check}: {f.message[:160]}")
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
