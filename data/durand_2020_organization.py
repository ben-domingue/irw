#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC7485505
# DOI: 10.7717/peerj.9844
#   "Reduced organizational skills in adults with ADHD are due to deficits in
#   persistence, not in strategies" (Durand, Arbone & Wharton, 2020), PeerJ
#   8:e9844.
# Data: PeerJ supplementary file peerj-08-9844-s001.sav (774 x 77), fetched from
#       the Europe PMC supplementaryFiles zip. One row per respondent.
# License: CC BY 4.0 (article licence, Europe PMC `license: cc by`); the data
#          are the article's own supplementary file.
#
# Item text: not shipped. The .sav has no variable labels on the item columns
#   (bare DOSQ_1..DOSQ_38, ASRS_1..ASRS_18); value labels exist only for the
#   demographics. The ASRS v1.1 wording is public (Kessler et al. 2005); the
#   DOSQ items are in Durand's own instrument papers, not this deposit.
#
# Tables:
#   durand_2020_dosq  Durand Organizational Skills Questionnaire, 38 items,
#                     6-point Strongly Disagree..Strongly Agree (1-6, paper)
#   durand_2020_asrs  Adult ADHD Self-Report Scale, 18 items, 5-point
#                     Never..Very Often (1-5, paper)
#
# The paper reports one online sample of N = 774; the file's `Study` column
# splits it 407 / 367. The 407 rows of Study 1 are exactly the sample of the
# follow-up paper Durand & Arbone 2022 (10.7717/peerj.12836; every one of its
# 407 rows matches a Study 1 row on age + all 56 DOSQ/ASRS items), so DOSQ and
# ASRS ship once, here, with `Study` kept as cov_study; durand_2022_* carries
# only the PHQ-9 and STAI-6 that the 2022 paper added.
# Subscale and total columns are verified sums and skipped as composites.
# No missing values anywhere in the item block; no imputation language in the
# paper.

import io
import sys
import tempfile
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7485505/supplementaryFiles"

DOSQ = [f"DOSQ_{i}" for i in range(1, 39)]
ASRS = [f"ASRS_{i}" for i in range(1, 19)]
SCALES = {
    "durand_2020_dosq": (DOSQ, [1, 2, 3, 4, 5, 6]),
    "durand_2020_asrs": (ASRS, [1, 2, 3, 4, 5]),
}
COV = {
    "Study": "cov_study",
    "Language_R": "cov_language",        # 1 English, 2 other
    "Education_R": "cov_education",      # 1 HS-college, 2 bachelor, 3 post-bachelor
    "Student": "cov_student",            # 1 yes, 2 no
    "Gender": "cov_gender",              # 1 male, 2 female
    "Location": "cov_location",          # 1 N. America ... 7 Oceania
    "ADHDdiagnosis": "cov_adhd_diagnosis",  # 1 yes, 2 no
    "Age": "cov_age",
}
SKIP = {c: "subscale/total score (composite)" for c in [
    "DOSQ_work_organization", "DOSQ_communication_clarity", "DOSQ_punctuality",
    "DOSQ_goal_oriented", "DOSQ_assiduity", "DOSQ_workspace_organization",
    "DOSQ_strategies", "DOSQ_attentiveness", "DOSQ_Total", "ASRS_Total",
    "ASRS_PartA", "ASRS_inattention", "ASRS_hyperimpuls"]}


def fetch():
    r = requests.get(SUPP, headers=UA, timeout=300)
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(z.read("peerj-08-9844-s001.sav"))
        f.flush()
        d, _ = pyreadstat.read_sav(f.name)
    return d


def convert():
    d = fetch()
    assert d.shape == (774, 77), d.shape
    items = [c for cols, _ in SCALES.values() for c in cols]
    cols, accounted = set(d.columns), set(items) | set(COV) | set(SKIP)
    assert cols == accounted, (cols - accounted, accounted - cols)
    for c, why in SKIP.items():
        print(f"  skip {c}: {why}")
    assert (d[DOSQ].sum(axis=1) == d["DOSQ_Total"]).all()
    assert (d[ASRS].sum(axis=1) == d["ASRS_Total"]).all()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COV)
    covs = list(COV.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    names = list(SCALES)
    assert len(names) == len(set(names))
    for name, (cols_, pv) in SCALES.items():
        long = d.melt(id_vars=["id"] + covs, value_vars=cols_,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        assert long["resp"].isin(pv).all()
        long = long[["id", "item", "resp"] + covs].reset_index(drop=True)
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(
            long, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
