#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0197924
# DOI: 10.1371/journal.pone.0197924
#
# Konerding, Bowen, Elkhuizen, Faubel, Forte, Karampli, Malmstrom, Pavi,
# Torkki (2019). Development of a universal short patient satisfaction
# questionnaire on the basis of SERVQUAL: Psychometric analyses with data of
# diabetes and stroke patients from six different European countries.
# PLOS ONE.
#
# S1 File (SAV) contains raw per-item responses to the 7-item short patient
# satisfaction questionnaire (6 SERVQUAL-style perception items plus an
# overall satisfaction item), each on a 1-7 scale ("strongly disagree" to
# "strongly agree" / "extremely dissatisfied" to "extremely satisfied").
# Values are stored as a mix of numeric codes and text-labelled endpoints;
# value labels confirm 1-7 range. N=1884 across diabetes and stroke patients
# in six countries.

import io
import os
import requests
import pandas as pd
import pyreadstat

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SRC_URL = "https://doi.org/10.1371/journal.pone.0197924.s001"

ITEM_COLS = [
    "UpToDateEquipment", "ServiceOnTime", "ReactPromptly", "Polite",
    "PersonalAttention", "RightCommunication", "ServicesSatisfaction",
]
COV_MAP = {
    "Med_Cond": "cov_condition",
    "Country": "cov_country",
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Education": "cov_education",
    "Motherlang": "cov_mother_language",
    "MasterMainLang": "cov_masters_main_language",
}


def convert():
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp_path = "/tmp/konerding_2019_s1.sav"
    with open(tmp_path, "wb") as f:
        f.write(r.content)
    # apply_value_formats=False: keep raw numeric codes (1-7) for the item
    # columns instead of the mixed numeric/text-label representation pandas'
    # read_spss returns (text-only endpoints like "Strongly agree" contain
    # no digits and would otherwise be lost).
    df, meta = pyreadstat.read_sav(tmp_path, apply_value_formats=False)
    # Re-apply value labels only to covariate columns, for readability.
    df_labeled, _ = pyreadstat.read_sav(tmp_path, apply_value_formats=True)
    for c in COV_MAP:
        if c in df.columns and c not in ITEM_COLS:
            df[c] = df_labeled[c]

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    df = df.rename(columns=COV_MAP)
    cov_cols = list(COV_MAP.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "konerding_2019_patientsatisfaction.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
