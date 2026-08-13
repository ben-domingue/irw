#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0349305
# DOI: 10.1371/journal.pone.0349305
#
# "Understanding travel intention formation in government culture and
# tourism TikTok accounts: An integration of the SOR model and emotion
# appraisal theory". S2 File (.s002, XLS) is the raw survey dataset
# (N=406). Item columns are 29 Likert-scale statements across five
# constructs (information quality, service quality, destination image,
# positive emotions, travel intention); demographic columns become
# covariates. No PII. CC BY 4.0.

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0349305.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = {
    "Have watched or followed such accouts": "cov_followed_account",
    "Gender": "cov_gender",
    "Birth Cohort": "cov_birth_cohort",
    "Education": "cov_education",
    "Occupation": "cov_occupation",
    "Monthly disposable income (RMB)": "cov_income",
    "Daily TikTok ssage duration": "cov_tiktok_use_duration",
}

ITEM_COLS = [
    "Of sufficient depth", "Specific", "Accurate",
    "Effective for planning a trip", "Useful for planning a trip",
    "Helpful for planning a trip", "Easy to understand",
    "Concise and appropriate", "Harmonious and consistent",
    "Respond promptly to online comments",
    "Suggestions can receive timely feedback",
    "Have many interactive service features", "Trustworthy",
    "Sufficient professional knowledge", "Friendly and courteous",
    "Updated promptly and stably", "All kinds of services can be used",
    "Authoritative official information source",
    "Attractive cultural or natural landscapes",
    "Unique environmental ambiance", "Favorable overall image",
    "Relaxed", "Pleasant", "Excited", "Interesting", "Surprising",
    "Recommend it to others.", "Intend to visit it in the future",
    "Say positive things about it to other people",
]


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))

    df = df.rename(columns={"index": "id"})
    df = df.rename(columns=COV_COLS)
    cov_cols = list(COV_COLS.values())

    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id column is not unique per row"

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # 7-point Likert scale
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "sun_2026_tiktok_travel.csv")
    long.to_csv(out_path, index=False)
    print(f"sun_2026_tiktok_travel: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
