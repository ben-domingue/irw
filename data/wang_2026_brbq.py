#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.32991527
# DOI: 10.3390/bs16101775
# Paper: Wang Z, Sun L (2026). Adaptation and Validity of the Chinese Version
#   of the Bicycle Rider Behaviour Questionnaire (BRBQ) and Its Associations
#   with Personality Traits, Cycling Behaviours, and Traffic Crashes.
#   Behavioral Sciences 16(10): 1775.
# Data: figshare 10.6084/m9.figshare.32991527, one file (sheet "Exploration",
#   file 66642734): the EFA subsample only (Sample 1, n = 241 of 482 regular
#   cyclists from four regions of China) x 145 columns. Sample 2 (CFA) is not
#   deposited.
# License: CC BY 4.0 (figshare record).
# Codebook: none; the paper's Measures section and Table 1.
#
# Worked in overnight lane D 2026-11-10 (Europe PMC); held there (not built),
# ruled by Ben 2026-11-11: ship block C1 only, as the 34-item BRBQ.
#
# ONE table: wang_2026_brbq, Chinese BRBQ (Hezaveh et al. 2018), items
#   C1.1..C1.34 as deposited, 1-5 (1 = never .. 5 = nearly all of the time,
#   the paper's 2.2.1). All 34 original items ship, including items 20, 25, 33
#   and 34, which the paper's panel set aside before its EFA, and the five the
#   EFA dropped; the paper's final form is 25 items.
# Not shipped: blocks C2-C7. C2 (29 items) is coded 1-5 where the paper's CBQ
#   is 0-4, C3/C4/C5/C7 (7, 5, 8 on 1-7, 5) are not described in the paper,
#   and C6 (44) does not match the paper's 34-item IPIP; so the deposit's
#   97+ columns cannot be tied to the paper's instruments. Also not shipped:
#   occupation (free-text job titles), riding environment (multi-select),
#   and ride duration (free text, mixed units).
# Checks against the paper (Sample 1): N = 241, 128 male / 113 female, 118 with
#   no crash in three years (55 male) and 123 with one or more (73 male), age
#   mean 29.2 (SD 9.1 here vs 9.8) and range 18-55 once one age of 96 is set
#   aside. The 96 is outside the study's 18-60 eligibility and is shipped as
#   missing. Primary-responsibility crashes: 74 as in the paper, but 52 male
#   here vs the paper's 42.
# Covariates: sex (1 male / 2 female, from the paper's counts), age, education,
#   marital status, years of riding experience, purpose of riding, crashes in
#   the past three years, crashes mainly responsible for, riding hours per week.
# `id` = No.
#
# Item text: NOT SHIPPED. The deposit has codes only; the paper's Table 2 gives
#   English glosses for the 25 retained items, and the BRBQ needs a rights-
#   register row first.

import os
import sys
from io import BytesIO

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://ndownloader.figshare.com/files/66642734"
RAW = os.environ.get("WANG2026BRBQ_RAW")
NAME = "wang_2026_brbq"


def load():
    if RAW:
        return pd.read_excel(RAW)
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
    r.raise_for_status()
    return pd.read_excel(BytesIO(r.content))


def main():
    d = load()
    d.columns = [str(c).strip() for c in d.columns]
    assert d.shape == (241, 145), d.shape
    items = [f"C1.{i}" for i in range(1, 35)]
    assert [c for c in d.columns if c.startswith("C1.")] == items
    assert d[items].isin(range(1, 6)).all().all()
    assert d["sex"].value_counts().to_dict() == {1: 128, 2: 113}
    crash = d["Number of accidents in the past three years"]
    assert ((crash == 0) & (d["sex"] == 1)).sum() == 55 and (crash == 0).sum() == 118
    d["id"] = d["No."]
    assert d["id"].is_unique
    d["cov_sex"] = d["sex"].map({1: "male", 2: "female"})
    d["cov_age"] = d["age"].where(d["age"] <= 60).astype("Int64")
    assert d["cov_age"].isna().sum() == 1 and d["cov_age"].max() == 55
    d["cov_education"] = d["education level"]
    d["cov_marital_status"] = d["marital status"].str.lower()
    d["cov_riding_experience_years"] = d["riding experience"]
    d["cov_riding_purpose"] = d["purpose of riding"]
    d["cov_crashes_3y"] = crash
    d["cov_crashes_responsible_3y"] = d[
        "Number of accidents in the past three years for which you were mainly responsible"]
    d["cov_riding_hours_week"] = d["Your riding intensity (hours per week)"]
    covs = [c for c in d.columns if c.startswith("cov_")]
    long = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(int)
    long["cov_age"] = long["cov_age"].astype("Int64")
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    pv = {i: set(range(1, 6)) for i in items}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(long, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message[:200]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    main()
