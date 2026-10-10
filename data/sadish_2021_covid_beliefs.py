#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/WKDC9I
# DOI: 10.1016/j.jdeveco.2021.102699
#   Sadish, D., Adhvaryu, A., & Nyshadham, A. (2021). (Mis)information and anxiety:
#   evidence from a randomized Covid-19 information campaign. Journal of Development
#   Economics, 152, 102699.
# Data: Harvard Dataverse 10.7910/DVN/WKDC9I (D, Sadish; 2021-05-31). is_4_4_6_publicData.dta
#       (file 4771542, format=original) -- 914 garment-factory workers (Bengaluru; most
#       staying in hostels or back home in Odisha after the 2020 lockdown), phone surveys at
#       baseline (_bl) and endline (_el, 745 reached), randomised to receive Covid-19
#       information by voice recording, phone call or text message. Six yes/no belief
#       questions are asked at both rounds, each with value labels 0 No / 1 Yes / 2 Don't
#       know and a variable label naming the statement (via the *_des_* copies): vector
#       "Non-symptomatic can spread Covid-19", remedy "Covid-19 has remedies", antibiotics
#       "Would recommend Covid-19 symptomatic to take antibiotics", urine "... drink cow's
#       urine", turmeric "Eating turmeric protects from Covid-19 infection",
#       religion_spread "Believers of some religions spread Covid-19 more".
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. The .dta carries the statement paraphrases above at the
#   variable-label level of the *_des_* copies and No/Yes/Don't know value labels on the
#   raw items, but these are analysis labels, not the questionnaire wording (asked by phone
#   in Hindi/Odia; README: a redacted baseline questionnaire was in the authors' own
#   archive and is not in the deposit).
#
# Table:
#   sadish_2021_covid_beliefs  vector, remedy, antibiotics, urine, turmeric, religion_spread;
#                              resp 1 = Yes (endorses the statement), 0 = No; "Don't know"
#                              (2) is a non-response and is dropped. Only "vector" is a
#                              true statement, so endorsement is not correctness; resp is
#                              the endorsement as asked. wave 1 baseline, 2 endline.
# Skipped: symptoms_1-9 (free-recall symptom lists) and cough_des/fever_des (derived from
#   them); heart (a "which is deadlier" comparison); the *_tri/_bi/_des recodes; knowledge
#   indices; PHQ-4 / PHQ-2 / GAD-2 (only totals deposited); call-process and intervention
#   delivery variables.
# Covariates: cov_treatment (1 voice recording, 2 phone call, 3 text message), cov_female,
#   cov_edu_hi (above grade 10), cov_age, cov_religion (code; 998 other), cov_location
#   (code), cov_smartphone, cov_hostel. cluster_id = factory (23); block_id = strata
#   (randomisation strata).
# id: empcode (unique 1-914, an anonymised sequence).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "wkdc9i"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/4771542?format=original"
NAME = "sadish_2021_covid_beliefs"
ITEMS = ["vector", "remedy", "antibiotics", "urine", "turmeric", "religion_spread"]
COVS = {"treatment": "cov_treatment", "female": "cov_female", "edu_hi": "cov_edu_hi",
        "age": "cov_age", "religion": "cov_religion", "location": "cov_location",
        "smartphone": "cov_smartphone", "hostel": "cov_hostel"}


def fetch() -> Path:
    p = RAW_DIR / "data.dta"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, m = pyreadstat.read_dta(str(fetch()))
    assert d.shape == (914, 142) and d["empcode"].is_unique
    rows, n_dk = [], 0
    for wave, suf in ((1, "_bl"), (2, "_el")):
        for it in ITEMS:
            raw = pd.to_numeric(d[it + suf].replace("", pd.NA))
            assert set(raw.dropna().unique()) <= {0, 1, 2}, (it, suf)
            assert m.variable_value_labels[it + "_bl"] == {0: "No", 1: "Yes", 2: "Don't know"}
            des = d[it + "_des" + suf]
            ok = raw.notna()
            assert ((raw[ok] == 1) == (des[ok] == 1)).all(), (it, suf)  # des = said Yes
            n_dk += int((raw == 2).sum())
            x = pd.DataFrame({"id": d["empcode"].astype(int), "item": it, "resp": raw, "wave": wave})
            rows.append(x[x["resp"].isin([0, 1])])
    print(f"  dropped {n_dk} \"Don't know\" answers")
    print("  [skip] symptoms_*, cough/fever_des, heart, recodes, indices, PHQ/GAD totals, delivery vars")
    cov = d[["empcode", "factory", "strata"] + list(COVS)].rename(
        columns={"empcode": "id", "factory": "cluster_id", "strata": "block_id", **COVS})
    for c in cov.columns:
        cov[c] = pd.to_numeric(cov[c]).astype("Int64")
    t = pd.concat(rows, ignore_index=True).merge(cov, on="id", validate="many_to_one")
    t["resp"] = t["resp"].astype(int)
    covs = ["cluster_id", "block_id"] + list(COVS.values())
    t = t[["id", "item", "resp", "wave"] + covs].sort_values(["id", "wave", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item", "wave"]).any() and set(t["item"]) == set(ITEMS)
    assert t["id"].nunique() >= 100
    pv = {i: {0, 1} for i in ITEMS}
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
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
