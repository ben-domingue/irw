#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/32p7btkgr4
# DOI: 10.17632/32p7btkgr4 (data); paper 10.1007/s12144-020-00988-7
#   May A, Norris S, Richter L, Pitman M (2020). A psychometric evaluation of the Highly
#   Sensitive Person Scale in ethnically and culturally heterogeneous South African samples.
#   Current Psychology 41.
# License: CC BY 4.0 (Mendeley Data record)
# Data: hspsbtt.xlsx (1,400 Birth to Twenty cohort participants; sheet "key" codes
#   Ethnicity 1 White, 2 Black African, 3 Mixed ancestry, 4 Indian; Sex 0 male, 1 female) and
#   hspsstudent.xlsx (750 university students; labels in the cells). Both sheets' keys:
#   Q1-Q27 = HSPS items 1-27 in the original instrument's order; columns 1-3 = "researcher-
#   generated reverse-scored items".
#
# Table: may_2020_hsps -- Highly Sensitive Person Scale (Aron & Aron 1997), 27 items Q1..Q27,
#   1-7. Same instrument and response scale in both samples -> one table with cov_study
#   (btt / student). The 3 researcher-generated items are not shipped: the key calls them
#   "reverse-scored" without saying whether the stored values are already reversed.
# id: the deposits' ids (BTTID, student number) are replaced by "btt_<row>" / "student_<row>"
#   (a student number is an institutional identifier; the row index links to nothing).
# Covariates (one student has a blank ethnicity, kept NA): cov_study, cov_sex, cov_ethnicity (both samples, harmonised to the student
#   labels; BTT "Mixed ancestry" kept as is), cov_age and cov_home_language (students only).
# Item text: not shipped -- item numbers only; HSPS wording is in Aron & Aron (1997).
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402


def gate(t):
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails

OUT = REPO_ROOT / "automated_finding" / "irw_output"
BASE = "https://data.mendeley.com/public-files/datasets/32p7btkgr4/files/"
URL_BTT = BASE + "2d9395fe-55ce-49cc-9e7c-074aec346de3/file_downloaded"
URL_STU = BASE + "ea373cb5-74f5-4c90-995f-4036b5bc3084/file_downloaded"
Q = [f"Q{i}" for i in range(1, 28)]


def get(url, sheet):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name=sheet)


def main():
    b = get(URL_BTT, "hspsbtt")
    s = get(URL_STU, "hspsstudent")
    assert len(b) == 1400 and len(s) == 750
    b = b.reset_index(drop=True)
    s = s.reset_index(drop=True)
    b["id"] = "btt_" + (b.index + 1).astype(str)
    s["id"] = "student_" + (s.index + 1).astype(str)
    b["cov_study"], s["cov_study"] = "btt", "student"
    b["cov_sex"] = b["Sex"].map({0: "Male", 1: "Female"})
    s["cov_sex"] = s["Sex"]
    b["cov_ethnicity"] = b["Ethnicity"].map({1: "White", 2: "Black African", 3: "Mixed ancestry", 4: "Indian"})
    s["cov_ethnicity"] = s["Ethnicity"]
    s["cov_age"] = s["Age"]
    s["cov_home_language"] = s["Home Language"]
    b["cov_age"] = pd.NA
    b["cov_home_language"] = pd.NA
    covs = ["cov_study", "cov_sex", "cov_ethnicity", "cov_age", "cov_home_language"]
    frames = []
    for d in (b, s):
        print(d["cov_study"].iloc[0], "missing sex/ethnicity:", d[["cov_sex", "cov_ethnicity"]].isna().sum().to_dict())
        t = d[["id"] + covs + Q].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        frames.append(t.dropna(subset=["resp"]))
    t = pd.concat(frames, ignore_index=True)
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 7).all() and not t.duplicated(["id", "item"]).any()
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    gate(t)
    t.to_csv(OUT / "may_2020_hsps.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
