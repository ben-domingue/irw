#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/24511318
# DOI: 10.6084/m9.figshare.24511318.v1 (data)
#   Muffato V (2023). Explorers are greener? Investigating personality traits, connectedness to
#   nature and attitudes toward exploring in various pro-environmental behaviors [Data set]. figshare.
# License: CC BY 4.0 (figshare)
# Data: "Exploreres are greener - Dataset.xlsx", 649 Italian adults aged 18-59 (405 women).
#
# Table: muffato_2023_spatial_anxiety -- QAS_1..QAS_8, the spatial anxiety questionnaire of the
#   wayfinding-inclinations battery, 1-6; the deposit's QAS total equals the item sum in all rows and
#   every item correlates .65-.81 with the rest (one direction, nothing reversed).
# Not shipped, and why:
#   CNS_1-14: each item takes only three values (1/4/5, or 1/2/5 on items 4, 12, 14) on a 1-5
#     scale -- collapsed in the deposit; not the scale as answered.
#   BIG1-44 (BFI-44): the deposit's E and N scores equal the raw item means with no reversal, A/C/O
#     match neither the raw nor the reversed means, so which items were already reversed cannot be
#     established.
#   AtOT_1-10 and PEBS_1-19: totals/subscale means equal raw sums/means and no item runs against the
#     rest, i.e. any reverse-keyed items were reversed before deposit and cannot be identified.
# id: the deposit's ID. Covariates: cov_age, cov_gender.
# Item text: not shipped -- variable names only; the questionnaire wording is in the published
#   Italian battery, not the deposit.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://ndownloader.figshare.com/files/43052584"


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content))
    assert len(d) == 649 and d["ID"].is_unique
    items = [f"QAS_{i}" for i in range(1, 9)]
    assert (d[items].sum(axis=1) == d["QAS"]).all()
    d = d.rename(columns={"ID": "id", "age": "cov_age", "gender": "cov_gender"})
    covs = ["cov_age", "cov_gender"]
    t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    t = t.dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 6).all()
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails
    t.to_csv(OUT / "muffato_2023_spatial_anxiety.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
