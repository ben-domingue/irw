#!/usr/bin/env python3
# Source: https://zenodo.org/records/7534902
# DOI: 10.1080/10911359.2023.2165589
#   Cambaz, H. Z., & Unal, A. (2023). "Comparing self-report and performance
#   measurement of wisdom in Turkish sample: Relations with
#   self-transcendence and cognitive flexibility." Journal of Human Behavior
#   in the Social Environment, 34(3), 361-372. (Found by Crossref title
#   search; the deposit has no related identifiers. Paywalled; read from a
#   PDF Ben supplied, 2026-10-02.)
#   Dataset: Cambaz, H. Z. (2023). Zenodo.
#   https://doi.org/10.5281/zenodo.7534902
# Data: data.sav (148 rows x 33 columns; Turkish young adults 18-32).
# License: CC BY 4.0 (Zenodo API).
#
# Item text: not shipped. Both label levels checked: no variable labels on
#   any column; value labels only on sex and the parental-education
#   covariates. The rating criteria are those of the Berlin wisdom
#   paradigm (Baltes & Staudinger); the dilemma used is in the paper.
#
# What ships: the only item-level data in the file are the five Berlin
# wisdom-paradigm criteria on which each participant's think-aloud answer to
# a life dilemma was rated -- factual knowledge, procedural knowledge,
# lifespan contextualism, value relativism, recognition/management of
# uncertainty. Their sum is the "total" column (asserted). The self-report
# instruments (ASTI "transcendence", SD-WISE "sandiego", the Cognitive
# Flexibility Inventory and its two subscales, and five SD-WISE subscales)
# are present only as scale totals, so they cannot ship.
# Response range, per the paper's Method: each criterion was rated on a
# 7-point scale (1 = not similar .. 7 = very similar to an ideal wise answer),
# so totals run 7-35. Asserted as the permitted set {1..7} for every item.
# Rater: the paper says the second author rated all responses and the first
# author one-fifth of them (ICC .57). The per-criterion ratings here cover all
# 148 people, so they are the second author's; "percent20" (30 rows) is the
# first author's TOTAL on that one-fifth subsample, with no per-criterion
# second ratings, so it is dropped and the table carries no rater column. The
# paper's N is 151 minus 3 misreadings of the task = 148, matching the file.
#
# Table (item codes are the source column names):
#   cambaz_2023_berlin_wisdom   factual, procedural, lifespanc, valurelativ,
#                               uncertainty
#
# Dropped:
#   - Totals: transcendence, sandiego, sr_flex, cf_alternatives, cf_control,
#     sd_emotinalregulation, sd_socialcounseling, sd_determination,
#     sd_insight, sd_prosocial, tolerance, total, percent20.
#   - total_emotion, totalusedword: counts (emotion words, words used) coded
#     from the think-aloud transcript, not ratings.
#   - control_like .. control_knowandsea: six 1-7 questions about the
#     dilemma whose wording is undocumented and which do not form a scale
#     (inter-item r from -.60 to .31); not shipped.
# id: row index. "paricipant_no" (1-151, unique) is a study sequence number
#   and is not shipped.
# Covariates: cov_sex (1 Kadin/female, 2 Erkek/male), cov_age,
#   cov_mother_education, cov_father_education (1 primary .. 4 university),
#   cov_perceived_ses (as entered, 1-6), cov_siblings.

import os
import sys
import tempfile
from pathlib import Path

import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/7534902/files/data.sav/content"

TABLE = "cambaz_2023_berlin_wisdom"
ITEMS = ["factual", "procedural", "lifespanc", "valurelativ", "uncertainty"]
PERMITTED = set(range(1, 8))
DROPPED = {"transcendence", "sandiego", "sr_flex", "cf_alternatives",
           "cf_control", "sd_emotinalregulation", "sd_socialcounseling",
           "sd_determination", "sd_insight", "sd_prosocial", "tolerance",
           "total", "percent20", "total_emotion", "totalusedword",
           "control_like", "control_stres", "control_willingtogo",
           "control_balance", "control_otherinterest", "control_knowandsea",
           "paricipant_no"}
COVS = {"sex": "cov_sex", "age": "cov_age",
        "mother_education": "cov_mother_education",
        "father_education": "cov_father_education",
        "perceived_ses": "cov_perceived_ses", "siblings": "cov_siblings"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (148, 33), d.shape

    known = set(ITEMS) | DROPPED | set(COVS)
    assert set(d.columns) == known, set(d.columns) ^ known
    assert d["paricipant_no"].is_unique
    assert not d.drop(columns="paricipant_no").duplicated().any()
    assert (d[ITEMS].sum(axis=1) == d["total"]).all()
    assert not any(meta.column_names_to_labels.get(c) for c in ITEMS)

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - PERMITTED
        assert not bad, (it, bad)
    pv = {i: PERMITTED for i in ITEMS}
    long = long[["id", "item", "resp"] + cov_cols]
    for c in cov_cols:
        long[c] = long[c].astype("Int64")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == len(ITEMS)
    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
