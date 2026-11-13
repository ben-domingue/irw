#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/33919306
# DOI: 10.6084/m9.figshare.33919306.v2 (data)
#   Timsina P (2026). Dataset for Cancer Stigma score at baseline and followup and cervical cancer
#   screening uptake [Data set]. figshare. (Thesis: "Effectiveness of a Community-Based Cervical
#   Cancer Stigma Reduction Intervention on Cancer Stigma and Cervical Cancer Screening Uptake in
#   Nepal: A Cluster-Randomized Controlled Trial".)
# License: CC BY 4.0 (figshare)
# Data: "S4_Dataset_Stigma Score (1).xls" (header on row 2), 310 women aged 30-60 in Budanilkantha
#   municipality, cluster-randomised by ward. Cancer stigma items in six domains -- severity (5),
#   personal responsibility (4), awkwardness (5), avoidance (5), financial discrimination (3),
#   opposition to policy (3): 25 items, 1-6, at baseline and endline (endline columns suffixed .1;
#   64 women have no endline). Each domain mean the deposit stores equals the mean of its raw items
#   at baseline (checked). The description classes a domain mean < 3 as "stigma", i.e. lower =
#   more stigmatising; items are shipped as stored.
#
# Table: timsina_2026_cancer_stigma -- item = the baseline column name (severity01 ..
#   Policyopposition03; the deposit's own spelling, incl. "Awkwarness"); wave 1 = baseline,
#   2 = endline; treat = Intervention(Intenttotreat) (1 intervention, 0 control).
# Not shipped: domain means/binaries; per-protocol flag; screening uptake file. The ward number
#   (randomisation cluster) is not carried: it is an administrative area code.
# id: Unique_ID. Covariates: cov_age, cov_education, cov_religion, cov_ethnicity, cov_work_status.
# Item text: not shipped -- the deposit carries domain-coded column names only.
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://ndownloader.figshare.com/files/68838646"
DOMS = {"severity": "Mean_Severity", "Personalresponsibility": "Mean_Personalresponsibility",
        "Awkwarness": "Mean_Awkwardness", "Avoidance": "Mean_Avoidance",
        "Financialdiscrimination": "Mean_FinancialDiscrimination",
        "Policyopposition": "Mean_Policy Opposition"}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    d = pd.read_excel(io.BytesIO(r.content), header=1)
    assert len(d) == 310 and d["Unique_ID"].is_unique
    items = list(d.columns[13:38])
    assert items[0] == "severity01" and items[-1] == "Policyopposition03"
    for pre, m in DOMS.items():
        cols = [c for c in items if c.startswith(pre)]
        assert ((d[cols].mean(axis=1) - d[m]).abs() < 1e-4).all(), pre
    d = d.copy()
    d["id"] = d["Unique_ID"]
    d["treat"] = d["Intervention(Intenttotreat)"]
    covmap = {"cov_age": "age_in_years", "cov_education": "lvl_education_completed",
              "cov_religion": "religion", "cov_ethnicity": "ethnicity", "cov_work_status": "work_status"}
    for c, v in covmap.items():
        d[c] = d[v]
    covs = list(covmap)
    rows = []
    for w, suf in ((1, ""), (2, ".1")):
        for it in items:
            rows.append(pd.DataFrame({"id": d["id"], "item": it, "resp": d[it + suf], "wave": w,
                                      "treat": d["treat"], **{c: d[c] for c in covs}}))
    t = pd.concat(rows).dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 6).all()
    t = t[["id", "item", "resp", "wave", "treat"] + covs].sort_values(["id", "wave", "item"])
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails
    t.to_csv(OUT / "timsina_2026_cancer_stigma.csv", index=False)
    print(len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
