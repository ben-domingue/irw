#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0259392
# DOI: 10.1371/journal.pone.0259392
# Paper: Useche SA, Valle E, Valle-Escolano R, Colomer-Perez N (2021).
#   Psychometric properties, validity and insights of the School Bullying
#   Questionnaire (CIE-A) in secondary schools of the Valencian Community
#   (Spain). PLoS ONE 16(11): e0259392.
# Data: PLOS SI S1 File (journal.pone.0259392.s001, SPSS .sav): 810 Valencian
#   secondary students x 43 columns.
# License: CC BY 4.0 (the article and its SI).
# Codebook: none beyond the .sav's own variable/value labels.
#
# Worked from the cleaned leads list (leads/plos_leads_2026-10-30.csv),
# overnight lane A 2026-11-10; held that night, ruled ship by Ben 2026-11-11.
#
# ONE table: useche_2021_cie_a, CIE1..CIE36, 0-2 (value labels 0/1/2), raw.
#
# DATA NOTE -- NON-INTEGER CELLS DROPPED: 778 of 29,160 CIE item cells (94
#   respondents) hold non-integer values on the 0/1/2 scale (e.g. 0.155,
#   1.0182, -0.066), and Age has values like 14.293. The paper describes
#   listwise deletion and does not mention these values. Every non-integer
#   item cell is dropped (the gori_2021 precedent); integer cells are kept as
#   deposited. Age ships only where it is a whole number.
# Not shipped: the composite scores (redes social networks, SWLS, Psychological
#   Distress), which are single summary columns, not items.
# Covariates: gender (value labels), grade (1ESO..4ESO, 1BACH; code 6 is
#   unlabelled, 6 rows, and ships as missing), age (integer values only),
#   repeated a grade in the last 5 years (Neg_outc, 0 no / 1 yes).
# `id` = row index (the file has no id column).
#
# Item text: NOT SHIPPED. The .sav carries no item wording (labels are the
#   numeric codes only); the CIE-A stems would need the published instrument.

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0259392.s001"
RAW = os.environ.get("USECHE2021_RAW")
NAME = "useche_2021_cie_a"


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_useche2021_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    d, m = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return d, m


def main():
    d, m = load()
    assert d.shape == (810, 43), d.shape
    vl = m.variable_value_labels
    items = [f"CIE{i}" for i in range(1, 37)]
    nonint = d[items].notna() & (d[items] != d[items].round())
    print(f"non-integer item cells dropped: {int(nonint.sum().sum())} "
          f"({int(nonint.any(axis=1).sum())} respondents)")
    d["id"] = range(1, len(d) + 1)
    d["cov_gender"] = d["Gender"].map(vl["Gender"]).str.lower()
    d["cov_grade"] = d["Grade"].map(vl["Grade"])
    d["cov_age"] = d["Age"].where(d["Age"] == d["Age"].round()).astype("Int64")
    d["cov_repeated_grade"] = d["Neg_outc"].astype("Int64")
    assert (d["cov_gender"] == "female").sum() == 428
    covs = ["cov_gender", "cov_grade", "cov_age", "cov_repeated_grade"]
    long = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].isin([0, 1, 2])].copy()
    long["resp"] = long["resp"].astype(int)
    for c in ["cov_age", "cov_repeated_grade"]:
        long[c] = long[c].astype("Int64")
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    pv = {i: {0, 1, 2} for i in items}
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(long, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, NAME + ".csv"), index=False)
    print(f"{NAME}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    main()
