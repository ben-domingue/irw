#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0273968
# DOI: 10.1371/journal.pone.0273968
# Hewei & Youngsook (2022), "Factors affecting clothing purchase intention
# in mobile short video app: Mediation of perceived value and immersion
# experience", PLOS ONE. CC BY 4.0.
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0273968.s001

from __future__ import annotations

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0273968.s001"

COV_RENAME = {
    "Your gender is?": "cov_gender",
    "Your age is?": "cov_age_band",
    "Your education is?": "cov_education",
    "Your Monthly income is?": "cov_income_band",
    "Your social e-commerce Purchase experience is?": "cov_ecommerce_experience",
}
COV_COLS = list(COV_RENAME.values())


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    # Unnamed: 0 = row id, Unnamed: 1 = completion time (e.g. "162秒" = 162
    # seconds), Unnamed: 2 = IP address + geolocation (PII -- dropped).
    df = df.rename(columns={"Unnamed: 0": "id", "Unnamed: 1": "cov_completion_time_s"})
    df = df.rename(columns=COV_RENAME)
    df["cov_completion_time_s"] = df["cov_completion_time_s"].str.extract(r"(\d+)").astype(float)
    df = df.drop(columns=["Unnamed: 2"])

    item_cols = [c for c in df.columns if c not in (["id", "cov_completion_time_s"] + COV_COLS)]
    long = df.melt(id_vars=["id", "cov_completion_time_s"] + COV_COLS, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "cov_completion_time_s"] + COV_COLS]

    path = os.path.join(OUT_DIR, "hewei_2022_msva_purchase.csv")
    long.to_csv(path, index=False)
    print(f"hewei_2022_msva_purchase: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
