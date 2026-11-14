#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Nudging_in_e-commerce_the_impact_of_user_experience_as_a_nudge_on_customer_loyalty_in_grocery_retailing/30588839
# DOI: 10.6084/m9.figshare.30588839.v1 (data)
#   Lombard S (2025). Nudging in e-commerce: the impact of user experience as a nudge on customer
#   loyalty in grocery retailing [Data set]. figshare.
# License: CC0 (figshare record)
# Data: the Google Forms export (563 rows). 494 respondents answered "Yes" to the screener (online
#   grocery shopping in the last 6 months) and went on to the questionnaire; the 69 "No" rows have no
#   answers and are not used. South African sample (income bands in rand).
# Items: every column header is "<code>. <statement>"; item = the code (B1.1 ...), responses are the
#   words Strongly Disagree .. Strongly Agree, coded 1-5 here.
# Tables, one per sub-section of the questionnaire (construct names are IRW's reading of the statements):
#   _ease_of_use B1.1-5, _help_information B2.1-4, _visual_aesthetics C1.1-6, _product_ratings D1.1-5,
#   _online_reviews D2.1-5, _online_shopping_appeal E1.1-5, _perceived_control E2.1-4,
#   _convenience F1.1-6, _attitude F2.1-4, _trust G1.1-5, _loyalty G2.1-4, _satisfaction G3.1-4.
# Covariates: cov_gender, cov_age_group, cov_education (A1-A3 as answered).
# Not carried: timestamp, income, marital status, usage questions A6-A9.
# Item text: not shipped -- the statements are in the headers, but several read as adapted from
#   published e-commerce and brand-relationship scales that have not been identified; recorded in
#   itemtext_provenance as cheap but unidentified.
import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://ndownloader.figshare.com/files/59460440"
LIKERT = {"Strongly Disagree": 1, "Disagree": 2, "Neutral": 3, "Agree": 4, "Strongly Agree": 5}
SECTIONS = {"B1": "ease_of_use", "B2": "help_information", "C1": "visual_aesthetics", "D1": "product_ratings",
            "D2": "online_reviews", "E1": "online_shopping_appeal", "E2": "perceived_control",
            "F1": "convenience", "F2": "attitude", "G1": "trust", "G2": "loyalty", "G3": "satisfaction"}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content))
    assert len(d) == 563
    screen = [c for c in d.columns if c.startswith("Have you done online grocery")][0]
    d = d[d[screen] == "Yes"].reset_index(drop=True)
    assert len(d) == 494
    d["id"] = range(1, len(d) + 1)
    code = {}
    for c in d.columns:
        m = re.match(r"^([A-G]\d?\.\d+|A\d+)\.\s", c)
        if m:
            code[c] = m.group(1)
    d = d.rename(columns=code)
    d["cov_gender"] = d["A1"]
    d["cov_age_group"] = d["A2"]
    d["cov_education"] = d["A3"]
    covs = ["cov_gender", "cov_age_group", "cov_education"]
    n_items = 0
    for sec, label in SECTIONS.items():
        items = [c for c in d.columns if re.fullmatch(re.escape(sec) + r"\.\d+", str(c))]
        n_items += len(items)
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].str.strip().map(LIKERT)
        assert t["resp"].notna().all(), sec
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        name = f"lombard_2025_{label}"
        fails = [c for c in run_qc(t, permitted_values=range(1, 6)) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    assert n_items == 57


if __name__ == "__main__":
    main()
