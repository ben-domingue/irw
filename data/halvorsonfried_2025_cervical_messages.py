#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/XKMAUT (Harvard Dataverse)
# DOI: 10.7910/DVN/XKMAUT (data)
#   Halvorson-Fried S (2025). Perceived effectiveness of messages to address cervical cancer
#   screening barriers: Data from an online experiment [Data set]. Harvard Dataverse.
# License: CC0 1.0 (Dataverse)
# Data: cc_data_public.xlsx + cc_codebook_public.docx, 1,536 US women aged 21-65 (online RCT,
#   University of North Carolina). Each participant rated five messages, one per theme (control,
#   cancer fatalism, screening guidelines, risk factors, convenience); for the four non-control
#   themes the message shown was one of three, recorded in theme1-theme4.
#
# Tables (1-5, value labels from the codebook):
#   halvorsonfried_2025_cancer_fatalism -- fatalism1-4, HINTS cancer fatalism items, 1 strongly
#     disagree .. 5 strongly agree.
#   halvorsonfried_2025_message_ratings -- three questions per message: pe_ (how much it encourages
#     screening, 1 not at all .. 5 a great deal), social_ (how likely to talk about it in the next
#     week, 1 not at all likely .. 5 extremely likely), learn_ (learned something new, 1 not at all ..
#     5 a great deal). item = <question>_<theme>, with the message number appended for the four
#     randomised themes (e.g. pe_fat_m2), so each item is one question about one message: 3 + 4 x 3 x
#     3 = 39 items, each person answering 15. The control message's items are coded <question>_ctrlmsg
#     (source pe_control etc.; renamed because a bare "control" reads as a group covariate).
# id: cc_id. Covariates (codebook labels): cov_age (screener, years), cov_race_ethnicity (racecat),
#   cov_education (edcat), cov_income (incomecat), cov_arm (parent-study arm 1-4).
# Item text: not shipped -- the codebook gives every question and anchor, but the message texts the
#   ratings refer to are not in the deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://dataverse.harvard.edu/api/access/datafile/12125969"
THEMES = {"fat": "theme1", "screen": "theme2", "risk": "theme3", "time": "theme4"}
RACE = {1: "White", 2: "Black/African American", 3: "Latine", 4: "Asian",
        5: "Another race/multiracial, not Latine"}
EDU = {1: "<HS or HS/GED", 2: "Some college", 3: "4 year or graduate degree"}
INCOME = {1: "Less than $25,000", 2: "$25,000-49,999", 3: "$50,000-99,999", 4: "$100,000 or more"}


def save(t, name, covs):
    t = t.dropna(subset=["resp"]).copy()
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 5).all(), name
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, (name, fails)
    t.to_csv(OUT / f"{name}.csv", index=False)
    print(name, len(t), t.id.nunique(), t.item.nunique())


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert len(d) == 1536 and d["cc_id"].is_unique
    d["id"] = d["cc_id"]
    d["cov_age"] = d["age_screener"]
    d["cov_race_ethnicity"] = d["racecat"].map(RACE)
    d["cov_education"] = d["edcat"].map(EDU)
    d["cov_income"] = d["incomecat"].map(INCOME)
    d["cov_arm"] = d["arm"]
    covs = ["cov_age", "cov_race_ethnicity", "cov_education", "cov_income", "cov_arm"]
    f = [f"fatalism{i}" for i in range(1, 5)]
    save(d[["id"] + covs + f].melt(id_vars=["id"] + covs, var_name="item", value_name="resp"),
         "halvorsonfried_2025_cancer_fatalism", covs)
    rows = []
    for q in ("pe", "social", "learn"):
        rows.append(pd.DataFrame({"id": d["id"], "item": f"{q}_ctrlmsg", "resp": d[f"{q}_control"],
                                  **{c: d[c] for c in covs}}))
        for th, col in THEMES.items():
            assert d[col].isin([1, 2, 3]).all()
            rows.append(pd.DataFrame({"id": d["id"], "item": f"{q}_{th}_m" + d[col].astype(int).astype(str),
                                      "resp": d[f"{q}_{th}"], **{c: d[c] for c in covs}}))
    save(pd.concat(rows), "halvorsonfried_2025_message_ratings", covs)


if __name__ == "__main__":
    main()
