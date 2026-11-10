#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0288451
# DOI: 10.1371/journal.pone.0288451
# Paper: Mifsud C, Sammut G (2023). Worldviews and the role of social values
#   that underlie them. PLoS ONE 18(7): e0288451.
# Data: PLOS SI S1 (journal.pone.0288451.s001, .sav), 251 Prolific
#   participants aged 18-31 (156 female, as in the paper) who passed the
#   attention checks and completed both sessions.
# License: CC BY 4.0 (the article and its SI).
# Codebook: the .sav variable labels, each opening with the item's code
#   ("SDT1 It is important to them to form their views independently.");
#   one label reads "CONI 1It is ..." and is read as CONI1.
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; leads/plos_leads_2026-10-30.csv), overnight lane A
# 2026-11-10.
#
# TWO output tables, items as answered:
#   mifsud_2023_pvq_rr      Portrait Values Questionnaire-Revised, 57
#     portraits (3 per value x 19), 1-5 (the paper used a 5-point scale in
#     place of the usual 6). Item codes are the codes that open each variable
#     label (SDT1, HUM1, UNN1 ...).
#   mifsud_2023_worldviews  the five worldview vignettes (localised,
#     pragmatist, orthodox, reward, survivor), "applies to me" 1 not at all
#     .. 5 completely; codes are the vignette names from the labels.
# Dropped: the forced choice of best-fitting worldview, every derived value
#   score, MRAT-centred score and dummy.
# Covariates: age, gender, nationality (as typed: country names).
# `id` = pp.
#
# Item text: NOT SHIPPED. The labels carry the English wording of every
#   portrait and vignette; the PVQ-RR is Schwartz's (register: block), the
#   vignettes are study-authored (CC BY) -- the vignettes are a cheap later
#   pass.

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
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0288451.s001"
RAW = os.environ.get("MIFSUD2023_RAW")
WV = ["LOCALISED", "PRAGMATIST", "ORTHODOX", "REWARD", "SURVIVOR"]


def load():
    path = RAW
    if not path:
        r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"}, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, "_mifsud2023_tmp.sav")
        with open(path, "wb") as f:
            f.write(r.content)
    df, meta = pyreadstat.read_sav(path)
    if not RAW:
        os.remove(path)
    return df, meta


def save(df, covs, mapping, name):
    sub = df[["id"] + covs + list(mapping)].rename(columns=mapping)
    long = sub.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert set(long["resp"]) <= {1, 2, 3, 4, 5}
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    checks = run_qc(long, permitted_values=[1, 2, 3, 4, 5])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


def convert():
    df, meta = load()
    assert len(df) == 251 and df["pp"].is_unique
    lab = meta.column_names_to_labels
    pvq, wv = {}, {}
    for c in df.columns:
        text = (lab.get(c) or "").replace("CONI 1It", "CONI1 It")  # one label typo
        first = text.split(" ")[0]
        if re.fullmatch(r"[A-Z]{2,5}\d", first) and text.startswith(first + " It is"):
            pvq[c] = first
        elif first in WV:
            wv[c] = first.lower()
    assert len(pvq) == 57 and len(set(pvq.values())) == 57
    assert len(wv) == 5
    df["id"] = df["pp"].astype(int)
    df["cov_age"] = df["Age"]
    df["cov_gender"] = df["Gender"]
    df["cov_nationality"] = df["Nationality"].str.strip()
    assert (df["cov_gender"] == "Female").sum() == 156
    covs = ["cov_age", "cov_gender", "cov_nationality"]
    save(df, covs, pvq, "mifsud_2023_pvq_rr")
    save(df, covs, wv, "mifsud_2023_worldviews")


if __name__ == "__main__":
    convert()
