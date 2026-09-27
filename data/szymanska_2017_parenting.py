#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC5470577
# DOI: 10.7717/peerj.3384
#   "The ways parents cope with stress in difficult parenting situations: the
#   structural equation modeling approach" (Szymanska & Dobrenko, 2017), PeerJ
#   5:e3384.
# Data: PeerJ Supplemental Information 1, peerj-05-3384-s001.sav
#       ("BASE_FOR_REVIEW_STRESS.SAV", 319 x 44), fetched from the Europe PMC
#       supplementaryFiles zip. The other supplements are an AMOS how-to (.docx)
#       and two AMOS model files (.amw) -- no further data.
# License: CC BY 4.0 (PeerJ article; Europe PMC license "cc by"). Article-
#          attached SI, so the article licence is the source licence.
#
# Item text: not shipped. The .sav has no variable labels (bare codes tr1..,
#   r1.., s1..); the paper gives the SI variable-to-scale mapping and one sample
#   item pair for the Discrepancy scale only. The scales are the first author's
#   own Polish instruments (Szymanska 2011a/2012a); wording would need those
#   Polish sources.
#
# Online survey of 319 Polish parents of preschoolers (Methods). Tables:
#   szymanska_2017_parenting_difficulty   Experienced Parenting Difficulties, tr1-tr8
#   szymanska_2017_child_representation   Representation of the Child in the
#                                         Parent's Mind, r1-r8
#   szymanska_2017_parent_stress_coping   Stress Scale, s1-s15 (four factors per
#                                         the SI listing: distancing s2-s4, help
#                                         seeking s1/s5/s6, pressure s7-s9,
#                                         withdrawal s10-s15; one instrument)
# Every item uses 0-10, each value used on (nearly) every item; the paper does
# not print the anchors. No imputation language in the paper; every cell is an
# integer. Three respondents at 0 on all 31 items are dropped (see convert()).
# The 59 parents with blank s1-s15 did not answer the Stress Scale and
# are simply absent from that table.
#
# rozb1-rozb6 are NOT responses: the paper says the Discrepancy score is "the
# square of Euclidean distance" between two -7..7 ratings, and every value is a
# perfect square (asserted below). The underlying ratings are not deposited.
#
# Parent demographics are coded 0 for 144 parents who skipped them (0 is not a
# labelled category on sex/residence/education, and not an age); 0 -> missing,
# and the two parent_age == 1 cells too (not an adult age).

import sys
import time
import zipfile
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automated_finding"))
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC5470577/supplementaryFiles"
SAV = "peerj-05-3384-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch() -> pd.DataFrame:
    for attempt in range(5):
        r = requests.get(SUPP, headers=UA, timeout=120)
        if r.status_code == 200 and r.content[:2] == b"PK":
            with zipfile.ZipFile(BytesIO(r.content)) as z:
                name = next(n for n in z.namelist() if n.endswith(SAV))
                tmp = OUT_DIR / f".tmp_{SAV}"
                tmp.write_bytes(z.read(name))
                try:
                    df, _ = pyreadstat.read_sav(str(tmp))
                finally:
                    tmp.unlink()
                return df
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{SUPP} did not return a zip after 5 attempts")


TR = [f"tr{i}" for i in range(1, 9)]
R = [f"r{i}" for i in range(1, 9)]
S = [f"s{i}" for i in range(1, 16)]
ROZB = [f"rozb{i}" for i in range(1, 7)]
STRESS_FACTORS = {**{f"s{i}": "distancing" for i in (2, 3, 4)},
                  **{f"s{i}": "help_seeking" for i in (1, 5, 6)},
                  **{f"s{i}": "pressure" for i in (7, 8, 9)},
                  **{f"s{i}": "withdrawal" for i in range(10, 16)}}
COV = {"parent_age": "cov_parent_age", "parent_sex": "cov_parent_sex",
       "residence": "cov_residence", "education_level": "cov_education",
       "child_age": "cov_child_age", "child_sex": "cov_child_sex",
       "kindergarten_type": "cov_kindergarten_type"}
TABLES = {
    "szymanska_2017_parenting_difficulty": (TR, None),
    "szymanska_2017_child_representation": (R, None),
    "szymanska_2017_parent_stress_coping": (S, STRESS_FACTORS),
}


def convert() -> None:
    d = fetch()
    assert d.shape == (319, 44), d.shape

    # ---- books ---------------------------------------------------------------
    skip = {c: "squared Euclidean distance between two unreported ratings "
               "(computed discrepancy score, not a response)" for c in ROZB}
    acc = set(TR) | set(R) | set(S) | set(COV) | set(skip)
    assert set(d.columns) == acc, set(d.columns) ^ acc
    for c, why in skip.items():
        print(f"  skip {c}: {why}")
    for c in ROZB:
        v = d[c].dropna()
        assert (np.sqrt(v) == np.round(np.sqrt(v))).all(), c

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    # Three parents are 0 on all 31 items -- every difficulty, representation
    # AND all four opposed coping factors. The only full-row duplicates in the
    # file; read as blank-coded non-response, not answers. Dropped.
    allzero = (d[TR + R + S].fillna(0) == 0).all(axis=1)
    assert allzero.sum() == 3, allzero.sum()
    print(f"  drop {allzero.sum()} respondents who are 0 on all 31 items")
    d = d[~allzero].reset_index(drop=True)
    for c in ["parent_age", "parent_sex", "residence", "education_level"]:
        d.loc[d[c] == 0, c] = np.nan
    d.loc[d["parent_age"] < 18, "parent_age"] = np.nan
    d = d.rename(columns=COV)
    covs = list(COV.values())

    names = list(TABLES)
    assert len(set(names)) == len(names)
    for name, (items, constructs) in TABLES.items():
        long = d.melt(id_vars=["id"] + covs, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        assert (long["resp"] == long["resp"].round()).all(), name
        assert long["resp"].between(0, 10).all(), name
        long["resp"] = long["resp"].astype(int)
        t = long[["id", "item", "resp"] + covs].sort_values(
            ["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100, name
        # exact-duplicate response vectors (trust check)
        wide = t.pivot(index="id", columns="item", values="resp")
        print(f"  {name}: duplicate response vectors = {wide.duplicated().sum()}")

        checks = run_qc(t, item_constructs=constructs)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail}")
        ctx = {"item_constructs": constructs} if constructs else {}
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context=ctx)
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")

        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    convert()
