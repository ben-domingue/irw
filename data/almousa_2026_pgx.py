#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/PGx_knowledge_and_Attitude_in_Jordan/31436659
# DOI: 10.6084/m9.figshare.31436659.v1 (data)
#   Almousa A (2026). PGx knowledge and Attitude in Jordan [Data set]. figshare.
# License: CC BY 4.0 (figshare record)
# Data: "Assessing Pharmacogenetics among students version_Final.xlsx", 279 third-year-and-above
#   pharmacy and medical students at Jordanian universities (survey March-September 2025). The
#   workbook's legend columns give the coding: basic-knowledge statements scored by the depositors as
#   Right answer = 1, Wrong answer = -1, Not sure = 0; "familiar to you" statements I Know = 1,
#   I Don't Know/Not Sure = 0; attitude statements Strongly agree = 2 .. Strongly disagree = -2;
#   confidence questions Very Confident = 2 .. -2.
# Item codes: headers are statements, so items are coded by block and column order (k1-k8, f1-f5,
#   a1-a4, c1-c4); the script asserts the first statement of each block.
# Tables:
#   almousa_2026_pgx_knowledge   -- k1-k8 true/false/not sure statements. resp = 1 if scored right,
#     0 if wrong or not sure (resp_raw keeps the depositors' 1/0/-1).
#   almousa_2026_pgx_familiarity -- f1-f5 advanced statements (warfarin/CYP2C9, clopidogrel/CYP2C19,
#     DPYD, TPMT, acetaminophen), 1 = "I know", 0 = don't know / not sure.
#   almousa_2026_pgx_attitudes   -- a1-a4, stored -2..2, shifted to 1-5 (1 = strongly disagree).
#   almousa_2026_pgx_confidence  -- c1-c4, stored -2..2, shifted to 1-5 (5 = very confident).
# Covariates: cov_academic_year, cov_sex, cov_major, cov_gpa_band, cov_heard_of_pgx.
# Not carried: university (free-typed), knowledge source and learning-preference multi-selects, the
#   two single 1-5 questions.
# Item text: not shipped -- the statements are the headers, but the questionnaire is described as
#   validated and adapted from earlier PGx surveys that have not been identified.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://ndownloader.figshare.com/files/62259976"
BLOCKS = [("k", 9, 8, "Pharmacogenetics is the study"), ("f", 17, 5, "Patients with CYP2C9"),
          ("a", 22, 4, "I may consider pharmacogenetics"), ("c", 26, 4, "Interpreting PGx test")]


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert len(d) == 279 and d["Response No."].is_unique
    cols = list(d.columns)
    rename = {}
    for pre, start, n, first in BLOCKS:
        assert str(cols[start]).startswith(first), (pre, cols[start])
        for i in range(n):
            rename[cols[start + i]] = f"{pre}{i + 1}"
    d = d.rename(columns=rename)
    d["id"] = d["Response No."]
    d["cov_academic_year"] = d["Academic year"]
    d["cov_sex"] = d["Sex:"]
    d["cov_major"] = d["Major "].str.strip()
    d["cov_gpa_band"] = d["Academic Grade (GPA):"]
    d["cov_heard_of_pgx"] = d["Have you ever heard about pharmacogenetics before?"]
    covs = ["cov_academic_year", "cov_sex", "cov_major", "cov_gpa_band", "cov_heard_of_pgx"]

    def long(items):
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp_raw")
        return t.dropna(subset=["resp_raw"])

    out = {}
    t = long([f"k{i}" for i in range(1, 9)])
    assert t["resp_raw"].isin([1, 0, -1]).all()
    t["resp"] = (t["resp_raw"] == 1).astype(int)
    t["resp_raw"] = t["resp_raw"].astype(int)
    out["almousa_2026_pgx_knowledge"] = (t, (0, 1), ["resp_raw"])
    t = long([f"f{i}" for i in range(1, 6)])
    assert t["resp_raw"].isin([0, 1]).all()
    t["resp"] = t["resp_raw"].astype(int)
    out["almousa_2026_pgx_familiarity"] = (t, (0, 1), [])
    for pre, name in [("a", "almousa_2026_pgx_attitudes"), ("c", "almousa_2026_pgx_confidence")]:
        t = long([f"{pre}{i}" for i in range(1, 5)])
        assert t["resp_raw"].isin([-2, -1, 0, 1, 2]).all()
        t["resp"] = (t["resp_raw"] + 3).astype(int)
        out[name] = (t, (1, 5), [])
    for name, (t, (lo, hi), extra) in out.items():
        t = t[["id", "item", "resp"] + extra + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
