#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0205934
# DOI: 10.1371/journal.pone.0205934
# SI: S2 File ("Minimal data set"), SAV
#
# A lifestyle intervention improves sexual function of women with
# obesity and infertility: A 5 year follow-up of a RCT. Instrument is
# the McCoy Female Sexuality Questionnaire (MFSQ/MCC): 19 items, 18
# scored on a 7-point Likert scale across 5 domains (sexual interest,
# satisfaction, vaginal lubrication, orgasm, sex partner); the 19th
# item (MCC12) asks about frequency of intercourse in the past 4 weeks
# on a different (0-30) scale and is excluded here as a non-Likert
# item. `Treatment_group` (0=control/1=lifestyle intervention) maps to
# `treat`.
#
# IMPORTANT: the paper states "'non applicable' answers were replaced
# by the mean of at least 2 of the other items of the corresponding
# domain" when computing DOMAIN scores -- but inspection of the raw
# MCC1-19 item columns themselves shows a scattered set of non-integer
# values (e.g. 1.25, 2.35, 3.5) on an instrument documented as integer
# 1-7 Likert, present on nearly every item column. This means the
# mean-imputation was in fact applied at the item level in this shared
# file, not only when deriving domain totals as the text implies. Per
# datastandard.md's imputation-check rule, these non-integer values are
# dropped (kept only where resp is a clean integer in [1,7]) rather
# than shipped as if they were raw observations.

import os
import pandas as pd
import pyreadstat

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "journal.pone.0205934_S2_File.sav")
SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0205934.s002&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")

OUT_NAME = "wekker_2018_mfsq"
ITEM_COLS = [f"MCC{i}" for i in range(1, 20) if i != 12]  # exclude MCC12 (non-Likert)


def convert():
    if not os.path.exists(RAW):
        import requests
        r = requests.get(SI_URL, headers=UA, timeout=60)
        r.raise_for_status()
        with open(RAW, "wb") as f:
            f.write(r.content)

    df, meta = pyreadstat.read_sav(RAW)

    assert df["ID"].nunique() == len(df), "id column not unique"
    df = df.rename(columns={"ID": "id"})
    df["treat"] = (df["Treatment_group"] == 1).astype(int)

    long = df.melt(id_vars=["id", "treat"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    # drop non-integer (imputed) values; keep clean 1-7 Likert responses
    long = long[(long["resp"] % 1 == 0)]
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]
    long["resp"] = long["resp"].astype(int)
    long = long.reset_index(drop=True)

    long = long[["id", "item", "resp", "treat"]]
    path = os.path.join(OUT_DIR, f"{OUT_NAME}.csv")
    long.to_csv(path, index=False)
    print(f"{OUT_NAME}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
