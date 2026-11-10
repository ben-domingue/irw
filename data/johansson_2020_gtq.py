#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243805
# DOI: 10.1371/journal.pone.0243805
# Paper: Johansson M, Karlsson T, Finizia C (2020). Further validation of the
#   Gothenburg Trismus Questionnaire (GTQ). PLoS ONE 15(12): e0243805.
# Data: PLOS SI S1 (journal.pone.0243805.s001, .xlsx, sheet "Inmatningsfil
#   Enkatsvar"), Swedish patients at Sahlgrenska University Hospital: head and
#   neck cancer patients at risk of trismus, TMD patients, and matched
#   controls. S2 File is the English GTQ 2 form.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# FOUR output tables, items as answered; codes are the instrument's own item
# numbers (the sheet repeats bare numbers per block: "1", "1.1", "1.2", ...):
#   johansson_2020_gtq    GTQ 2 items 1-23, 1 (not at all) .. 5 (very severe).
#     The jaw pictures (0/1) and the training follow-ups 24-29 (answered by
#     the ~45 who train) are not carried.
#   johansson_2020_c30    EORTC QLQ-C30, c30_1..c30_30: items 1-28 1-4,
#     items 29-30 1-7 (global health / QoL).
#   johansson_2020_hn35   EORTC QLQ-H&N35, hn35_31..hn35_65 (the module's
#     own numbering): 31-60 1-4, 61-65 yes/no stored 1/2. One 3 and one 0 in
#     61/65 and a blank-string cell dropped.
#   johansson_2020_hads   HADS, hads_1..hads_14, 0-3 as scored.
# Covariates: group (1 trismus/HNC, 2 TMD, 3 control -- the sheet's own
#   header), age, sex, occupational status, living alone, smoking. Education
#   years dropped (contains 119), tumour diagnosis and mouth-opening
#   measurement not carried. Derived EORTC domain and HADS totals dropped.
# `id` = row index (rows without any response dropped by the melt).
#
# Item text: NOT SHIPPED. GTQ 2 English wording in S2 File (study-authored,
#   CC BY; administered in Swedish). EORTC and HADS are register-restricted.

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0243805.s001"
RAW = os.environ.get("JOHANSSON2020_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_johansson2020_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    df = pd.read_excel(path)
    df.columns = [x.strip() if isinstance(x, str) else x for x in df.columns]
    if not RAW:
        os.remove(path)
    return df


def save(df, covs, mapping, name, allowed):
    sub = df[["id"] + covs + list(mapping)].rename(columns=mapping)
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    ok = long.apply(lambda r: r["resp"] in allowed(r["item"]), axis=1)
    long = long[ok].copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    vals = sorted(set(long["resp"]))
    checks = run_qc(long, permitted_values=vals)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df = load()
    c = list(df.columns)
    assert c[0].startswith("1=trismus 2=TMD 3=control")
    assert c.index("GTQ") + 1 == c.index(1) and c[c.index("H&N35") + 1] == 31
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cov_group"] = df[c[0]].map({1: "trismus (HNC)", 2: "TMD", 3: "control"})
    df["cov_age"] = df["Age"]
    df["cov_sex"] = df[c[3]].map({1: "male", 2: "female"})
    df["cov_occupation"] = df[c[2]].map({1: "working", 2: "retired", 3: "studying", 4: "other"})
    df["cov_lives_alone"] = df[c[5]]
    smoke = [x for x in c if str(x).startswith("Smoking")][0]
    df["cov_smoking"] = df[smoke].map({0: "never", 1: "stopped >12 months ago", 2: "current, or stopped <12 months ago"})
    covs = ["cov_group", "cov_age", "cov_sex", "cov_occupation", "cov_lives_alone", "cov_smoking"]

    gtq = {i: f"gtq_{i}" for i in range(1, 24)}
    c30_src = [f"{i}.2" for i in range(1, 13)] + [f"{i}.1" for i in range(13, 30)] + [30]
    assert c.index("EORTC C30") + 1 == c.index("1.2") and c[c.index("1.2") + 29] == 30
    c30 = {s: f"c30_{k}" for k, s in enumerate(c30_src, 1)}
    hn35 = {i: f"hn35_{i}" for i in range(31, 66)}
    hads_src = [f"{i}.3" for i in range(1, 13)] + ["13.2", "14.2"]
    assert c.index("HADS") + 1 == c.index("1.3")
    hads = {s: f"hads_{k}" for k, s in enumerate(hads_src, 1)}

    save(df, covs, gtq, "johansson_2020_gtq", lambda it: {1, 2, 3, 4, 5})
    save(df, covs, c30, "johansson_2020_c30",
         lambda it: {1, 2, 3, 4, 5, 6, 7} if it in ("c30_29", "c30_30") else {1, 2, 3, 4})
    save(df, covs, hn35, "johansson_2020_hn35",
         lambda it: {1, 2} if int(it.split("_")[1]) >= 61 else {1, 2, 3, 4})
    save(df, covs, hads, "johansson_2020_hads", lambda it: {0, 1, 2, 3})
    print(df["cov_group"].value_counts(dropna=False).to_dict())


if __name__ == "__main__":
    convert()
