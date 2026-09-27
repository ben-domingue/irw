#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC12810385
# DOI: 10.7717/peerj.20584
#   "Examination of factors affecting insomnia in older victims of the Kumamoto
#   earthquake" (Kanamori, Samiso & Ide-Okochi, 2026), PeerJ 14:e20584.
# Data: PeerJ supplementary files, fetched from the Europe PMC supplementaryFiles
#       zip: peerj-14-20584-s001.xlsx (4,758 x 31 raw data, one row per
#       respondent) and peerj-14-20584-s002.xlsx (codebook, "Categorical data
#       codes"; 99 = No answer).
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data
#          are the article's own supplementary file.
#
# Item text: not shipped. The codebook (s002) names each AIS item and gives all
#   four anchors for every item (e.g. "AIS-1 (Sleep induction): 0 No problem ...
#   3 Very delayed or did not sleep all"); the survey used the Japanese AIS
#   (Okajima et al. 2013), whose Japanese wording is not in the deposit.
#
# Tables:
#   kanamori_2026_ais  Athens Insomnia Scale, 8 items, 0-3 (codebook). 99 = "No
#                      answer" is dropped per item-response (the paper:
#                      "Missing values for each variable were excluded").
#
# The respondents are adults 65+ living in temporary housing or relocated after
# the 2016 Kumamoto earthquake. Everything else in the file is a person-level
# covariate (demographics, housing, lifestyle, and a 10-way "who provides
# social support" checklist), carried as cov_* with 99 set to missing.
# AIS Total is the sum of the eight items (verified: equal on all 4,758 rows)
# and is skipped as a composite.

import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12810385/supplementaryFiles"

AIS = [f"AIS-{i}" for i in range(1, 9)]
COV = {
    "Gender": "cov_male",                     # 1 = male, 0 = female
    "Age": "cov_age",
    "Cohabitant": "cov_cohabitant",           # 1 yes, 2 no
    "temporary\nhousing": "cov_temporary_housing",  # 1 prefab, 3 private, 5 public
    "current \nresidence": "cov_current_residence",
    "Scope of \nrelocation": "cov_relocation_scope",
    "exercise\nhabits": "cov_exercise_habit",
    "Eat three\nmeals a day": "cov_three_meals",
    "Appetite": "cov_appetite",
    "Meal partner": "cov_meal_partner",
    "Community\nparticipation": "cov_community_participation",
    "SS\n(anyone)": "cov_ss_none",            # codebook: Yes = 0, None = 1
    "SS\n(Family) ": "cov_ss_family",
    "SS\n(Friend) ": "cov_ss_friend",
    "SS\n(Neighbors) ": "cov_ss_neighbors",
    "SS\n(Coworker) ": "cov_ss_coworker",
    "SS\n(District welfare \ncommissioners) ": "cov_ss_welfare_commissioner",
    "SS\n(Hospital) ": "cov_ss_hospital",
    "SS\n(Nursing care\noffice ) ": "cov_ss_nursing_office",
    "SS\n(City office) ": "cov_ss_city_office",
    "SS\n(Other) ": "cov_ss_other",
}
SKIP = {
    "No.": "becomes id",
    "AIS Total": "sum of AIS-1..AIS-8 (composite)",
}


def fetch():
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    return pd.read_excel(io.BytesIO(z.read("peerj-14-20584-s001.xlsx")))


def convert():
    d = fetch()
    assert d.shape == (4758, 31), d.shape
    assert d["No."].is_unique
    # books
    cols = set(d.columns)
    accounted = set(AIS) | set(COV) | set(SKIP)
    assert cols == accounted, (cols - accounted, accounted - cols)
    for c, why in SKIP.items():
        print(f"  skip {c!r}: {why}")
    assert (d[AIS].sum(axis=1) == d["AIS Total"]).all()

    d = d.rename(columns={"No.": "id", **COV})
    covs = list(COV.values())
    for c in covs:
        d[c] = pd.to_numeric(d[c], errors="coerce").replace(99, np.nan)

    long = d.melt(id_vars=["id"] + covs, value_vars=AIS,
                  var_name="item", value_name="resp")
    long["item"] = long["item"].str.replace("-", "_").str.lower()
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    n99 = int((long["resp"] == 99).sum())
    long = long[long["resp"].isin([0, 1, 2, 3])].reset_index(drop=True)
    print(f"  dropped {n99} '99 = No answer' item-responses")
    long = long[["id", "item", "resp"] + covs]

    name = "kanamori_2026_ais"
    pv = [0, 1, 2, 3]
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        long, label=name, profile="upload", context={"permitted_values": pv})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{name}.csv", index=False)
    print(f"{name}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
