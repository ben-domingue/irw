#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/24511318
# DOI: 10.6084/m9.figshare.24511318.v1 (data)
#   Muffato V (2023). Explorers are greener? Investigating personality traits, connectedness to
#   nature and attitudes toward exploring in various pro-environmental behaviors [Data set]. figshare.
# License: CC BY 4.0 (figshare)
# Data: "Exploreres are greener - Dataset.xlsx", 649 Italian adults aged 18-59 (405 women).
#
# Tables:
#   muffato_2023_spatial_anxiety -- QAS_1..QAS_8, the spatial anxiety questionnaire of the
#     wayfinding-inclinations battery, 1-6; the deposit's QAS total equals the item sum in all rows and
#     every item correlates .65-.81 with the rest (one direction, nothing reversed).
#   muffato_2023_bfi44 -- BIG1..BIG44 (BFI-44), 1-5, as deposited. The deposit's E and N scores equal
#     the raw item means with no reversal, while A/C/O match neither the raw nor the reversed means, so
#     the reversal state is not confirmed; check direction before scoring. Every reverse-keyed item
#     (BFI key) correlates positively (.12-.60) with the direct items of its trait, which points to all of
#     them being stored already reversed.
#   muffato_2023_atot -- AtOT_1..AtOT_10 (attitudes toward exploring), 1-6, as deposited.
#   muffato_2023_pebs -- PEBS_1..PEBS_19 (pro-environmental behaviours), 1-5, as deposited.
#     For AtOT and PEBS the totals/subscale means equal the raw sums/means and no item runs against the
#     rest, so any reverse-keyed items were reversed before deposit and are not identified; check
#     direction before scoring.
# Not shipped:
#   CNS_1-14: each item takes only three values (1/4/5, or 1/2/5 on items 4, 12, 14) on a 1-5
#     scale -- collapsed in the deposit; not the scale as answered.
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
    tables = {"muffato_2023_spatial_anxiety": (items, 1, 6),
              "muffato_2023_bfi44": ([f"BIG{i}" for i in range(1, 45)], 1, 5),
              "muffato_2023_atot": ([f"AtOT_{i}" for i in range(1, 11)], 1, 6),
              "muffato_2023_pebs": ([f"PEBS_{i}" for i in range(1, 20)], 1, 5)}
    for name, (cols, lo, hi) in tables.items():
        t = d[["id"] + covs + cols].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(lo, hi).all(), name
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())

if __name__ == "__main__":
    main()
