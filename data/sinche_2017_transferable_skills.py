#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0185023
# DOI: 10.1371/journal.pone.0185023
# S1 File (SAV) -- national survey of science PhDs. Two 15-item scales using
# the same 15 transferable-skill labels: (1) how much the skill was
# developed during doctoral training (Doc_Skill_1-15, 1-5), and (2) how
# important the skill is for the respondent's current job
# (Employ_Skill_1R-15R, 1-5, asked only of the ~3800 currently-employed
# subset). Written as two separate scale files.

import os
import io

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://doi.org/10.1371/journal.pone.0185023.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/_sinche_2017.sav"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df, meta = pyreadstat.read_sav(tmp)
    os.remove(tmp)
    return df


def build(df, item_cols, item_prefix, out_name):
    d = df[["SUBJ_ID", "Gender"] + item_cols].copy()
    d = d.rename(columns={"SUBJ_ID": "id", "Gender": "cov_gender"})
    item_map = {c: f"{item_prefix}{i+1}" for i, c in enumerate(item_cols)}
    d = d.rename(columns=item_map)
    item_names = list(item_map.values())

    assert d["id"].nunique() == len(d), "id not unique"

    long = d.melt(id_vars=["id", "cov_gender"], value_vars=item_names,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp", "cov_gender"]
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    out_dir_abs = os.path.abspath(OUT_DIR)
    os.makedirs(out_dir_abs, exist_ok=True)
    out_path = os.path.join(out_dir_abs, out_name)
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()

    doc_cols = [f"Doc_Skill_{i}" for i in range(1, 16)]
    build(df, doc_cols, "skill_dev_", "sinche_2017_skill_development.csv")

    employ_cols = [f"Employ_Skill_{i}R" for i in range(1, 16)]
    build(df, employ_cols, "skill_imp_", "sinche_2017_skill_importance.csv")


if __name__ == "__main__":
    convert()
