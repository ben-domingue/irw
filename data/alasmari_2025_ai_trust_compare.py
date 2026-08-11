#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0331003
# DOI: 10.1371/journal.pone.0331003
# SI: S1 Data (10.1371/journal.pone.0331003.s001), XLSX
#
# Companion file to alasmari_2025_ai_trust_confidence.py -- see that
# script's header for shared background. This file covers the second,
# distinct construct in the raw sheet: comparative AI-vs-other trust
# across five domains (self-driving, medical treatment, historical
# recall, logistics, personal-data recall). Each item's "other" referent
# differs (human / doctor / myself) but the response set is the same
# underlying trust-in-AI ordering, so each item is internally consistent
# even though the comparator label varies across items (datastandard.md:
# direction only needs to be consistent *within* an item).
#
# "Unsure" is dropped rather than coded as a scale point: per
# datastandard.md's guidance on ambiguous/non-response categories, this
# option reflects lack of a preference rather than a real intermediate
# step between "trust other more" and "trust both equally", so it is
# treated as a non-response and filtered out (not recoded, not imputed).
# Remaining categories form a clean 3-point ordinal:
#   1 = trust other (human/doctor/myself) more
#   2 = trust both equally
#   3 = trust AI more

import os
import io
import re
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0331003.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "  Age": "cov_age",
    " Gender": "cov_gender",
    " Familiarty": "cov_ai_familiarity",
    "Frequent use": "cov_ai_use_frequency",
}

ITEM_COLS = {
    " Self-driving ": "item_self_driving",
    " Suggest treatment ": "item_medical_treatment",
    "Recall historical ": "item_historical_recall",
    " logistics problem ": "item_logistics",
    " Recall personal data ": "item_personal_data_recall",
}


def _clean(s):
    return s.astype(str).str.strip("[] ").str.strip().str.lower()


def _map_resp(v):
    if v == "trust both equally":
        return 2
    if v == "unsure":
        return None
    if v == "trust ai more":
        return 3
    if re.match(r"^trust (a |)(human|doctor|myself) more$", v):
        return 1
    return None


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    df = df.rename(columns=COV_MAP)
    for c in COV_MAP.values():
        df[c] = _clean(df[c])

    df = df.rename(columns=ITEM_COLS)
    item_col_names = list(ITEM_COLS.values())
    for c in item_col_names:
        df[c] = _clean(df[c])

    cov_cols = list(COV_MAP.values())
    long = df[["id"] + cov_cols + item_col_names].melt(
        id_vars=["id"] + cov_cols, value_vars=item_col_names,
        var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(_map_resp)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "alasmari_2025_ai_trust_compare.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
