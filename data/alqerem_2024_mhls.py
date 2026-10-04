#!/usr/bin/env python3
# Source: https://zenodo.org/records/10781205
# DOI: 10.3389/fpubh.2024.1396255
#   Al-Qerem, Jarab, Khdour, Eberhardt et al. (2024). "Assessing mental health
#   literacy in Jordan: a factor analysis and Rasch analysis study." Frontiers
#   in Public Health 12. (Deposit: Al-Qerem, Walid, Zenodo 10781205.)
# Data: Zenodo 10781205, "mental health litracy.sav" (982 rows x 85 columns;
#       Google Forms survey of Jordanian adults, Arabic administration).
# License: CC BY 4.0 (Zenodo record licence, api record metadata).
#
# Item text: shipped (alqerem_2024_mhls__items.csv). Administered wording is
#   the Arabic variable labels of the 35 Google Forms text columns; English is
#   the variable labels of Q1-Q35; options are the Arabic answer strings, with
#   English from the Q-column value labels. Both label levels checked: variable
#   labels on all 35 items (English Q1/Q2 truncated at SPSS's 256-char limit,
#   so their item_text_translated is left blank), value labels on all 35.
#
# Table:
#   alqerem_2024_mhls   35 items  Mental Health Literacy Scale (O'Connor &
#                        Casey 2015), Jordanian Arabic version.
#                        Q1-Q10, Q13-Q15: 1-4 very unlikely .. very likely
#                        Q11-Q12:         1-4 very unhelpful .. very helpful
#                        Q16-Q28:         1-5 strongly disagree .. strongly agree
#                        Q29-Q35:         1-5 definitely unwilling .. willing
#                        (paper: first 15 items 4-point, the rest 5-point.)
#
# resp is derived from the ADMINISTERED Arabic answer text, not the deposit's
#   numeric Q columns, because two of those are miscoded:
#   - Q9 holds codes 1-6 under 1-4 value labels. It is an alphabetical
#     autorecode of the text column, which itself has two truncated strings:
#     1 = unlikely, 2 = "غير محتم" (truncation), 3 = very unlikely, 4 = likely,
#     5 = "محتمل جد" (truncation of very likely), 6 = very likely.
#   - Q8 has its two lowest categories swapped against its own labels
#     (1 = "unlikely", 2 = "very unlikely").
#   Every other item's code<->text crosstab is one-to-one (asserted), and the
#   authors' numeric columns for Q10, Q12, Q15, Q20-Q28 are REVERSE-scored
#   (value labels run very likely -> very unlikely). Coding from the text
#   gives raw, unreversed responses on one direction per format, as the MHLS
#   is published. Q9's "محتمل جد" (7 cells) is unambiguous and coded 4; its
#   "غير محتم" (8 cells) is a prefix of both "unlikely" and "very unlikely",
#   so those cells are NA.
#
# Dropped as items: Q1-Q35 numeric columns (superseded by the text, above);
#   A_Score, C_Score, BI_Score, BII_Score, Total_Score (authors' composites).
#
# Respondents: all 982 rows kept. The paper reports N = 974; the 8 extra rows
#   are the 8 with a blank gender, which the authors appear to have excluded
#   (not asserted -- the paper does not state the rule). They are kept and
#   flagged as cov_gender = NA.
# id: row index. The deposit's ID column has one duplicated value; it is
#   not carried. No names, contact details or free text exist in the file.
# Covariates: cov_age (as entered; includes an implausible 7, kept raw),
#   cov_gender (1 female, 2 male), cov_education (1 high school or less,
#   2 diploma, 3 bachelor's or higher), cov_married (1 other, 2 married),
#   cov_income (1 < 500 JOD, 2 500-1000, 3 > 1000) -- the deposit's own
#   English-coded covariates.

import os
import re
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
TEXT_DIR = REPO_ROOT / "automated_finding" / "itemtext_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/10781205/files/"
       "mental%20health%20litracy.sav/content")
TABLE = "alqerem_2024_mhls"

# Administered Arabic option strings, raw order, with the English anchors.
LIKELY = [("غير محتمل أبدا", "Very unlikely"), ("غير محتمل", "Unlikely"),
          ("محتمل", "Likely"), ("محتمل جدا", "Very likely")]
HELPFUL = [("غير مفيد أبدا", "Very unhelpful"), ("غير مفيد", "Unhelpful"),
           ("مفيد", "Helpful"), ("مفيد جدا", "Very helpful")]
AGREE = [("غير موافق أبدا", "Strongly disagree"), ("غير موافق", "Disagree"),
         ("محايد", "Neither agree or disagree"), ("موافق", "Agree"),
         ("موافق بشدة", "Strongly agree")]
WILLING = [("بالتأكيد غير مستعد", "Definitely unwilling"),
           ("ربما غير مستعدا", "Probably unwilling"),
           ("محايد", "Neither unwilling or willing"),
           ("ربما مستعدا", "Probably willing"),
           ("بالتأكيد مستعد", "Definitely willing")]


def fmt(k):
    if k in (11, 12):
        return HELPFUL
    if k <= 15:
        return LIKELY
    if k <= 28:
        return AGREE
    return WILLING


TRUNCATED_OK = {"محتمل جد": 4}        # unambiguous prefix of "محتمل جدا"
TRUNCATED_NA = {"غير محتم"}           # prefix of two different options

COVS = {"Age": "cov_age", "Gender": "cov_gender", "Education": "cov_education",
        "maritalstatus": "cov_married", "Income": "cov_income"}


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


def clean_label(s):
    s = (s or "").replace("\r", "").strip()
    s = re.sub(r"^\d+\.\s*", "", s)          # question numbering
    s = re.sub(r"^\[(.*)\]$", r"\1", s)      # Google Forms grid-row brackets
    return re.sub(r"\s{2,}", " ", s).strip()


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (982, 85), d.shape
    labels = meta.column_names_to_labels

    ar_cols = list(d.columns[6:41])            # administered text, items 1-35
    assert ar_cols[0].startswith("@1.") and ar_cols[14].startswith("@15.")
    q_cols = [f"Q{k}" for k in range(1, 36)]

    # Text <-> code must be one-to-one for every item except the two known
    # miscodings, which is what licenses reading resp off the text.
    for k, (a, q) in enumerate(zip(ar_cols, q_cols), 1):
        ct = pd.crosstab(d[a], d[q])
        one_to_one = ((ct > 0).sum(axis=1) == 1).all() and \
            ((ct > 0).sum(axis=0) == 1).all()
        assert one_to_one, q
        assert ct.values.sum() == len(d), q

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    # Balance the books: every column is shipped, a covariate, or named.
    composites = {"A_Score", "C_Score", "BI_Score", "BII_Score", "Total_Score"}
    ar_covs = {"الجنس", "المستوىالتعليمي", "الحالةالاجتماعية", "الدخلالشهري"}
    accounted = set(ar_cols) | set(q_cols) | composites | ar_covs \
        | set(cov_cols) | {"id", "ID"}
    assert set(d.columns) == accounted, set(d.columns) ^ accounted

    rows = []
    for k, a in enumerate(ar_cols, 1):
        code = {t: i for i, (t, _) in enumerate(fmt(k), 1)}
        code.update(TRUNCATED_OK if k == 9 else {})
        vals = d[a].astype(str)
        unknown = set(vals) - set(code) - (TRUNCATED_NA if k == 9 else set())
        assert not unknown, (k, unknown)
        resp = vals.map(code)
        part = d[["id"] + cov_cols].copy()
        part["item"] = f"Q{k}"
        part["resp"] = resp
        rows.append(part)
    long = pd.concat(rows, ignore_index=True)
    assert long["resp"].isna().sum() == 8           # the Q9 "غير محتم" cells
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    for c in cov_cols:
        long[c] = long[c].astype("Int64")

    pv = {f"Q{k}": set(range(1, len(fmt(k)) + 1)) for k in range(1, 36)}
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - pv[it]
        assert not bad, (it, bad)
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100 and long["item"].nunique() == 35

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

    # Item text: Arabic administered wording, English in _translated.
    text = []
    for k, a in enumerate(ar_cols, 1):
        en = clean_label(labels[f"Q{k}"])
        if k in (1, 2):
            en = ""          # English label truncated at 256 chars in the .sav
        for i, (ar_opt, en_opt) in enumerate(fmt(k), 1):
            text.append({
                "table": TABLE, "section_id": f"{TABLE}_1", "item": f"Q{k}",
                "instrument": "Mental Health Literacy Scale (MHLS), "
                              "Jordanian Arabic version",
                "language": "Arabic", "instructions": "",
                "section_prompt": "", "item_text": clean_label(labels[a]),
                "item_text_translated": en, "correct_response": "",
                "option_text": ar_opt, "option_text_translated": en_opt,
                "resp": i})
    tx = pd.DataFrame(text)
    assert set(tx["item"]) == set(long["item"])
    assert set(tx["resp"]) == set(long["resp"])
    tx.to_csv(TEXT_DIR / f"{TABLE}__items.csv", index=False)
    print(f"{TABLE}__items.csv: rows={len(tx)}")


if __name__ == "__main__":
    convert()
