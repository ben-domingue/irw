#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0175019
# DOI: 10.1371/journal.pone.0175019
# Paper: Rees SJ, Tay AK, Savio E, Maria Da Costa Z, Silove D (2017).
#   Identifying a combined construct of grief and explosive anger as a response
#   to injustice amongst survivors of mass conflict: A latent class analysis of
#   data from Timor-Leste. PLoS ONE 12(4): e0175019.
# Data: PLOS Supporting Information S1 Dataset (journal.pone.0175019.s001,
#   Stata .dta with variable and value labels), 2,964 adults in an urban and a
#   rural village of Timor-Leste, interviewed 2010-2011.
# License: CC BY 4.0 (the article and its SI).
#
# Worked from the cleaned leads list of 2026-11-07 (refined_flag
# recoverable_format; source leads/plos_leads_2026-10-30.csv), leads batch 4.
#
# FOUR output tables, item codes the deposit's own, codes per its value labels:
#   rees_2017_grief                Grief1-4 (longing/yearning, bitterness over
#     the death, life empty without the person, functional impairment), 1
#     "Almost never" to 5 "Always". The grief items were asked about the
#     loss that most affected the respondent; code 0 (unlabelled; 11 people
#     hold it on all four items, one more on two) is read as "no loss
#     reported" and dropped.
#   rees_2017_anger_reactions      Anger6, 7, 8a, 9a, 10a: "When you became
#     very angry, how often did you feel out of control / about to explode /
#     like shouting / like throwing or breaking things / like pushing or
#     hitting someone", 0 "Circle 1: Never" to 6 "Circle 7: every time I get
#     angry". Asked of everyone (all codes occur whatever the screening answer).
#     One Anger6 cell holds 99, a sentinel, dropped.
#   rees_2017_anger_physiological  Anger13a-l, 12 bodily reactions during anger
#     (racing heart, feeling hot, chest pain, ...), 0 No / 1 Yes.
#   rees_2017_anger_beliefs        Anger15b-l, 11 beliefs about showing or
#     holding in anger ("When you are angry, you should show it", ...), 0
#     "Circle 1: Never" to 6 "Circle 7: every time".
# Covariates: female (0/1, the deposit's), age group (its five labelled
#   groups), rural/urban village, employment category (three labelled
#   groups), married (0/1).
# Dropped: the screening questions and their follow-ups (Anger1-5: two yes/no
#   screens and frequency/upset items asked conditionally), the conditional
#   "did you actually shout/throw/hit" items (Anger8b, 9b, 10b, 11), the
#   single items Anger12 (0-10 anger intensity), Anger14 and Anger15a (each
#   its own response scale); the derived K10 cut-off, poverty and
#   trauma-event counts.
# `id` is the row index (the deposit has no respondent id).
#
# Item text: NOT SHIPPED. The variable labels carry short item wording (used
#   above); not built in this batch.

import os
import sys

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0175019.s001"
RAW = os.environ.get("REES_RAW")
HDR = {"User-Agent": "IRW-Finder/1.0"}
TABLES = {
    "grief": (["Grief1", "Grief2", "Grief3", "Grief4"], range(1, 6)),
    "anger_reactions": (["Anger6", "Anger7", "Anger8a", "Anger9a", "Anger10a"], range(0, 7)),
    "anger_physiological": ([f"Anger13{c}" for c in "abcdefghijkl"], range(0, 2)),
    "anger_beliefs": ([f"Anger15{c}" for c in "bcdefghijkl"], range(0, 7)),
}


def load():
    src = RAW
    if not src:
        r = requests.get(URL, headers=HDR, timeout=180)
        r.raise_for_status()
        os.makedirs(OUT_DIR, exist_ok=True)
        src = os.path.join(OUT_DIR, "_rees_tmp.dta")
        open(src, "wb").write(r.content)
    df, meta = pyreadstat.read_dta(src)
    if not RAW:
        os.remove(src)
    return df, meta


def convert():
    df, meta = load()
    assert df.shape == (2964, 52), df.shape
    txt = [c for c in df.columns if pd.api.types.is_string_dtype(df[c]) or df[c].dtype == object]
    print(f"PII screen: {len(txt)} text columns of {len(df.columns)} examined: {txt}")
    assert len(df.columns) > 0 and not txt
    lab = lambda v: meta.value_labels[meta.variable_to_label[v]]  # noqa: E731
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1
    df["cov_female"] = df["female"].astype(int)
    df["cov_age_group"] = df["AgeGp3"].map(lab("AgeGp3"))
    df["cov_urban"] = df["Rural_Urban"].map(lab("Rural_Urban"))
    df["cov_employment"] = df["Employment_Cat"].map(lab("Employment_Cat"))
    df["cov_married"] = df["marry"].astype(int)
    covs = ["cov_female", "cov_age_group", "cov_urban", "cov_employment", "cov_married"]
    assert df[covs].notna().all().all()
    for name, (items, perm) in TABLES.items():
        long = df[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long[long["resp"].notna()].copy()
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        if name == "grief":
            assert (long["resp"] == 0).sum() == 46, (long["resp"] == 0).sum()
            long = long[long["resp"] != 0]
        if name == "anger_reactions":
            assert (long["resp"] == 99).sum() == 1
            long = long[long["resp"] != 99]
        assert set(long["resp"]) <= set(perm), (name, set(long["resp"]))
        long = long[["id", "item", "resp"] + covs]
        assert not long.duplicated(["id", "item"]).any()
        checks = run_qc(long, permitted_values={c: list(perm) for c in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:150]}")
        out = f"rees_2017_{name}"
        os.makedirs(OUT_DIR, exist_ok=True)
        long.to_csv(os.path.join(OUT_DIR, out + ".csv"), index=False)
        print(f"{out}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()}")


if __name__ == "__main__":
    convert()
