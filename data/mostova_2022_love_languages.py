#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0269429
# DOI: 10.1371/journal.pone.0269429
# Paper: Mostova O, Stolarski M, Matthews G (2022). I love the way you love
#   me: Responding to partner's love language preferences boosts satisfaction
#   in romantic heterosexual couples. PLoS ONE 17(6): e0269429.
# Data: PLOS SI S1 Data (journal.pone.0269429.s002, .csv), one row per couple:
#   100 heterosexual couples, M_* = male partner, F_* = female partner
#   (S1 File lists the variable names).
# License: CC BY 4.0 (the article and its SI).
#
# Worked from leads/plos_leads_2026-11-10a.csv (hour-1110 lane A).
#
# Partners are stacked: 200 ids, id = 2*couple - 1 (male) / 2*couple
#   (female); `cluster_id` = couple number (the partners are nested in it).
# FIVE output tables, items as answered, item codes = the deposit's names
#   without the M_/F_ prefix (lower-cased):
#   mostova_2022_lls_express  Love Language Scale, expressing love, 20 items
#     (4 each: acts of service, physical touch, words of affirmation, quality
#     time, gifts), 1-5.
#   mostova_2022_lls_felt     the same 20 items for feeling loved, 1-5.
#   mostova_2022_ras          Relationship Assessment Scale, 7 items, 1-5.
#   mostova_2022_iss          Index of Sexual Satisfaction, 24 items, 1-7.
#   mostova_2022_iri          Interpersonal Reactivity Index, 28 items, 1-5
#     (one female cell coded 0 dropped).
#   Blank cells (" ") are missing. Reverse-keyed items as answered.
# Covariates: gender, age. Nationality (free text), relationship length and
#   the sexual-history items are not carried.

import os
import re
import sys

import pandas as pd
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0269429.s002"
RAW = os.environ.get("MOSTOVA2022_RAW")

SCALES = [("lls_express", r"LLS_.*_Express_\d+", range(1, 6)),
          ("lls_felt", r"LLS_.*_Felt_\d+", range(1, 6)),
          ("ras", r"RAS\d+", range(1, 6)),
          ("iss", r"ISS\d+", range(1, 8)),
          ("iri", r"IRI\d+", range(1, 6))]


def load():
    if RAW:
        return pd.read_csv(RAW, dtype=str)
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
    r.raise_for_status()
    from io import StringIO
    return pd.read_csv(StringIO(r.text), dtype=str)


def partner(df, s, gender):
    cols = [c for c in df.columns if c.startswith(s + "_")]
    out = df[cols].copy()
    out.columns = [c[2:] for c in cols]
    couple = pd.to_numeric(df["CoupleNumber"])
    out["cluster_id"] = couple
    out["id"] = 2 * couple - (1 if s == "M" else 0)
    out["cov_gender"] = gender
    out["cov_age"] = pd.to_numeric(out["Age"])
    return out


def convert():
    df = load()
    assert len(df) == 100
    assert (df["CoupleNumber"] == df["F_Couple_Number"]).all()
    assert (df["M_Gender"] == "1").all() and (df["F_Gender"] == "0").all()
    both = pd.concat([partner(df, "M", "male"), partner(df, "F", "female")], ignore_index=True)
    assert both["id"].is_unique
    covs = ["cov_gender", "cov_age"]
    for label, pat, values in SCALES:
        src = [c for c in both.columns if re.fullmatch(pat, c)]
        sub = both[["id", "cluster_id"] + covs + src].rename(columns={c: c.lower() for c in src})
        long = sub.melt(id_vars=["id", "cluster_id"] + covs, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"].str.strip(), errors="coerce")
        long = long[long["resp"].isin(list(values))].copy()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "cluster_id"] + covs].sort_values(["id", "item"])
        checks = run_qc(long, permitted_values=list(values))
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        os.makedirs(OUT_DIR, exist_ok=True)
        name = f"mostova_2022_{label}"
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
