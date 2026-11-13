#!/usr/bin/env python3
# Source: https://osf.io/8wqzv/
# DOI: 10.17605/OSF.IO/8WQZV (data); paper Okan Y, Smith SG, Bruine de Bruin W (2019). How Do Women
#   Interpret the NHS Information Leaflet about Cervical Cancer Screening? Medical Decision Making,
#   doi 10.1177/0272989X19873647.
# License: CC BY 4.0 (OSF node licence)
# Data: "Survey data cervical leaflet.csv" + _codebook.xlsx, 602 UK women aged 25-64 (online panel)
#   who read the NHS cervical screening leaflet and answered a 23-item knowledge test about it.
#
# Tables:
#   okan_2019_cervical_leaflet_knowledge -- k1..k23 scored by the authors (k*_corr, 0/1; the stored
#     k_tot equals their sum in every row). Items 1-11, 14, 16, 18-23 are true/false statements,
#     12, 13, 15, 17 numeric estimates. resp_raw = the answer given (k*: 1 True / 2 False for the
#     statements, the number for the estimates). item = k1..k23.
#   okan_2019_numeracy -- num1-3 (Schwartz et al. 1997), num*_corr 0/1; resp_raw = the answer.
# Not shipped: per-item confidence ratings (k*_conf, 0-100 in steps of 10), leaflet and image
#   evaluations (single 1-7 ratings), screening history.
# id: id_clean. Covariates: cov_age, cov_education, cov_ethnicity (codebook value labels).
#   Region of residence (location) and GP practice location are dropped (geographic codes).
# Item text: not shipped -- the statements are the codebook labels and "Survey materials cervical
#   leaflet.pdf"; the numeric estimates need the frequency framing from the PDF.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
DATA = "https://osf.io/download/y45dp/"
CODEBOOK = "https://osf.io/download/u9rh6/"


def get(u):
    r = requests.get(u, timeout=120)
    r.raise_for_status()
    return r.content


def labels(cb, var):
    v = cb.copy()
    v["var"] = v.iloc[:, 0].ffill()
    v = v[v["var"] == var]
    return {int(k): s for k, s in zip(v.iloc[:, 1], v.iloc[:, 2])}


def save(t, name, covs):
    t = t.dropna(subset=["resp"]).copy()
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].isin([0, 1]).all()
    t = t[["id", "item", "resp", "resp_raw"] + covs].sort_values(["id", "item"])
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, (name, fails)
    t.to_csv(OUT / f"{name}.csv", index=False)
    print(name, len(t), t.id.nunique(), t.item.nunique())


def main():
    d = pd.read_csv(io.BytesIO(get(DATA)))
    cb = pd.read_excel(io.BytesIO(get(CODEBOOK)), sheet_name=1)
    assert len(d) == 602 and d["id_clean"].is_unique
    d = d.copy()
    d["id"] = d["id_clean"]
    d["cov_age"] = d["age"]
    d["cov_education"] = d["education"].map(labels(cb, "education"))
    d["cov_ethnicity"] = d["ethnic"].map(labels(cb, "ethnic"))
    covs = ["cov_age", "cov_education", "cov_ethnicity"]
    k = [f"k{i}" for i in range(1, 24)]
    assert (d[[f"{x}_corr" for x in k]].sum(axis=1) == d["k_tot"]).all()
    t = pd.concat([pd.DataFrame({"id": d["id"], "item": x, "resp": d[f"{x}_corr"], "resp_raw": d[x],
                                 **{c: d[c] for c in covs}}) for x in k])
    save(t, "okan_2019_cervical_leaflet_knowledge", covs)
    n = [f"num{i}" for i in range(1, 4)]
    t = pd.concat([pd.DataFrame({"id": d["id"], "item": x, "resp": d[f"{x}_corr"], "resp_raw": d[x],
                                 **{c: d[c] for c in covs}}) for x in n])
    save(t, "okan_2019_numeracy", covs)


if __name__ == "__main__":
    main()
