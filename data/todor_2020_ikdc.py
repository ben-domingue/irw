#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC7003694
# DOI: 10.7717/peerj.8448
#   "Cross-cultural adaptation and validation of the Romanian International
#   Knee Documentation Committee-subjective knee form" (Todor, Vermesan,
#   Haragus, Patrascu, Timar & Cosma, 2020), PeerJ 8:e8448.
# Data: Supplemental File peerj-08-8448-s002.xlsx (Sheet1, 110 rows x 47;
#       Sheet2/Sheet3 empty), fetched from the Europe PMC supplementaryFiles
#       zip. s001.docx is the Romanian IKDC form.
# License: CC BY 4.0 (PeerJ article and supplements; Europe PMC "cc by").
#
# Item text: available, not shipped here -- the administered Romanian wording
#   of all items and their anchors is in s001.docx ("IKDC CHESTIONAR DE
#   EVALUARE A GENUNCHIULUI"); the data columns are bare codes (Q1..Q102).
#   English source: IKDC Subjective Knee Evaluation Form (Irrgang et al. 2001).
#
# Table: todor_2020_ikdc -- the 18 scored items of the IKDC subjective knee
#   form, with wave 1 = first administration (Q* columns, N = 105) and wave 2 =
#   retest after ~4 days (q* columns, N = 55 of the same patients).
#     ikdc_1 (0-4)  highest activity level without significant pain
#     ikdc_2 (0-10) pain frequency       ikdc_3 (0-10) pain severity
#     ikdc_4 (0-4)  stiffness/swelling   ikdc_5 (0-4) activity w/o swelling
#     ikdc_6 (0/1)  locking/catching     ikdc_7 (0-4) activity w/o giving way
#     ikdc_8 (0-4)  regular activity level
#     ikdc_9a..9i (0-4) difficulty with stairs up/down, kneeling, squatting,
#                   sitting with knee bent, rising from a chair, running
#                   straight ahead, jumping/landing, stopping/starting
#     ikdc_10b (0-10) current knee function (Q102; the pre-injury rating,
#                   item 10a, is not scored and not in the deposit)
#   Codes are as deposited (the form's own scoring direction; not reversed).
#   The paper reports 106 analysable data sets; 105 rows carry first-
#   administration item responses, and 4 further rows carry only the retest
#   block (kept, wave 2 only), so N = 109 ids. One row has a total score but
#   no item responses and contributes nothing.
# No imputation (all integers), no exact-duplicate rows. No PII: age and sex
#   only (no names, record numbers or dates).

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
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ZIP_URL = ("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7003694/"
           "supplementaryFiles")
FNAME = "peerj-08-8448-s002.xlsx"
TABLE = "todor_2020_ikdc"

SRC = ["1", "2", "3", "4", "5", "6", "7", "8", "91", "92", "93", "94", "95",
       "96", "97", "98", "99", "102"]
NAME = {s: f"ikdc_{s}" for s in SRC[:8]}
NAME.update({f"9{i}": f"ikdc_9{c}" for i, c in zip(range(1, 10), "abcdefghi")})
NAME["102"] = "ikdc_10b"
PERM = {"ikdc_2": range(0, 11), "ikdc_3": range(0, 11),
        "ikdc_10b": range(0, 11), "ikdc_6": range(0, 2)}
COVS = {"varsta": "cov_age", "sex": "cov_sex"}
SKIP = {
    "Tegner": "Tegner-Lysholm knee score (total of another instrument)",
    "IKDC": "IKDC total score (wave 1)",
    "ikdc2": "IKDC total score (retest)",
    "KOOS": "KOOS JR total score",
    "Index": "EQ-5D-5L index value",
    "VAS": "EQ-5D VAS (single rating, other instrument)",
    "Mi": "clinical grading column, not a questionnaire response",
    "Me": "clinical grading column, not a questionnaire response",
    "Cartilaj": "cartilage lesion grade (clinical), not a questionnaire "
                "response",
}


def convert() -> None:
    r = requests.get(ZIP_URL, headers=UA, timeout=120)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        d = pd.read_excel(io.BytesIO(z.read(FNAME)), sheet_name="Sheet1")
    assert d.shape == (110, 47), d.shape

    w1 = [f"Q{s}" for s in SRC]
    w2 = [f"q{s}" for s in SRC]
    # ---- books ---------------------------------------------------------
    acc = set(w1) | set(w2) | set(COVS) | set(SKIP)
    assert set(d.columns) == acc and len(d.columns) == len(acc), \
        set(d.columns) ^ acc
    for c, why in SKIP.items():
        print(f"  skip {c}: {why}")

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())
    # 4 rows (source rows 81, 95-97) carry only the retest block; they are
    # kept as wave-2-only respondents. Row alignment of the two blocks is
    # confirmed by the deposited totals: corr(IKDC, ikdc2) = 0.84 over the 50
    # rows with both, matching the paper's r = 0.816 (n = 50).
    only2 = d[w2].notna().any(axis=1) & d[w1].isna().all(axis=1)
    assert only2.sum() == 4, only2.sum()
    both = d.dropna(subset=["IKDC", "ikdc2"])
    assert len(both) == 50 and both["IKDC"].corr(both["ikdc2"]) > 0.8

    parts = []
    for wave, cols in [(1, w1), (2, w2)]:
        sub = d[["id"] + cov_cols + cols].rename(
            columns={c: NAME[c[1:]] for c in cols})
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=list(NAME.values()),
                        var_name="item", value_name="resp")
        long["wave"] = wave
        parts.append(long)
    t = pd.concat(parts, ignore_index=True).dropna(subset=["resp"])
    assert (t["resp"] % 1 == 0).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp", "wave"] + cov_cols]
    t = t.sort_values(["id", "wave", "item"]).reset_index(drop=True)
    assert not t.duplicated(["id", "item", "wave"]).any()
    assert t["id"].nunique() >= 100, t["id"].nunique()

    pv = {i: set(PERM.get(i, range(0, 5))) for i in NAME.values()}
    for i, s in pv.items():
        bad = set(t.loc[t["item"] == i, "resp"]) - s
        assert not bad, (i, bad)
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    t.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    waves = t.groupby("wave")["id"].nunique().to_dict()
    print(f"{TABLE}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-"
          f"{t['resp'].max()} waves={waves}")


if __name__ == "__main__":
    convert()
