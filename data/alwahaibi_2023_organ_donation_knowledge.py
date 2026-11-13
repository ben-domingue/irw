#!/usr/bin/env python3
# Source: https://frontiersin.figshare.com/articles/dataset/23168456 (Table 3) and /23168447 (Table 1)
# DOI: 10.3389/fpubh.2023.1115531 (paper); data 10.3389/fpubh.2023.1115531.s005 (items),
#   .s003 (demographics)
#   Alwahaibi N, Al Wahaibi A, Al Abri M (2023). Knowledge and attitude about organ donation and
#   transplantation among Omani university students. Frontiers in Public Health 11:1115531.
# License: CC BY 4.0 (Frontiers / figshare)
# Data: the supplementary "tables" are per-student response files, rows linked by "#N" (1-2125, same
#   order in every file). 2,125 Sultan Qaboos University students, 2021-22 (paper N = 2,125).
#
# Table: alwahaibi_2023_organ_donation_knowledge -- the 15 questions of the knowledge section
#   (Table_3 file), answered Yes / No / I don't know (items 1, 3, 4, 11, 13 Yes/No only).
#   The counts reproduce the paper's Table 2 on every item (item 4: 800/1325 vs 799/1326).
#   The paper scores 0-15 but never publishes the key, and the section mixes awareness items
#   ("Have you heard about brain death?") with factual ones, so responses are stored as answered,
#   not keyed: resp 1 = Yes, 0 = No; "I don't know" is not a row (8,270 cells).
#   item = k01..k15, the question number in the header.
# Not shipped: the attitude section (Table_4 file). Its eight columns do not reproduce the paper's
#   Table 4: column k holds the counts of the paper's question k+1 for k = 1-5, question 1 is
#   absent, and columns 6 and 7 are identical in every row. The source/reason checklists
#   (Table_2, _5, _6) are multi-select.
# id: "#N". Covariates (Table_1 file): sex, age group, marital status, college, degree, semester.
#   Governorate of residence is dropped (geographic code); nationality is constant ("Omani").
# Item text: not shipped -- the English questions are the column headers (study-authored), but
#   kept out of this pass; cheap later from the Table_3 headers.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
ITEMS = "https://ndownloader.figshare.com/files/40869236"
DEMO = "https://ndownloader.figshare.com/files/40869230"


def get(u):
    r = requests.get(u, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def main():
    k, demo = get(ITEMS), get(DEMO)
    assert len(k) == len(demo) == 2125
    assert (k["#N"].values == demo["#N"].values).all() and k["#N"].is_unique
    qcols = [c for c in k.columns if c != "#N"]
    assert len(qcols) == 15
    ren = {}
    for c in qcols:
        n = int(c.split(")")[0])
        ren[c] = f"k{n:02d}"
    assert sorted(ren.values()) == [f"k{i:02d}" for i in range(1, 16)]
    covmap = {"Sex": "cov_sex", "Age": "cov_age_group", "Marital status": "cov_marital_status",
              "College": "cov_college", "Degree": "cov_degree", "Semester": "cov_semester"}
    d = k.rename(columns=ren).merge(demo[["#N"] + list(covmap)].rename(columns=covmap), on="#N")
    d = d.rename(columns={"#N": "id"})
    covs = list(covmap.values())
    t = d.melt(id_vars=["id"] + covs, value_vars=list(ren.values()), var_name="item",
               value_name="ans")
    print(t["ans"].value_counts().to_dict())
    t["resp"] = t["ans"].map({"Yes": 1, "No": 0})
    assert t.loc[t["resp"].isna(), "ans"].eq("I don't know").all()
    t = t.dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails
    t.to_csv(OUT / "alwahaibi_2023_organ_donation_knowledge.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
