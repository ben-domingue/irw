#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0166410
# DOI: 10.1371/journal.pone.0166410
# Paper: Zeng X, Pan Y, Zhou H, Yu S, Liu X (2016). Exploring Different
#   Patterns of Love Attitudes among Chinese College Students. PLoS ONE
#   11(11): e0166410.
# Data: PLOS SI S4 (journal.pone.0166410.s004, .sav), 389 students at 10
#   Beijing universities (191 female, as in the paper).
# License: CC BY 4.0 (the article and its SI).
# Codebook: none; scales and subscale names (pinyin) from the paper.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# FIVE output tables, 1-5, items as answered (codes as deposited):
#   zeng_2016_las  Love Attitudes Scale short form (Chinese), 22 items as
#     deposited (paper: 24): LoveLangMan (eros), LoveYouXi (ludus),
#     LoveYouYi (storge), LoveXianShi (pragma), LoveFengXian (mania),
#     LoveZhanYou (agape). The paper states 1 = strongly agree, 5 = strongly
#     disagree for this scale.
#   zeng_2016_sas  Multidimensionality of Sexual Attitudes (Chinese), 21
#     items: SexGongJu, SexJiaoLiu, SexKuanRong, SexYuYue, SexZeRen.
#   zeng_2016_neo_deliberation / _neo_dutifulness / _neo_self_discipline
#     NEO PI-R facets C6 (JinShen), C3 (JinZe), C5 (ZiLv), 8 items each.
#     Items suffixed R are reverse-keyed AS ANSWERED (they correlate
#     negatively with their facet-mates), not recoded.
# EM-IMPUTED CELLS DROPPED: the paper replaced missing values with the EM
#   algorithm; those cells are the deposit's non-integer values (e.g.
#   3.0095), and the deposited subscale means were computed before imputation
#   (they equal the item mean only on rows without such cells). All
#   non-integer cells are dropped.
# Covariates: gender, grade (year of study).
# `id` = the deposit's ID.
#
# Item text: NOT SHIPPED. No wording deposited (published instruments).

import os
import re
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0166410.s004"
RAW = os.environ.get("ZENG2016_RAW")


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_zeng2016_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, meta = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df, meta


def items_of(df, prefixes):
    out = []
    for p in prefixes:
        out += [c for c in df.columns if re.fullmatch(p + r"\d+R?", c)]
    return out


def save(df, covs, items, name, n):
    assert len(items) == n, (name, len(items))
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    frac = long["resp"] != long["resp"].round()
    long = long[~frac].copy()
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=[1, 2, 3, 4, 5])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} dropped_imputed={int(frac.sum())}")


def convert():
    df, meta = load()
    assert len(df) == 389 and df["ID"].is_unique
    vl = meta.variable_value_labels
    df["id"] = df["ID"].astype(int)
    df["cov_gender"] = df["Gender"].map(vl["Gender"])
    df["cov_grade"] = df["Grade"]
    assert (df["cov_gender"] == "female").sum() == 191
    covs = ["cov_gender", "cov_grade"]
    save(df, covs, items_of(df, ["LoveLangMan", "LoveYouXi", "LoveYouYi", "LoveXianShi",
                                 "LoveFengXian", "LoveZhanYou"]), "zeng_2016_las", 22)
    save(df, covs, items_of(df, ["SexGongJu", "SexJiaoLiu", "SexKuanRong", "SexYuYue", "SexZeRen"]),
         "zeng_2016_sas", 21)
    save(df, covs, items_of(df, ["JinShen"]), "zeng_2016_neo_deliberation", 8)
    save(df, covs, items_of(df, ["JinZe"]), "zeng_2016_neo_dutifulness", 8)
    save(df, covs, items_of(df, ["ZiLv"]), "zeng_2016_neo_self_discipline", 8)


if __name__ == "__main__":
    convert()
