#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0190746
# DOI: 10.1371/journal.pone.0190746
# Paper: Shen B, Qu W, Ge Y, Sun X, Zhang K (2018). The relationship between
#   personalities and self-report positive driving behavior in a Chinese
#   sample. PLoS ONE 13(1): e0190746.
# Data: PLOS Supporting Information S1 Table (journal.pone.0190746.s001,
#   .xlsx "raw data"; row 1 block names, row 2 the full English item wording).
#   448 licensed drivers in Beijing.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 7.
#
# THREE output tables, items as answered, numbered as in the headers:
#   shen_2018_pdbs  Positive Driver Behaviours Scale (Chinese, 13 items),
#     1 never .. 6 very often.
#   shen_2018_dbq   Driver Behaviour Questionnaire, 28 items, 1-5.
#   shen_2018_dddi  Dula Dangerous Driving Index, 28 items, 1-5.
#   None of the three has reverse-keyed items (all items in a block point the
#   same way; every inter-item correlation is positive).
# Note: the deposit holds all 448 respondents; the paper dropped 27 for
#   careless responding (N = 421) without saying which. All 448 are kept.
# Dropped: the BFI-44. Its reverse-keyed items correlate near zero (-0.10 to
#   +0.07) with the direct items of their own scale rather than clearly
#   negatively, so it cannot be told whether they were recoded before
#   deposit; dropped under the 2026-11-08 rule. Mileage, fines and penalty
#   points dropped.
# Covariates: gender, age, education, driving years, accidents in the past
#   three years.
# `id` is the deposit's questionnaire number (1001..1449).
#
# Item text: NOT SHIPPED. Cheap: row 2 carries the English wording of every
#   item (PDBS, DBQ and DDDI are published instruments; check the register).

import os
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0190746.s001"
RAW = os.environ.get("SHEN2018_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_shen2018_tmp.xlsx")
        with open(path, "wb") as f:
            f.write(r.content)
    top = pd.read_excel(path, sheet_name=0, header=None, nrows=1)
    df = pd.read_excel(path, sheet_name=0, header=1)
    if not RAW:
        os.remove(path)
    return top, df


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
    top, df = load()
    assert len(df) == 448
    blocks = top.iloc[0].tolist()
    assert (blocks[10], blocks[23], blocks[51], blocks[79]) == ("PDBS", "DBQ", "DDDI", "BFI")
    c = list(df.columns)
    add = pd.DataFrame(
        {
            "id": df[c[0]].astype(int),
            "cov_gender": df[c[1]].str.strip(),
            "cov_age": df[c[2]],
            "cov_education": df[c[3]].str.strip(),
            "cov_driving_years": df[c[4]],
            "cov_accidents_3y": df[c[7]],
        }
    )
    df = pd.concat([df, add], axis=1)
    assert df["id"].is_unique
    assert c[4] == "Driving years" and c[7] == "Accidents in the past three years"
    covs = ["cov_gender", "cov_age", "cov_education", "cov_driving_years", "cov_accidents_3y"]

    for lo, hi, pre, name, vals in [
        (10, 23, "pdbs", "shen_2018_pdbs", range(1, 7)),
        (23, 51, "dbq", "shen_2018_dbq", range(1, 6)),
        (51, 79, "dddi", "shen_2018_dddi", range(1, 6)),
    ]:
        src = c[lo:hi]
        for k, s in enumerate(src, 1):
            assert str(s).startswith(f"{k}. "), s
        names = [f"{pre}{k:02d}" for k in range(1, len(src) + 1)]
        out = df[["id"] + covs + src].copy()
        out[src] = out[src].apply(pd.to_numeric, errors="coerce")
        assert (out[src].corr().values > 0).all()
        out.columns = ["id"] + covs + names
        save(out, covs, names, name, vals)


if __name__ == "__main__":
    convert()
