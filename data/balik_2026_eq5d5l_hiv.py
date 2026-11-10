#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC13576739
# DOI: 10.7717/peerj.21727
#   "Reliability and validity of the Turkish EQ-5D-5L in adults living with HIV"
#   (Balik & Ceran, 2026), PeerJ 14:e21727.
# Data: the article's supplementary file peerj-14-21727-s005.csv (Europe PMC
#   supplementaryFiles zip): 217 survey rows x 31 columns for 157 patients;
#   the 60 test-retest participants (paper Methods) have two rows each
#   (retest = 1, `days.between.survey` filled on both).
# License: CC BY 4.0 (article licence; the data are the article's own SI).
#
# Sample: 157 adults living with HIV at a tertiary referral hospital in
#   Istanbul (paper: median age 41, 93.0% male, 63.1% university education).
#   id = patient.id. wave: 1 = the patient's first survey, 2 = the retest
#   (the higher survey.id of a retest pair; the file does not date the surveys,
#   and `days.between.survey` is the same on both rows).
#
# Table:
#   balik_2026_eq5d5l  mobility, self_care, activity, pain, anxiety  1-5
#     EQ-5D-5L descriptive system (1 = no problems .. 5 = extreme problems /
#     unable to). Items use EuroQol's dimension codes: eq5d_mo (source column
#     mobility), eq5d_sc (self_care), eq5d_ua (activity = usual activities),
#     eq5d_pd (pain/discomfort), eq5d_ad (anxiety/depression); the source names
#     read as covariates to irw_lint_covariates.
#   Not shipped: the *_3l columns and utility_uk_3l, which the paper says were
#   derived with the UK EQ-5D-3L crosswalk (Van Hout et al. 2012) - not
#   administered; the 5-digit `state` and `health_state_3l` strings (derived);
#   EQ_VAS (a single 0-100 rating); note the derived `state` string disagrees
#   with the item columns on 2 of 217 rows, and the items are what ship; the clinical record fields (CD4, viral
#   load, ART regimen and duration, AIDS-defining illness, comorbidity).
#   dx.date (date of HIV diagnosis) is dropped in no form.
#
# Covariates: age, sex (1 male, 2 female), education (1 primary, 2 high school,
#   3 university; the paper's three categories).
#
# Item text: not shipped. Levels checked: csv headers are dimension names, no
#   labels. EQ-5D-5L wording is EuroQol-licensed and not in the deposit.

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "balik_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13576739/supplementaryFiles"
FILE = "peerj-14-21727-s005.csv"
NAME = "balik_2026_eq5d5l"
ITEMS = ["mobility", "self_care", "activity", "pain", "anxiety"]
# the EuroQol's own dimension abbreviations (MO, SC, UA, PD, AD)
CODES = {"mobility": "eq5d_mo", "self_care": "eq5d_sc", "activity": "eq5d_ua",
         "pain": "eq5d_pd", "anxiety": "eq5d_ad"}


def fetch() -> Path:
    p = RAW_DIR / FILE
    if not p.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        p.write_bytes(z.read([n for n in z.namelist() if n.endswith(FILE)][0]))
    return p


def main() -> None:
    d = pd.read_csv(fetch())
    assert d.shape == (217, 31), d.shape
    assert d["survey.id"].is_unique
    n = d.groupby("patient.id").size()
    assert n.value_counts().to_dict() == {1: 97, 2: 60}
    assert (d.loc[d["patient.id"].isin(n[n == 2].index), "retest"] == 1).all()
    assert d[ITEMS].isin([1, 2, 3, 4, 5]).all().all()
    # the 5-digit state string is the five items concatenated, except on two
    # rows (e.g. items 4-4-5-5-4 vs state 44444),
    # where the item columns are shipped as deposited
    assert (d[ITEMS].astype(str).agg("".join, axis=1) != d["state"].astype(str)).sum() == 2
    d = d.sort_values(["patient.id", "survey.id"])
    d["wave"] = d.groupby("patient.id").cumcount() + 1
    pat = d.drop_duplicates("patient.id")
    assert len(pat) == 157 and round((pat["sex"] == 1).mean() * 100, 1) == 93.0
    d = d.rename(columns={"patient.id": "id", "age": "cov_age", "sex": "cov_sex",
                          "education": "cov_education"})
    d["cov_sex"] = d["cov_sex"].map({1: "male", 2: "female"})
    d["cov_education"] = d["cov_education"].map({1: "primary", 2: "high school", 3: "university"})
    covs = ["cov_age", "cov_sex", "cov_education"]
    assert d[covs].notna().all().all()
    t = d.melt(id_vars=["id", "wave"] + covs, value_vars=ITEMS, var_name="item", value_name="resp")
    t["resp"] = t["resp"].astype(int)
    t["item"] = t["item"].map(CODES)
    t = t[["id", "item", "resp", "wave"] + covs].sort_values(["id", "wave", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item", "wave"]).any()

    pv = {CODES[i]: {1, 2, 3, 4, 5} for i in ITEMS}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message[:150]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
