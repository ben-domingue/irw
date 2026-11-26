#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/43fjx5m99p
# DOI: 10.17632/43fjx5m99p (data)
#   Tong F, Zhang H, Zhen F, Irby B, Lara-Alecio R, Tang S (2021). Survey Data from an Experimental Study in Supporting
#   Parental Engagement among Chinese Low-income Families in their Children's English Learning Through Home-literacy
#   Activities [Data set]. Mendeley Data.
# License: CC BY 4.0 (Mendeley record metadata)
# Data: one workbook, Sheet1, a two-row header (groups above, variables below): 172 low-SES Chinese parents, 86
#   treatment and 86 control (the deposit's Student ID), each answering the same 10-item parental-engagement survey
#   before and after the intervention. The record and headers give no anchors; every response is observed within
#   2-5, so 1-5 (five-point) is taken as the range.
# Table: tong_2021_parental_engagement, item = the deposit's label (item1..item10, from "Item 1".."Item 10"; the
#   post block repeats the same labels), wave 1 = pre-intervention, 2 = post-intervention. treat = 1 for T, 0 for C.
# Covariates: cov_parent_age_group (codes in the header: 1 = 25-34 ... 5 = 65+), cov_english_years (years of
#   learning English, as entered), cov_child_tutoring (1 = participates, 2 = not, per the header),
#   cov_parent_degree (high school / associate / bachelor / master+, per the header), cov_english_cet4 (1 = has the Band 4 certificate, 0 = not).
# PII: none. The six open-ended Chinese answers about the STELLA course (treatment parents only) are not carried;
#   7 text columns screened (condition and those answers).
# Item text: not shipped -- the deposit labels the items "Item 1".."Item 10" only.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = "https://data.mendeley.com/public-files/datasets/43fjx5m99p/files/3f517ad8-358a-412b-a875-7a3a931708c6/file_downloaded"
NAME = "tong_2021_parental_engagement"
LO, HI = 1, 5


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content), header=None)
    assert raw.iloc[0, 7].startswith("Pre-intervention") and raw.iloc[0, 17].startswith("Post-intervention")
    d = raw.iloc[2:].reset_index(drop=True)
    assert len(d) == 172
    hdr = [str(x).strip() for x in raw.iloc[1]]
    pre = list(range(7, 17))
    post = list(range(17, 27))
    assert [hdr[i] for i in pre] == [f"Item {k}" for k in range(1, 11)] == [hdr[i] for i in post]
    covs = {2: "cov_parent_age_group", 3: "cov_english_years", 4: "cov_child_tutoring", 5: "cov_parent_degree",
            6: "cov_english_cet4"}
    not_carried = {0: "id", 1: "treat"} | {i: "open-ended text" for i in range(27, raw.shape[1])}
    assert set(range(raw.shape[1])) == set(pre) | set(post) | set(covs) | set(not_carried), "column books"
    base = pd.DataFrame({"id": pd.to_numeric(d[0]).astype(int)})
    assert base.id.is_unique
    assert set(d[1]) == {"T", "C"}
    base["treat"] = (d[1] == "T").astype(int)
    keys = {"cov_parent_age_group": {1: "25-34", 2: "35-44", 3: "45-54", 4: "55-64", 5: "65+"},
            "cov_child_tutoring": {1: "participates", 2: "does_not"},
            "cov_parent_degree": {1: "high_school", 2: "associate", 3: "bachelor", 4: "master_or_above"},
            "cov_english_cet4": {1: "yes", 0: "no"}}
    for i, c in covs.items():
        v = pd.to_numeric(d[i])
        if c in keys:
            assert set(v.dropna()) <= set(keys[c]), c
            v = v.map(keys[c])
        base[c] = v
    parts = []
    for wave, cols in ((1, pre), (2, post)):
        w = base.copy()
        for k, i in enumerate(cols, start=1):
            w[f"item{k}"] = pd.to_numeric(d[i])
        w = w.melt(id_vars=list(base.columns), var_name="item", value_name="resp")
        w["wave"] = wave
        parts.append(w)
    t = pd.concat(parts).dropna(subset=["resp"])
    assert t.resp.between(LO, HI).all() and (t.resp % 1 == 0).all()
    t["resp"] = t.resp.astype(int)
    t = t[["id", "item", "resp", "wave", "treat"] + list(covs.values())].sort_values(["id", "wave", "item"])
    fails = [c for c in run_qc(t, permitted_values=range(LO, HI + 1)) if c.status == "fail"]
    assert not fails, fails
    t.to_csv(OUT / f"{NAME}.csv", index=False)
    print(NAME, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
