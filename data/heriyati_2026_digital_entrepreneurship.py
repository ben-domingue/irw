#!/usr/bin/env python3
# Source: https://zenodo.org/records/20199216
# DOI: 10.5281/zenodo.20199216 (dataset; no paper DOI found)
#   Heriyati, Pantri & Aguzman, Glory (2026). "The Role of Digital Literacy in
#   Shaping Entrepreneurial Intention among University Students" [data set], Zenodo.
# Data: the deposit's single xlsx, sheet "Form Responses 1": 100 young
#       entrepreneurs (graduates with >= 3 years running a business, Greater
#       Jakarta) x 66 Google-Forms columns: Timestamp, two screening questions,
#       nine profile questions, then 54 Likert items whose headers are the full
#       Indonesian item stems.
# License: CC BY 4.0 (Zenodo record).
#
# Tables: the record description names six constructs, "measured on a Likert scale
#   ranging from strongly disagree to strongly agree"; the 54 item columns fall in
#   six consecutive blocks of nine, and each block's stems read as its construct
#   (checked by reading every header):
#   heriyati_2026_digital_info_literacy     DIL1-9  (searching/evaluating business information)
#   heriyati_2026_digital_networking        DNC1-9  (communicating/networking via digital media)
#   heriyati_2026_entrepreneurship_edu      EEE1-9  ("Saat kuliah, ..." course/mentoring exposure)
#   heriyati_2026_digital_safety            DSR1-9  (digital security, fraud, privacy)
#   heriyati_2026_entrepreneurial_se        ESE1-9  (confidence in business tasks)
#   heriyati_2026_entrepreneurial_intention EI1-9   (intent to grow the business)
#   Item code = construct prefix + position within the block; the script asserts
#   the first stem of every block so the tie between code and header is checked,
#   not assumed. Responses 1-5 (observed 1-5; strong ceiling, most answers 4-5).
# Covariates: graduation recency, gender, business sector, location, employees,
#   monthly turnover, digital tools used, years in business, digital use in college
#   (Indonesian labels, "□ " stripped).
#   Timestamp and the two constant screening answers dropped.
#
# Item text: not shipped. Levels checked: xlsx, no labels; the column headers ARE
#   the administered Indonesian stems (cheap, data_labels/study_materials) --
#   left for a later pass; no English version in the deposit.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "heriyati_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/20199216/files/The%20Role%20of%20Digital%20Literacy"
       "%20in%20Shaping%20Entrepreneurial%20Intention%20among%20University%20Students.xlsx/content")

BLOCKS = [  # (table, prefix, start of first stem in the block)
    ("heriyati_2026_digital_info_literacy", "DIL", "Saya mampu mencari informasi bisnis"),
    ("heriyati_2026_digital_networking", "DNC", "Saya berkomunikasi secara efektif"),
    ("heriyati_2026_entrepreneurship_edu", "EEE", "Saat kuliah, Saya mengikuti mata kuliah"),
    ("heriyati_2026_digital_safety", "DSR", "Saat ini Saya memahami risiko keamanan"),
    ("heriyati_2026_entrepreneurial_se", "ESE", "Saya mampu mengidentifikasi peluang bisn"),
    ("heriyati_2026_entrepreneurial_intention", "EI", "Saya berniat terus mengembangkan usaha"),
]
COV_NAMES = ["cov_graduated", "cov_gender", "cov_sector", "cov_location", "cov_employees",
             "cov_turnover", "cov_digital_tools", "cov_years_business", "cov_digital_in_college"]


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="Form Responses 1")
    assert d.shape == (100, 66), d.shape
    cols = d.columns.tolist()
    for c in cols[1:3]:  # screening questions: constant "Ya"
        assert d[c].nunique() == 1
    covsrc = cols[3:12]
    assert len(covsrc) == len(COV_NAMES)
    item_cols = cols[12:]
    assert len(item_cols) == 54
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    for src, new in zip(covsrc, COV_NAMES):
        d[new] = d[src].astype(str).str.replace("□", "", regex=False).str.strip()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for b, (name, prefix, first) in enumerate(BLOCKS):
        block = item_cols[9 * b: 9 * b + 9]
        assert block[0].strip().startswith(first), (name, block[0])
        ren = {c: f"{prefix}{k + 1}" for k, c in enumerate(block)}
        t = d.rename(columns=ren).melt(id_vars=["id"] + COV_NAMES, value_vars=list(ren.values()),
                                       var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"])
        assert t["resp"].isin(range(1, 6)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + COV_NAMES].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: {1, 2, 3, 4, 5} for i in ren.values()}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
