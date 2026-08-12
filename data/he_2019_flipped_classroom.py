#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0214624
# DOI: 10.1371/journal.pone.0214624

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ATTITUDES_URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0214624.s007"
SATISFACTION_URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0214624.s008"


def _load(url, tmp_name, group_col):
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = f"/tmp/{tmp_name}"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df = pd.read_excel(tmp)
    df = df.rename(columns={group_col: "cov_group"})
    df["id"] = df["cov_group"].astype(int) * 1000 + df["ID"].astype(int)
    df["cov_group"] = df["cov_group"].map({0: "flipped_classroom", 1: "lecture_based"})
    return df


def _write(df, item_cols, out_name, item_prefix):
    keep = ["id", "cov_group"] + item_cols
    sub = df[keep].copy()
    rename_map = {c: f"{item_prefix}_{c}" for c in item_cols}
    sub = sub.rename(columns=rename_map)
    item_cols = list(rename_map.values())
    for c in item_cols:
        sub[c] = pd.to_numeric(sub[c], errors="coerce")

    long = sub.melt(id_vars=["id", "cov_group"], value_vars=item_cols,
                     var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]  # 9 = not applicable/missing sentinel

    long = long[["id", "item", "resp", "cov_group"]]

    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    att = _load(ATTITUDES_URL, "he_2019_attitudes.xls", "group")
    att_items = list(range(1, 13))
    _write(att, att_items, "he_2019_flipped_classroom_attitudes", "attitude")

    sat = _load(SATISFACTION_URL, "he_2019_satisfaction.xls", "Group")
    sat_items = list(range(1, 9))
    _write(sat, sat_items, "he_2019_flipped_classroom_satisfaction", "satisfaction")


if __name__ == "__main__":
    convert()
