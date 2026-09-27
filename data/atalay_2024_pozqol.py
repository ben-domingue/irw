#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11344534
# DOI: 10.7717/peerj.17873
#   "Validation of PozQoL scale in Turkish population living with HIV: a
#   cross-cultural adaptation study" (Atalay, Varol, Singil & Sonmez, 2024),
#   PeerJ 12:e17873.
# Data: PeerJ Supplemental Information 2 "Raw data in English",
#       peerj-12-17873-s002.sav (130 x 43: covariates, Q1-Q13 at test (R1) and
#       at the 4-week retest (R2), totals and subscale scores). Supplemental
#       Information 1 (s001.sav, Turkish variable names) holds the test items
#       only and is asserted identical to the R1 block. Both fetched from the
#       Europe PMC supplementaryFiles zip.
# License: CC BY 4.0 (PeerJ article; Europe PMC license "cc by"). Article-
#          attached SI, so the article licence is the source licence.
#
# Item text: available, not shipped here -- Supplemental Information 3
#   (peerj-12-17873-s003.pdf) is the full Turkish form: instruction, the five
#   anchors (1 hic, 2 ara sira, 3 bazen, 4 cogunlukla, 5 her zaman) and all 13
#   item stems in order; .sav labels are positional ("Question1 first reply").
#   Administered in Turkish. English stems: the original PozQoL (Brown et al.
#   2018).
#
# Table: atalay_2024_pozqol -- 13 items, 1-5, wave 1 = test, wave 2 = retest
#   4 weeks later ("comparing all the participants' initial test results with
#   a retest performed 4 weeks later"; no blanks in either block).
#   The negatively worded items (2,3,4,6,7,9,10,11,12) are stored ALREADY
#   REVERSE-SCORED: no inter-item correlation is negative (min ~0.00, Q5-Q9), and the deposited
#   subscale scores equal plain sums of the items (asserted). Kept as deposited:
#   higher = better quality of life on every item.
#   Subscales (from the deposited subscale columns, matched exactly):
#   psychological Q1/Q5/Q8/Q13, health concerns Q2/Q7/Q12, social Q3/Q9/Q11,
#   functional Q4/Q6/Q10.
#
# Anomaly, recorded not repaired: TEST1_TOTAL_SCORE equals the R1 item sum for
# only 46/130 rows, while s001's own total (`toplam`), the four first-test
# subscale columns and Test2TOTALSCORE all match their items exactly. The item
# block is internally consistent; the one stray total column is skipped.
#
# PII: `register_no` ("register number of participants", 21-682, not unique)
# is the clinic's participant number. It is never output: id is the row index.
# ben-domingue ruled 2026-09-26 that a clinic register number is neutralised,
# not disqualifying. It is not hashed: its range is only 21-682, so any hash
# could be reversed by trying every value. No names, dates or contact data.

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
SUPP = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11344534/supplementaryFiles"
SAV_EN = "peerj-12-17873-s002.sav"
SAV_TR = "peerj-12-17873-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
NAME = "atalay_2024_pozqol"


def fetch() -> dict:
    for attempt in range(5):
        r = requests.get(SUPP, headers=UA, timeout=120)
        if r.status_code == 200 and r.content[:2] == b"PK":
            out = {}
            with zipfile.ZipFile(BytesIO(r.content)) as z:
                for want in (SAV_EN, SAV_TR):
                    name = next(n for n in z.namelist() if n.endswith(want))
                    tmp = OUT_DIR / f".tmp_{want}"
                    tmp.write_bytes(z.read(name))
                    try:
                        out[want], _ = pyreadstat.read_sav(str(tmp))
                    finally:
                        tmp.unlink()
            return out
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"{SUPP} did not return a zip after 5 attempts")


R1 = [f"Q{i}R1" for i in range(1, 14)]
R2 = [f"Q{i}R2" for i in range(1, 14)]
SUBSCALES = {"PSYCHOLOGICAL": (1, 5, 8, 13), "HEALTH": (2, 7, 12),
             "SOCIAL": (3, 9, 11), "FUNCTIONALE": (4, 6, 10)}
CONSTRUCT = {f"pozqol_{i}": k.lower().replace("functionale", "functional")
             for k, v in SUBSCALES.items() for i in v}
COV = {"age": "cov_age", "gender": "cov_gender", "education": "cov_education",
       "marital_status": "cov_marital_status",
       "HIV_diagnosis_period_months": "cov_hiv_diagnosis_months",
       "ART_period_months": "cov_art_months"}
SKIP = {
    "register_no": "clinic participant number -- replaced by the row index",
    "TEST1_TOTAL_SCORE": "total score (composite; also inconsistent with items)",
    "Test2TOTALSCORE": "total score (composite)",
    **{c: "subscale score (composite)" for c in
       ["SOCIAL", "HEALTH", "PSYCHOLOGICAL", "FUNCTIONALE", "HEALTH2",
        "PSYCHOLOGİCAL2", "SOCIAL2", "FUNCTIONALE2"]},
}


def convert() -> None:
    f = fetch()
    b, a = f[SAV_EN], f[SAV_TR]
    assert b.shape == (130, 43) and a.shape == (130, 18), (b.shape, a.shape)
    acc = set(R1) | set(R2) | set(COV) | set(SKIP)
    assert set(b.columns) == acc, set(b.columns) ^ acc
    for c, why in SKIP.items():
        print(f"  skip {c}: {why}")

    # s001 (Turkish) test block == s002 R1 block; subscales/totals as documented
    assert (a[[f"S{i}Y1" for i in range(1, 14)]].values == b[R1].values).all()
    assert (a["toplam"] == b[R1].sum(axis=1)).all()
    assert (b["Test2TOTALSCORE"] == b[R2].sum(axis=1)).all()
    for sc, idx in SUBSCALES.items():
        assert (b[sc] == b[[f"Q{i}R1" for i in idx]].sum(axis=1)).all(), sc
    assert b[R1].corr().values.min() > -0.05  # negatives already reversed

    b = b.reset_index(drop=True)
    b["id"] = b.index + 1
    b = b.rename(columns=COV)
    for c in ["cov_education", "cov_marital_status"]:
        b[c] = pd.to_numeric(b[c])
    covs = list(COV.values())

    parts = []
    for wave, cols in ((1, R1), (2, R2)):
        w = b[["id"] + covs + cols].rename(
            columns={c: f"pozqol_{i}" for i, c in enumerate(cols, 1)})
        w = w.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        w["wave"] = wave
        parts.append(w)
    t = pd.concat(parts, ignore_index=True).dropna(subset=["resp"])
    assert (t["resp"] == t["resp"].round()).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp", "wave"] + covs].sort_values(
        ["id", "wave", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item", "wave"]).any()
    assert t["id"].nunique() >= 100

    pv = {i: set(range(1, 6)) for i in CONSTRUCT}  # form: 1 hic ... 5 her zaman
    for i, s in pv.items():
        bad = set(t.loc[t["item"] == i, "resp"]) - s
        assert not bad, (i, bad)
    checks = run_qc(t, permitted_values=pv, item_constructs=CONSTRUCT)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        t, label=NAME, profile="upload",
        context={"permitted_values": pv, "item_constructs": CONSTRUCT})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")

    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()} "
          f"waves={t.groupby('wave')['id'].nunique().to_dict()}")


if __name__ == "__main__":
    convert()
