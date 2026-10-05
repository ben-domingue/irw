#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC7666562
# DOI: 10.7717/peerj.10301
#   "Development and validation of Egyptian developmental screening chart for
#   children from birth up to 30 months" (El Shafie, Omar, Bashir, Mahmoud,
#   Basma, Hussein, Mostafa & Bahbah, 2020), PeerJ 8:e10301.
# Data: PeerJ supplementary file peerj-08-10301-s004 ("Designing Raw Data"),
#       fetched from the Europe PMC supplementaryFiles zip. It is served with a
#       .zip name but is an SPSS .sav (1503 x 74, one row per child), the
#       instrument-development sample. The other data file, s005 ("Validation
#       data", 337 children), carries only EDSC/ASQ grades and totals -- no
#       item responses -- and is not used.
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data
#          are the article's own supplementary file.
#
# Item text: shipped (itemtext_verification/make_itemtext_elshafie_2020_edsc.py).
#   The .sav has NO variable labels on Q1..Q54; value labels are {0: No, 1: Yes}
#   on all 54. The wording is in the deposit's own SI: s002 ("Arabic checklist",
#   the administered form, items numbered 1-..54- with their age band) and s001
#   (the English Baroda checklist it was adapted from; not identical -- e.g.
#   Arabic 27 is the pincer grasp, Baroda 10th month is "Pulls string"). Item
#   code Qk is tied to Arabic item k- by number (paper_order), checked against
#   each item's age band in itemtext_verification/verify_elshafie_2020_edsc.R.
#
# Table: elshafie_2020_edsc -- 54 developmental milestones (22 motor, 32
#   mental), parent interview / examiner check, 0 = No, 1 = Yes. Item codes are
#   the .sav column names Q1..Q54.
#
# `Serial_Number_Overall` (1..1503, unique) is the id. No PII (no names or
# dates of birth; age is in days). Items are complete (no missing cells) and
# their sum equals Total_Number_of_Items_Passed on every row (asserted).
# Items above a child's age band are recorded as 0; the deposit does not
# distinguish "not yet able" from "not asked", so they are shipped as recorded
# (the checklist is a Yes/No form with no "not administered" option).
# 3 pairs of children share an identical item pattern AND identical
# rounded anthropometry/age, but differ on sex, residence or SES; all three are
# Guttman-type prefix patterns that recur 6-9 times within their age band, so
# they are chance agreement, not duplication, and are kept.

import io
import sys
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW = REPO_ROOT / "automated_finding" / "runs" / "raw" / "elshafie_2020"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7666562/supplementaryFiles"
NAME = "elshafie_2020_edsc"

ITEMS = [f"Q{i}" for i in range(1, 55)]
COV = {
    "Sex": "cov_sex",                      # 1 Male, 2 Female
    "Residence": "cov_residence",          # 1 Rural, 2 Urban
    "Socio_Economic_Status": "cov_ses",    # 1 Low, 2 Moderate, 3 High
    "Age_days": "cov_age_days",
}
# Columns not shipped, with the reason (the books must balance).
SKIP = {
    "Serial_Number_within_candidate": "row counter per examiner",
    "Serial_number_within_Category": "row counter per age group",
    "Age_Category_for_each_month": "age group, derived from Age_days",
    "Age_Category": "coarse age group, derived from Age_days",
    "Age_months": "Age_days / 30",
    "Weight": "anthropometry; mixed units (grams for some rows, kg for others)",
    "Length": "anthropometry, not a response",
    "HC": "anthropometry, not a response",
    "Total_Number_of_Items_Passed": "sum of Q1..Q54 (asserted)",
    "Score": "summary score (mostly equal to the items-passed total)",
    "DA_BARODA_97": "derived developmental age",
    "DA_BARODA_50": "derived developmental age",
    "DA_Menofyia_97": "derived developmental age",
    "DA_Menofyia_50": "derived developmental age",
    "Grade_on_Barada": "derived grade",
}


def fetch():
    RAW.mkdir(parents=True, exist_ok=True)
    z = RAW / "supp.zip"
    if not z.exists():
        r = requests.get(SUPP, headers=UA, timeout=300)
        r.raise_for_status()
        z.write_bytes(r.content)
    sav = RAW / "peerj-08-10301-s004.sav"
    if not sav.exists():
        sav.write_bytes(zipfile.ZipFile(z).read("peerj-08-10301-s004.zip"))
    d, meta = pyreadstat.read_sav(str(sav))
    return d, meta


def main():
    d, meta = fetch()
    assert d.shape == (1503, 74), d.shape
    accounted = {"Serial_Number_Overall"} | set(COV) | set(ITEMS) | set(SKIP)
    assert set(d.columns) == accounted, set(d.columns) ^ accounted
    for c, why in SKIP.items():
        print(f"  skip {c}: {why}")
    assert d["Serial_Number_Overall"].is_unique
    assert d[ITEMS].notna().all().all()
    assert set(pd.unique(d[ITEMS].values.ravel())) == {0.0, 1.0}
    for c in ITEMS:
        assert meta.variable_value_labels[c] == {0.0: "No", 1.0: "Yes"}, c
    assert (d[ITEMS].sum(axis=1) == d["Total_Number_of_Items_Passed"]).all()
    # no full-row duplicates once the row counters are set aside
    content = [c for c in d.columns if not c.startswith("Serial")]
    assert not d.duplicated(content).any()

    d = d.rename(columns={"Serial_Number_Overall": "id", **COV})
    d["id"] = d["id"].astype(int)
    covs = list(COV.values())
    for c in covs:
        assert d[c].notna().all(), c
        d[c] = d[c].astype(int)

    t = d.melt(id_vars=["id"] + covs, value_vars=ITEMS, var_name="item",
               value_name="resp")
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100

    pv = {i: {0, 1} for i in ITEMS}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail}")
    report = irw_validate.validate_frame(
        t, label=NAME, profile="upload", context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
