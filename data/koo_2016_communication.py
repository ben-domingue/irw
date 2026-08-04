#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0146545
# DOI: 10.1371/journal.pone.0146545
#
# Koo LW, Horowitz AM, Radice SD, Wang MQ, Kleinman DV (2016) Nurse
# Practitioners' Use of Communication Techniques: Results of a Maryland Oral
# Health Literacy Survey. PLoS ONE 11(1): e0146545.
#
# S1 Data (SAV, N=229 nurse practitioners) contains two multi-item Likert
# batteries relevant to the paper's "recommended communication techniques"
# construct:
#   - Q4a_1..Q4a_12: frequency of use of 12 communication techniques
#   - Q5a_1..Q5a_18: opinion of effectiveness of 18 communication techniques
# Both are coded 1-4 (Likert) with 9 used as a "not applicable / does not use"
# sentinel -- filtered out here rather than treated as a 5th scale point.

import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0146545.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp_path = "/tmp/_koo_2016_s1.sav"
    with open(tmp_path, "wb") as f:
        f.write(r.content)
    df, _meta = pyreadstat.read_sav(tmp_path, apply_value_formats=False)
    os.remove(tmp_path)
    return df


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    d = df[["ID"] + item_cols].copy().rename(columns={"ID": "id"})
    d["id"] = pd.to_numeric(d["id"], errors="coerce")
    d = d.dropna(subset=["id"])
    assert d["id"].is_unique, "id column not unique"

    long = d.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    # 1-4 = Likert scale; 9 = "not applicable" sentinel, not a scale point
    long = long[(long["resp"] >= 1) & (long["resp"] <= 4)]
    long["resp"] = long["resp"].astype(int)
    long["id"] = long["id"].astype(int)
    return long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    print("Fetching S1 Data (SAV)...")
    raw = fetch_raw()

    use_items = [f"Q4a_{i}" for i in range(1, 13)]
    opinion_items = [f"Q5a_{i}" for i in range(1, 19)]

    use = build_long(raw, use_items)
    opinion = build_long(raw, opinion_items)

    write_scale(use, "koo_2016_comm_technique_use.csv")
    write_scale(opinion, "koo_2016_comm_technique_opinion.csv")


if __name__ == "__main__":
    convert()
