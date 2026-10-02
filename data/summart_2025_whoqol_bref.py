#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.28136420.v2
# DOI: 10.12688/f1000research.161251.3
#   Summart, U. et al. (2025). "Validation of the Thai version of the World
#   Health Organization's Quality of Life Scale (WHOQOL-BREF-THAI) among Thai
#   nursing students in northeast Thailand: A multi-centre study."
#   F1000Research 14, 161251 (v3; PMC12770885).
# Data: figshare 28136420 v2, DATA.xlsx (one sheet, NO header row: 3,570
#       rows x 38 columns; Thai nursing students at 15 institutions,
#       2023). The deposit also holds the Thai questionnaire PDF
#       (แบบสอบถาม_NCDs_แก้ไข.pdf) and an English WHOQOL-BREF item list.
# License: CC BY 4.0 (figshare API, article 28136420).
#
# Item text: not shipped. The xlsx has no labels at either level (no header
#   row at all, so no variable names; no value labels in a spreadsheet). The
#   Thai stems are in the deposit's questionnaire PDF, part 6 (items 1-26,
#   anchors ไม่เลย .. มากที่สุด); the column -> item tie below is positional
#   plus the domain-structure check, so it would need a verify script.
#
# Columns (positional; the file has no header):
#   0      row number 1..3570 -> dropped (replaced by our own row index)
#   1-6    gender, age, academic year, GPA, institution, residence (identified
#          against the paper's Table 1: 3,295 women coded 1; years 1-4 =
#          1,208/1,060/761/541; 2,567 living on campus coded 1)
#   7      monthly income (baht; values such as 2.79 and 120000 fall outside
#          the paper's 1,000-18,000 range) -> dropped
#   8      smoking, 0 never / 1-2 ever (128 ever, matching Table 1; which of
#          1/2 is current vs quit is undocumented) -> cov_smoking, raw codes
#   9-11   two 0/1 flags and a 0-25 count that match nothing in Table 1
#          (alcohol is 1,013 in the paper, 1,131 in column 10) -> dropped
#   12-37  the 26 WHOQOL-BREF-THAI items, in the order of the deposit's Thai
#          questionnaire (q1 .. q26). This is the Thai form's own order, not
#          the international one. The tie is positional, and it is supported
#          by structure: the Thai form's physical items (q2, q3, q4, q10,
#          q11, q12, q24), psychological items (q5-q9, q23), social items
#          (q13, q14, q25) and environment items (q15-q22) each form their
#          own correlation cluster.
#   Thai -> international WHOQOL-BREF numbering: q1=Q2 health satisfaction,
#   q2=Q3 pain, q3=Q10 energy, q4=Q16 sleep, q5=Q5 enjoy life,
#   q6=Q7 concentration, q7=Q19 self-satisfaction, q8=Q11 bodily appearance,
#   q9=Q26 negative feelings, q10=Q17 daily activities, q11=Q4 medical
#   treatment, q12=Q18 work capacity, q13=Q20 personal relationships,
#   q14=Q22 friend support, q15=Q8 safety, q16=Q23 living place,
#   q17=Q12 money, q18=Q24 health services, q19=Q13 information,
#   q20=Q14 leisure, q21=Q9 physical environment, q22=Q25 transport,
#   q23=Q6 meaningful life, q24=Q15 mobility, q25=Q21 sex life,
#   q26=Q1 overall QOL.
#
# Response format (paper): 5-point, 1-5. The paper reverses Q3, Q4 and Q26
#   (Thai q2, q11, q9) before scoring. Here those three correlate POSITIVELY
#   with the other items of their domain, so the file holds them after that
#   reversal. They are kept as stored.
#
# Cleaning:
#   - q14 (friend support) and q25 (sex life) are identical in all 3,570
#     rows (asserted), so one column is a copy of the other. The file does
#     not say which item the values belong to, so both are dropped.
#   - 7 rows are exact copies of an earlier row in every column but the row
#     number (asserted); the later copy is dropped -> 3,563 ids.
#   - Age outside 17-40 (e.g. 2, 13, 2546; the paper's range is 18-35) and
#     GPA outside 0-4 (e.g. 350) are covariate entry errors -> NA.
#
# id: row index after de-duplication.
# Covariates: cov_gender (1 female, 0 male), cov_age, cov_year (1-4),
#   cov_gpa, cov_institution (code, 15 institutions), cov_residence (1 campus
#   dorm, 2 off-campus dorm, 3 own home, 4 other, per questionnaire order),
#   cov_smoking (see above).

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
URL = "https://ndownloader.figshare.com/files/51480161"
TABLE = "summart_2025_whoqol_bref"

ITEM_COLS = {12 + k - 1: f"q{k}" for k in range(1, 27)}
DUPLICATED_PAIR = ("q14", "q25")
COVS = {1: "cov_gender", 2: "cov_age", 3: "cov_year", 4: "cov_gpa",
        5: "cov_institution", 6: "cov_residence", 8: "cov_smoking"}
DROPPED = {0: "row number", 7: "income (out-of-range values)",
           9: "unidentified 0/1 flag", 10: "unidentified 0/1 flag",
           11: "unidentified 0-25 count"}
DOMAINS = {"physical": ["q2", "q3", "q4", "q10", "q11", "q12", "q24"],
           "psych": ["q5", "q6", "q7", "q8", "q9", "q23"],
           "env": [f"q{k}" for k in range(15, 23)]}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), header=None)


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d = load()
    assert d.shape == (3570, 38), d.shape
    assert (d[0] == range(1, 3571)).all()
    known = set(ITEM_COLS) | set(COVS) | set(DROPPED)
    assert known == set(d.columns), known ^ set(d.columns)
    for c, why in DROPPED.items():
        print(f"  dropped column {c}: {why}")

    # Table 1 checks that pin the covariate columns.
    assert (d[1] == 1).sum() == 3295
    assert d[3].value_counts().to_dict() == {1: 1208, 2: 1060, 3: 761,
                                             4: 541}
    assert (d[6] == 1).sum() == 2567
    assert (d[8] > 0).sum() == 128

    d = d.rename(columns={**ITEM_COLS, **COVS})
    items = list(ITEM_COLS.values())
    a, b = DUPLICATED_PAIR
    assert (d[a] == d[b]).all()

    # Domain structure: every within-domain correlation is positive, and
    # each domain hangs together far more than it does with the others.
    r = d[items].corr()
    for dom, its in DOMAINS.items():
        sub = r.loc[its, its]
        assert (sub.values > 0.25).all(), dom
        others = [i for i in items if i not in its and i not in ("q1", "q26")]
        assert sub.values.mean() > r.loc[its, others].values.mean() + 0.2, dom

    dup = d.drop(columns=[0]).duplicated()
    assert dup.sum() == 7
    d = d[~dup].reset_index(drop=True)

    d.loc[~d["cov_age"].between(17, 40), "cov_age"] = pd.NA
    d.loc[~d["cov_gpa"].between(0, 4), "cov_gpa"] = pd.NA

    keep = [i for i in items if i not in DUPLICATED_PAIR]
    d.insert(0, "id", d.index + 1)
    cov_cols = list(COVS.values())
    long = d.melt(id_vars=["id"] + cov_cols, value_vars=keep,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    allowed = set(range(1, 6))
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - allowed
        assert not bad, (it, bad)
    pv = {i: allowed for i in keep}

    long = long[["id", "item", "resp"] + cov_cols]
    for c in ("cov_gender", "cov_age", "cov_year", "cov_institution",
              "cov_residence", "cov_smoking"):
        long[c] = long[c].astype("Int64")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() == 3563
    assert long["item"].nunique() == 24

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
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
