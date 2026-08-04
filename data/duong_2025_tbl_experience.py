#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0323656
# DOI: 10.1371/journal.pone.0323656
# A pre-post quasi-experimental study of team-based learning effectiveness
# for Vietnamese nursing students (Duong et al., PLOS ONE 2025)
# SI: journal.pone.0323656_S1_Dataset.sav, CC BY 4.0
#
# The file contains several pre/post (before TBL course = wave 1, after = wave
# 2) instrument blocks. This script ships the two blocks whose item-to-column
# correspondence is unambiguous:
#   - B1-B19 / B1.1-B19.1: team-based-learning experience scale (19 items)
#   - C1-C4  / C1.1-C4.1 : team self-efficacy/confidence scale (4 items)
# The D-block (TBL-SAI) and E-block (class engagement) are NOT shipped here:
# both contain "_Q" suffixed columns alongside separately-labelled plain
# columns (e.g. D4_Q vs. D4, E4_Q vs. E4) whose raw-vs-recoded relationship
# could not be determined from the data/column labels alone without the
# original questionnaire instrument, so they are left for human review.

import os

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0323656.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch_data() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp_path = "/tmp/_duong_2025_s1.sav"
    with open(tmp_path, "wb") as f:
        f.write(r.content)
    df, _ = pyreadstat.read_sav(tmp_path)
    os.remove(tmp_path)
    return df


def build_scale(df: pd.DataFrame, item_nums, prefix: str, cov_cols):
    pre_cols = [f"{prefix}{i}" for i in item_nums]
    post_cols = [f"{prefix}{i}.1" for i in item_nums]

    pre = df[["id"] + cov_cols + pre_cols].copy()
    pre = pre.rename(columns={c: c for c in pre_cols})
    pre_long = pre.melt(id_vars=["id"] + cov_cols, value_vars=pre_cols,
                         var_name="item", value_name="resp")
    pre_long["wave"] = 1

    post = df[["id"] + cov_cols + post_cols].copy()
    post_long = post.melt(id_vars=["id"] + cov_cols, value_vars=post_cols,
                           var_name="item", value_name="resp")
    post_long["item"] = post_long["item"].str.replace(".1", "", regex=False)
    post_long["wave"] = 2

    long = pd.concat([pre_long, post_long], ignore_index=True)
    long["item"] = prefix + long["item"].str.replace(prefix, "", regex=False)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 5)].reset_index(drop=True)

    out_cols = ["id", "item", "resp", "wave"] + cov_cols
    return long[out_cols].sort_values(["id", "wave", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch_data()

    df = df.rename(columns={"SC": "id"})
    assert df["id"].nunique() == len(df), "id column not unique"

    df = df.rename(columns={"A1": "cov_birth_year", "A2": "cov_gender"})
    cov_cols = ["cov_birth_year", "cov_gender"]

    b_scale = build_scale(df, range(1, 20), "B", cov_cols)
    write_scale(b_scale, "duong_2025_tbl_experience.csv")

    c_scale = build_scale(df, range(1, 5), "C", cov_cols)
    write_scale(c_scale, "duong_2025_tbl_confidence.csv")


if __name__ == "__main__":
    convert()
