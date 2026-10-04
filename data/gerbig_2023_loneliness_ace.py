#!/usr/bin/env python3
# Source: https://zenodo.org/records/7749115
# DOI: 10.1136/bmjopen-2024-088098
#   Gerbig, P., Reinhard, M. A., Ababu, H., Rek, S., Amann, B. L.,
#   Adorjan, K., Abera, M., Padberg, F., & Jobst, A. (2025). Are loneliness
#   and social network size mediators between childhood adversity and
#   depressive symptoms? A cross-sectional replication study in Ethiopia.
#   BMJ Open, 15(8), e088098. (PMC12359536; its data availability statement
#   cites this deposit. Preprint: 10.21203/rs.3.rs-2972638/v1.)
# Data: Zenodo 7749115, Loneliness_ACE_Ethiopia_Jimma.sav (256 rows x 135
#       columns) + Codebook_Dataset_Loneliness_ACE_Ethiopia.pdf.
# License: CC BY 4.0 (Zenodo API).
#
# Sample (paper): 125 psychiatric outpatients at Jimma University Medical
# Center (major depressive, bipolar or psychotic disorders) and 131
# non-clinical participants, interviewed by trained mental health
# professionals; questionnaires translated to Afan Oromo and Amharic.
#
# Item text: not shipped. Both label levels checked: the .sav has no value
#   labels on any item; its variable labels are truncated ENGLISH fragments of
#   each stem ("in tune with the people around me.*", "felt loved."), the same
#   fragments the codebook PDF prints. The administered Afan Oromo / Amharic
#   wording is not in the deposit or the paper. WHO-5 is a rights-register
#   block; the CTQ-SF is a commercially published instrument.
#
# Tables (item codes are the source column names; ranges from the deposit
# codebook and the paper's Measures section):
#   gerbig_2023_ucla  IN .. THERE2 (20 items)  Revised UCLA Loneliness Scale,
#       1-4 (codebook "UCLA-LS: Revised UCLA Loneliness Scale: 1-4"). Stored
#       UNREVERSED; the codebook's starred items are reverse-keyed.
#   gerbig_2023_ctq   DIDNT .. SOURCE (28 items)  Childhood Trauma
#       Questionnaire short form, 1-5 (codebook "1-5"; paper "1='never true'
#       to 5='very often true'"), incl. the three minimisation items
#       NOTHING1, HAD, BEST. Stored unreversed.
#   gerbig_2023_who5  CHEERFUL, CALM, ACTIVE, WOKE, LIFE1  WHO-5 Well-Being
#       Index, 0-5 (codebook "WHO 5 Wellbeing Index: 0-5").
#
# Dropped:
#   - R* reverse-coded copies: RIN .. RDO (= 5 - x, UCLA) and RSOMEONE ..
#     RTAKE (= 6 - x, CTQ); all asserted.
#   - Totals, subscale sums and prevalence flags: TUCLALS, TCTQSF,
#     EmoAbCTQ .. SexAbCTQ, TWHO5, ITWHO5, SNI, negSNI, Prev*, UCLAhigh. The
#     UCLA, CTQ (25 non-minimisation items) and WHO-5 totals equal the item
#     sums (asserted).
#   - The Social Network Index (N7 .. N28, SNI* scorings, THE, SUMMEMBERS):
#     counts of network members, not item responses. THE is a free-text group
#     name (only community savings / burial associations: edir, ekub).
# id: row index. The source ID column has three duplicated values (33, 120,
#   135) on rows that differ in demographics or items (data-entry
#   collisions); the paper's N is 256 = 125 + 131, matching the row count.
# Covariates: cov_age (years), cov_sex (1 male, 2 female), cov_education
#   (codebook 1/2 illiterate / read-write only .. 6 degree and above),
#   cov_occupation (1-7 per codebook), cov_income_etb (ETB per month),
#   cov_address (1 Jimma town, 2 Woreda town), cov_clinical (1 patient,
#   2 healthy participant), cov_diagnosis (0 none, 1 MDD, 2 bipolar,
#   3 psychotic), cov_illness_years (since diagnosis).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/7749115/files/"
       "Loneliness_ACE_Ethiopia_Jimma.sav/content")

UCLA = ["IN", "LACK", "NO1", "DO", "FEEL", "LOT", "NO2", "INTERESTS", "AN2",
        "ARE", "FEEL1", "SOCIAL", "NO3", "FEEL2", "CAN", "THERE", "UNHAPPY",
        "PEOPLE2", "THERE1", "THERE2"]
CTQ = ["DIDNT", "THERE3", "CALLED", "PARENT", "SOMEONE", "WEAR", "FELT1",
       "PARENTS", "GOT", "NOTHING1", "HIT", "PUNISHED", "FAMILY", "FAMILY1",
       "WAS", "HAD", "GOT1", "SOMEONE1", "FELT2", "TRIED", "THREATENED",
       "BEST", "MADE", "MOLESTED", "WAS1", "TAKE", "WAS2", "SOURCE"]
WHO5 = ["CHEERFUL", "CALM", "ACTIVE", "WOKE", "LIFE1"]
TABLES = {"gerbig_2023_ucla": (UCLA, range(1, 5)),
          "gerbig_2023_ctq": (CTQ, range(1, 6)),
          "gerbig_2023_who5": (WHO5, range(0, 6))}
UCLA_REV = {"RIN": "IN", "RFEEL": "FEEL", "RLOT": "LOT", "RAN2": "AN2",
            "RARE": "ARE", "RCAN": "CAN", "RTHERE": "THERE",
            "RTHERE1": "THERE1", "RTHERE2": "THERE2", "RDO": "DO"}
CTQ_REV = {"RSOMEONE": "SOMEONE", "RFELT1": "FELT1", "RFAMILY": "FAMILY",
           "RFELT2": "FELT2", "RSOURCE": "SOURCE", "RTHERE3": "THERE3",
           "RTAKE": "TAKE"}
MINIMISATION = ["NOTHING1", "HAD", "BEST"]
COMPOSITES = {"TUCLALS", "TCTQSF", "EmoAbCTQ", "EmoNeglCTQ", "PhyAbCTQ",
              "PhyNeglCTQ", "SexAbCTQ", "TWHO5", "ITWHO5", "SNI", "negSNI",
              "PrevEmoAb", "PrevEmoNegl", "PrevPhyAb", "PrevPhyNegl",
              "PrevSexAb", "PrevACE1", "PrevUCLA", "UCLAhigh"}
SNI_BLOCK = {"N7", "SNI1", "N8", "N2A", "SNI2A", "N15", "N3A", "SNI3A",
             "N19", "N4A", "SNI4A", "N21", "N5A", "SNI5A", "N22", "N6A",
             "SNI6A", "N23", "N7A", "SNI7A", "N24", "N8A", "SNI8A", "N25",
             "N9A", "SNI9A", "N9B", "SNI9B", "N26", "SNI10", "N27", "N11A",
             "SNI11A", "N28", "THE", "SUMMEMBERS"}
COVS = {"AGE": "cov_age", "SEX": "cov_sex", "EDUCATIONAL": "cov_education",
        "OCCUPATION": "cov_occupation", "INCOME": "cov_income_etb",
        "ADDRESS": "cov_address", "MENTAL": "cov_clinical",
        "DIAGNOSISSUB": "cov_diagnosis", "DURATION": "cov_illness_years"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (256, 135), d.shape

    # Balance the books.
    known = (set(UCLA) | set(CTQ) | set(WHO5) | set(UCLA_REV) | set(CTQ_REV)
             | COMPOSITES | SNI_BLOCK | set(COVS) | {"ID"})
    assert set(d.columns) == known, set(d.columns) ^ known

    for r, s in UCLA_REV.items():
        assert (d[r] == 5 - d[s]).all(), r
    for r, s in CTQ_REV.items():
        assert (d[r] == 6 - d[s]).all(), r
    ucla_scored = [c for c in UCLA if c not in UCLA_REV.values()] \
        + list(UCLA_REV)
    assert (d[ucla_scored].sum(axis=1) == d["TUCLALS"]).all()
    ctq_scored = [c for c in CTQ if c not in CTQ_REV.values()
                  and c not in MINIMISATION] + list(CTQ_REV)
    assert len(ctq_scored) == 25
    assert (d[ctq_scored].sum(axis=1) == d["TCTQSF"]).all()
    assert (d[WHO5].sum(axis=1) == d["TWHO5"]).all()
    assert (d["MENTAL"] == 1).sum() == 125 and (d["MENTAL"] == 2).sum() == 131
    assert d["ID"].duplicated().sum() == 3
    assert not d.drop(columns=["ID"]).duplicated().any()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, (its, rng) in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        allowed = set(rng)
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
