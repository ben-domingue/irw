#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0266802
# DOI: 10.1371/journal.pone.0266802
#
# Reyes, Vance-Chalcraft (2022). Understanding undergraduate students'
# eHealth usage and views of the patient-provider relationship. PLOS ONE.
#
# S3 File (CSV) contains raw per-item responses to the 8-item eHealth
# Literacy Scale (eHEALS; Norman & Skinner, 2006), 1-5 scale
# (1=strongly agree ... 5=strongly disagree, per the in-column codebook
# text). N=527 respondents after excluding incomplete surveys. The `ID`
# column has one duplicate value (538 appears twice) so the row index is
# used as `id` instead, per datastandard.md guidance.
#
# Excluded: all other survey columns (open-ended, ranking, and categorical
# items about health information sources / patient-provider relationship
# views - not part of a shared repeated-item scale), demographic free-text
# columns.
#
# Row 0 of the raw CSV is a Qualtrics codebook "key" row (e.g. cov_age =
# "Key: 1 = 18-20, 2 = 21-24, 3 = 25+"), not a respondent -- it must be
# dropped before processing. An earlier version of this script didn't drop
# it: the digit-extraction regex below pulled "1" out of each item's key
# text ("Key: 1 = Strongly agree...") and shipped a fake id=1 respondent
# with resp=1 on all 8 items and garbled cov_* values (the raw key text
# itself).

import os
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
SRC_URL = "https://doi.org/10.1371/journal.pone.0266802.s006"

COV_RENAME = {
    "What is your age?": "cov_age",
    "What is your gender identity? - Selected Choice": "cov_gender",
    "What is your racial or ethnic identification? - Selected Choice": "cov_race_ethnicity",
    "What is your major?": "cov_major",
}


def convert():
    import io
    import requests
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))

    item_cols = [c for c in df.columns if c.startswith("eHEALS question")]
    assert len(item_cols) == 8, item_cols

    # Drop the Qualtrics codebook "key" row (row 0) -- not a respondent.
    df = df[~df["What is your age?"].astype(str).str.startswith("Key:")]

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COV_RENAME)
    cov_cols = [c for c in COV_RENAME.values() if c in df.columns]

    # Rename item columns to short labels eheals_1..eheals_8. The source has
    # a typo "eHEALS question 61" for question 6, so map by explicit
    # substring match rather than parsing digits generically.
    item_rename = {}
    for c in item_cols:
        if "question 1 " in c or "question 1f" in c.lower():
            item_rename[c] = "eheals_1"
        elif "question 2 " in c:
            item_rename[c] = "eheals_2"
        elif "question 3 " in c:
            item_rename[c] = "eheals_3"
        elif "question 4 " in c:
            item_rename[c] = "eheals_4"
        elif "question 5 " in c:
            item_rename[c] = "eheals_5"
        elif "question 61" in c:
            item_rename[c] = "eheals_6"
        elif "question 7 " in c:
            item_rename[c] = "eheals_7"
        elif "question 8 " in c:
            item_rename[c] = "eheals_8"
    assert len(item_rename) == 8, (item_cols, item_rename)
    df = df.rename(columns=item_rename)
    item_cols = list(item_rename.values())

    for c in item_cols:
        df[c] = df[c].astype(str).str.extract(r"(\d+)")[0]

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "reyes_2022_eheals.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
