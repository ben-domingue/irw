#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0189666
# DOI: 10.1371/journal.pone.0189666
# Paper: Beshai S, Mishra S, Mishra S, Carleton RN (2017). Personal relative
#   deprivation associated with functional disorders via stress: An
#   examination of fibromyalgia and gastrointestinal symptoms. PLoS ONE
#   12(12): e0189666.
# Data: PLOS Supporting Information S1 Data (journal.pone.0189666.s001, .sav
#   with variable and value labels; a Qualtrics export). 525 CrowdFlower
#   workers from five English-speaking countries, 2016 (the paper analyses the
#   517 completers).
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 7.
#
# THREE output tables, items as answered:
#   beshai_2017_prds_r  Personal Relative Deprivation Scale-Revised, PRDS1-5,
#     1 strongly disagree .. 7 strongly agree (the value labels; the paper
#     says a 6-point scale, the deposit has seven labelled points). Items 2
#     ("I feel privileged...") and 4 ("...I am quite well off") are the
#     reversed ones by their wording (quoted in the paper); the deposit's
#     reversed copies PRDS2t/PRDS4t are 8 - x and are not shipped.
#   beshai_2017_fiqr  Revised Fibromyalgia Impact Questionnaire, 21 items, on
#     the scales the survey used: function f1-f9 1-9 (1 no difficulty .. 9
#     very difficult), overall impact o1-o2 1-11 (1 never .. 11 always),
#     symptoms s1-s10 0-10. The item sum + 10 equals the deposit's NewFIQR on
#     every complete row (asserted).
#   beshai_2017_sf_mpq  Short-form McGill Pain Questionnaire descriptors
#     (Q6.1_1-15, "throbbing" ...), 1 none .. 4 severe. Not analysed in the
#     paper.
# Dropped: the widespread pain body map and the 41-symptom checklist
#   (Qualtrics check-all boxes: unchecked and unanswered are both 0, and the
#   first two body-map boxes are coded differently from the rest); the
#   3-item symptom severity block (thin); Gastro-Questionnaire (one of 26
#   items deposited, the rest only as a total); DASS-21 (totals only);
#   pain VAS and PPI (single items); diagnosis questions, free text.
# Covariates: age, gender, education, income, from the value labels.
# `id` is the row index (the deposit carries no identifier).
#
# Item text: NOT SHIPPED. The PRDS-R wording is quoted in full in the paper's
#   Measures section (cheap); FIQR and SF-MPQ are published instruments.

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0189666.s001"
RAW = os.environ.get("BESHAI2017_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_beshai2017_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, meta = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df, meta


def save(df, covs, items, name, values):
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(values)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df, meta = load()
    assert len(df) == 525, df.shape
    vl = meta.variable_value_labels
    df["id"] = range(1, len(df) + 1)
    df["cov_age"] = df["Q5.1"]
    df["cov_gender"] = df["Q5.2"].map(vl["Q5.2"])
    df["cov_education"] = df["Q5.9"].map(vl["Q5.9"])
    df["cov_income"] = df["Q5.12"].map(vl["Q5.12"])
    covs = ["cov_age", "cov_gender", "cov_education", "cov_income"]

    prds = [f"PRDS{i}" for i in range(1, 6)]
    assert vl["PRDS1"][7.0] == "Strongly Agree"
    for k in (2, 4):
        ok = df[f"PRDS{k}"].notna()
        assert (df.loc[ok, f"PRDS{k}t"] == 8 - df.loc[ok, f"PRDS{k}"]).all()
    out = df.rename(columns={p: p.lower() for p in prds})
    save(out, covs, [p.lower() for p in prds], "beshai_2017_prds_r", range(1, 8))

    fn = [f"Q8.1_{i}" for i in range(1, 10)]
    ov = ["Q8.2_1", "Q8.2_2"]
    sy = [f"Q8.{i}_1" for i in range(3, 13)]
    full = df[fn + ov + sy].notna().all(axis=1)
    assert (df.loc[full, fn + ov + sy].sum(axis=1) + 10 == df.loc[full, "NewFIQR"]).all()
    ren = {c: f"fiqr_f{i}" for i, c in enumerate(fn, 1)}
    ren.update({c: f"fiqr_o{i}" for i, c in enumerate(ov, 1)})
    ren.update({c: f"fiqr_s{i:02d}" for i, c in enumerate(sy, 1)})
    out = df.rename(columns=ren)
    save(out, covs, list(ren.values()), "beshai_2017_fiqr", range(0, 12))

    mpq = [f"Q6.1_{i}" for i in range(1, 16)]
    assert vl["Q6.1_1"] == {1.0: "None", 2.0: "Mild", 3.0: "Moderate", 4.0: "Severe"}
    out = df.rename(columns={c: f"mpq{i:02d}" for i, c in enumerate(mpq, 1)})
    save(out, covs, [f"mpq{i:02d}" for i in range(1, 16)], "beshai_2017_sf_mpq", [1, 2, 3, 4])


if __name__ == "__main__":
    convert()
