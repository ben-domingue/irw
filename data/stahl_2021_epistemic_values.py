#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0258228
# DOI: 10.1371/journal.pone.0258228
# Paper: Stahl T, Turner J (2021). Epistemic values and the Big Five:
#   Personality characteristics of those who ascribe personal and moral value
#   to epistemic rationality. PLoS ONE 16(10): e0258228.
# Data: PLOS SI S2 File (s002, Study 1, 222 MTurk workers) and S3 File (s003,
#   Study 2, 345 University of Illinois at Chicago students), labelled .sav;
#   S1 File (s001) is the variable list.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# "Except for one demographic question (level of education), materials were
# identical in both studies" (Methods), and the item columns match one for
# one, so each instrument is ONE table with `cov_study` (1 MTurk, 2 student
# pool); Study 2 ids are offset by 1000.
# THREE output tables, items as answered (raw):
#   stahl_2021_mrs   Moralized Rationality Scale, MR1..MR9, 1-7.
#   stahl_2021_irs   Importance of Rationality Scale, IR1..IR6, 1-7.
#   stahl_2021_bfas  Big Five Aspect Scales, 100 items (Vol, Wit, Com, Pol,
#     Ind, Ord, Ent, Ass, Int, Ope 1-10), 1-5. Columns with an "R" suffix are
#     the reverse-keyed items AS ANSWERED; the deposit's "...rec" columns
#     equal 6 - x of them on every row and are not used.
# Covariates: gender (Male/Female/Other), age, race/ethnicity, education
#   (Study 1 only), study. Religion and the two political-outlook items
#   dropped (the economic item's stored codes 1..11 don't match its labels).
#
# Item text: NOT SHIPPED. The .sav variable labels carry the full English
#   wording of every item (study-authored-adjacent MRS/IRS by Stahl et al.
#   2016; BFAS by DeYoung et al. 2007, IPIP-based, public domain) -- a cheap
#   later pass once the register is checked.

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
BASE = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0258228."
RAW_DIR = os.environ.get("STAHL2021_RAW_DIR")
HDR = {"User-Agent": "IRW-Finder/1.0"}
ITEM = re.compile(r"(MR|IR|Vol|Wit|Com|Pol|Ind|Ord|Ent|Ass|Int|Ope)(\d+)R?")


def read(sfx):
    if RAW_DIR:
        path = [os.path.join(RAW_DIR, f) for f in os.listdir(RAW_DIR) if f.endswith(sfx + ".sav")][0]
        return pyreadstat.read_sav(path)
    r = requests.get(BASE + sfx, headers=HDR, timeout=180)
    r.raise_for_status()
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"_stahl2021_{sfx}.sav")
    with open(path, "wb") as f:
        f.write(r.content)
    out = pyreadstat.read_sav(path)
    os.remove(path)
    return out


def prep(df, meta, study):
    vl = meta.variable_value_labels
    items = [c for c in df.columns if ITEM.fullmatch(c)]
    assert len(items) == 115, len(items)
    out = pd.DataFrame({"id": range(1, len(df) + 1)})
    out["id"] += 1000 * (study - 1)
    out["cov_study"] = study
    out["cov_gender"] = df["Gender"].map(vl["Gender"]).values
    out["cov_age"] = df["Age"].values
    out["cov_race"] = df["Race"].map(vl["Race"]).values
    out["cov_education"] = df["Education"].map(vl["Education"]).values if "Education" in df else None
    for c in items:
        out[c] = df[c].values
    return out, items


def save(df, covs, items, name, values):
    long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= set(values)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=list(values))
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    d1, m1 = read("s002")
    d2, m2 = read("s003")
    assert (len(d1), len(d2)) == (222, 345)
    a, items1 = prep(d1, m1, 1)
    b, items2 = prep(d2, m2, 2)
    assert items1 == items2
    df = pd.concat([a, b], ignore_index=True)
    assert df["id"].is_unique
    covs = ["cov_study", "cov_gender", "cov_age", "cov_race", "cov_education"]
    mr = [c for c in items1 if c.startswith("MR")]
    ir = [c for c in items1 if c.startswith("IR")]
    bf = [c for c in items1 if c not in mr + ir]
    assert (len(mr), len(ir), len(bf)) == (9, 6, 100)
    save(df, covs, mr, "stahl_2021_mrs", range(1, 8))
    save(df, covs, ir, "stahl_2021_irs", range(1, 8))
    save(df, covs, bf, "stahl_2021_bfas", range(1, 6))


if __name__ == "__main__":
    convert()
