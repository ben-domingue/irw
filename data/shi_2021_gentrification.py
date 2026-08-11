#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0248265
# S1 Data: https://doi.org/10.1371/journal.pone.0248265.s001
# DOI: 10.1371/journal.pone.0248265
#
# Shi, Duan, Xu, Li (2021) "Effect analysis of the driving factors of
# super-gentrification using structural equation modeling". 23-item
# questionnaire on driving factors of super-gentrification, 5-point Likert
# scale (1=Can be ignored ... 5=Extremely important), N=209.

import os
import io
import re
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0248265.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"Serial number": "id"})
    assert df["id"].nunique() == len(df)

    # Item columns are numbered 5-27 in the questionnaire (columns after the
    # 4 demographic/covariate questions).
    item_cols = [c for c in df.columns if re.match(r"^(?:[5-9]|1[0-9]|2[0-7])、", c)]
    assert len(item_cols) == 23, len(item_cols)

    rename_items = {c: "item_" + re.match(r"^(\d+)、", c).group(1) for c in item_cols}
    df = df.rename(columns=rename_items)
    item_cols = list(rename_items.values())

    cov_rename = {
        "Nationality": "cov_nationality",
        "Data collection mode": "cov_collection_mode",
        "1、Your age: ": "cov_age",
        "2、Time of work or research related to gentrification": "cov_experience",
        "3、Your occupation:": "cov_occupation",
        "4、Your education: ": "cov_education",
    }
    df = df.rename(columns=cov_rename)
    cov_cols = list(cov_rename.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    out_name = "shi_2021_gentrification"
    out_path = os.path.join(OUT_DIR, out_name + ".csv")
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
