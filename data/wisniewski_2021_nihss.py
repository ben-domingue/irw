#!/usr/bin/env python3
# Source: https://zenodo.org/records/4536002
# DOI: 10.1371/journal.pone.0249211
#   Wisniewski, A., Filipska, K., Puchowska, M., Piec, K., Jaskolski, F.,
#   & Slusarz, R. (2021). Validation of a Polish version of the National
#   Institutes of Health Stroke Scale: Do moderate psychometric properties
#   affect its clinical utility? PLOS ONE, 16(4), e0249211.
#   (Data Availability statement points to this deposit; correction notice
#   10.1371/journal.pone.0270016 does not touch the data.)
# Data: Zenodo 4536002, six .xlsx files (all CC BY 4.0, Zenodo API):
#   - "baza NIHSS inter rater.xlsx": 225 patients x 15 items x 3 assessments.
#     THIS is what ships.
#   - "baza NIHSS intratarer.xlsx": 225 x 15 items x 2 (one rater's test and
#     3-hour retest). Not shipped: the paper says the retest rater is one of
#     the three inter-rater assessors, but the file does not say which, and
#     its first occasion does not equal any of the three inter-rater columns
#     for 5 patients, so it cannot be attached to a rater slot.
#   - "NIHSS cronbach overall/anterior/posterior.xlsx": one 15-item vector per
#     patient (matches an inter-rater column for 221/225 patients); the
#     anterior/posterior files renumber patients 1..n, so they cannot be
#     linked back. Not shipped.
#   - "NIHSS general.xlsx": covariates (code 1-225, same order as the other
#     files, asserted), GCS, Barthel and mRS.
# License: CC BY 4.0 (Zenodo API).
#
# Design (paper, Methods): 225 ischemic-stroke inpatients at one Polish stroke
# unit, Dec 2019 - Aug 2020. "Estimation of the inter-rater reliability of the
# PL-NIHSS was based on evaluations by three randomly selected researchers"
# out of four NIHSS-certified investigators, within 2 hours of each other.
# `rater` is the assessment SLOT (1, 2, 3) in the inter-rater file, not a
# stable person: the three were drawn at random from four per patient and the
# file does not record who. Agreement is near-total (99.9% of cells), which
# the paper's Table 3 corroborates (item ICCs 0.977-1.00).
#
# Items: the source headers are positional ("item 1 1", "item1 2", ...,
# "66 1", "15 3" = item k, slot r). Item codes are item1..item15 = the source
# item number k. Identity per the paper's Table 2 order, which lists the 15
# NIHSS items in the standard order:
#   item1 1a level of consciousness      0-3
#   item2 1b LOC questions               0-2
#   item3 1c LOC commands                0-2
#   item4 2  best gaze                   0-2
#   item5 3  visual fields               0-3
#   item6 4  facial palsy                0-3
#   item7 5a motor arm, left             0-4
#   item8 5b motor arm, right            0-4
#   item9 6a motor leg, left             0-4
#   item10 6b motor leg, right           0-4
#   item11 7 limb ataxia                 0-2
#   item12 8 sensory                     0-2
#   item13 9 best language               0-3
#   item14 10 dysarthria                 0-2
#   item15 11 extinction and inattention 0-2
# Permitted sets are the standard NIHSS scoring ranges (NINDS NIH Stroke
# Scale form), which the PL-NIHSS (paper S1 Table) keeps. The deposit's own
# header "66 1" for item 6 slot 1 is a typo (asserted by position).
#
# Item text: not shipped. No labels at either level (xlsx, positional
#   headers). The Polish PL-NIHSS wording is the paper's S1 Table (PDF).
#
# id: the deposit's patient code (1-225, a sequential study number). Kept as
#   the row index it already is.
# Covariates (from NIHSS general.xlsx): cov_age (years), cov_sex (M =
#   mezczyzna/male, K = kobieta/female; 120/105, matching the paper's Table 1).
#   Not carried: the anterior/posterior column (122/103 against the paper's
#   123/102, and its letter codes are undocumented), the stroke-type and
#   haemorrhage columns (undocumented codes that contradict the paper's
#   all-ischemic sample), and GCS/Barthel/mRS (other instruments' scores).

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASE = "https://zenodo.org/api/records/4536002/files/"
INTER = BASE + "baza%20NIHSS%20inter%20rater.xlsx/content"
GENERAL = BASE + "NIHSS%20general.xlsx/content"
TABLE = "wisniewski_2021_nihss"

RANGES = {1: 3, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 4, 10: 4,
          11: 2, 12: 2, 13: 3, 14: 2, 15: 2}


def fetch(url):
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), header=None)


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    inter = fetch(INTER)
    assert inter.shape == (231, 47), inter.shape
    hdr = [str(x).replace("item", "").split() for x in inter.iloc[3, 2:47]]
    # Header row: 15 items x 3 slots, in item-major order. "66 1" is item 6.
    expect = [(k, r) for k in range(1, 16) for r in range(1, 4)]
    got = [(int(h[0]) if h[0] != "66" else 6, int(h[1])) for h in hdr]
    assert got == expect, got
    body = inter.iloc[4:].copy()
    body = body[pd.to_numeric(body[0], errors="coerce").notna()]
    assert len(body) == 225
    codes = body[0].astype(int).tolist()
    assert codes == list(range(1, 226))
    assert body[1].isna().all()  # empty spacer column

    gen = fetch(GENERAL)
    assert gen.shape == (232, 24), gen.shape
    assert [str(x).strip() for x in gen.iloc[4, [11, 12]]] == ["age", "sex"]
    g = gen.iloc[5:]
    g = g[pd.to_numeric(g[1], errors="coerce").notna()]
    assert g[1].astype(int).tolist() == codes
    sex = g[12].map({"M": "male", "K": "female"})
    assert sex.notna().all() and (sex == "male").sum() == 120
    covs = pd.DataFrame({"id": codes,
                         "cov_age": pd.to_numeric(g[11]).astype(int).values,
                         "cov_sex": sex.values})

    rows = []
    for j, (k, r) in enumerate(expect):
        col = body.iloc[:, 2 + j]
        rows.append(pd.DataFrame({"id": codes, "item": f"item{k}",
                                  "resp": pd.to_numeric(col).values,
                                  "rater": r}))
    long = pd.concat(rows, ignore_index=True)
    assert long["resp"].notna().all()
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)

    pv = {f"item{k}": set(range(0, m + 1)) for k, m in RANGES.items()}
    for it, gi in long.groupby("item"):
        bad = set(gi["resp"]) - pv[it]
        assert not bad, (it, bad)

    long = long.merge(covs, on="id", how="left", validate="many_to_one")
    long = long[["id", "item", "resp", "cov_age", "cov_sex", "rater"]]
    long = long.sort_values(["id", "rater", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item", "rater"]).any()
    assert long["id"].nunique() == 225
    assert long["item"].nunique() == 15
    assert len(long) == 225 * 15 * 3

    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} raters={long['rater'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
