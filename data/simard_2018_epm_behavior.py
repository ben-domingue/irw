#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0204980
# S1 File: https://doi.org/10.1371/journal.pone.0204980.s001
# DOI: 10.1371/journal.pone.0204980
#
# "Fibroblast growth factor 2 is necessary for the antidepressant effects of
# fluoxetine" (mouse study). The S1 File's Elevated Plus Maze (EPM) sheet
# is one of three behavioral tests run on the same 67 mice (FST, EPM, OF);
# only EPM is shipped as a scale here -- FST and OF were dropped (see
# BATCH_LOG.md's "simard_2018 split" note): their "Time Immobile"/"Time
# Centre" duration items are genuine ordinal behavioral scores, but their
# companion "Latency to Immobility"/"Latency Centre" items are literally
# time-to-first-occurrence of a behavior, i.e. response-time-like measures
# not accuracy/substantive responses in their own right, per
# feedback_rt_column_scope -- removing them leaves each of FST/OF with
# only 1 item, below IRW's 2-item minimum. EPM's 3 items (time in open
# arms, % of distance traveled in open arms, total distance traveled) have
# no latency/response-time component, so the full EPM scale ships intact.
# Treatment (Vehicle vs Fluoxetine) is a genuine experimental manipulation
# -> `treat`. Group (Control vs Stress, the chronic-stress manipulation)
# and Genotype (WT vs FGF2 knockout) are carried as covariates.

import os
import io
import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0204980.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_RENAME = {
    "Time Open Arms (s)": "epm_time_open_arms_s",
    "(Open Distance/Total Distance)*100": "epm_open_distance_pct",
    "Total Distance (m)": "epm_total_distance_m",
}


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    xl = pd.ExcelFile(io.BytesIO(r.content))
    epm = xl.parse("EPM").dropna(subset=["Animal"])

    keys = ["Animal", "Genotype", "Group", "Treatment"]
    df = epm[keys + list(ITEM_RENAME.keys())].copy()
    df = df.rename(columns=ITEM_RENAME)
    df = df.rename(columns={"Animal": "id"})
    assert df["id"].nunique() == len(df), "animal id not unique"

    df["treat"] = (df["Treatment"] == "Fluoxetine").astype(int)
    df["cov_group"] = df["Group"]
    df["cov_genotype"] = df["Genotype"]
    df = df.drop(columns=["Genotype", "Group", "Treatment"])

    item_cols = list(ITEM_RENAME.values())
    cov_cols = ["cov_group", "cov_genotype"]

    long = df.melt(id_vars=["id", "treat"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp", "treat"] + cov_cols
    long = long[out_cols]

    out_name = "simard_2018_epm_behavior"
    out_path = os.path.join(OUT_DIR, out_name + ".csv")
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.2f}-{long['resp'].max():.2f}")


if __name__ == "__main__":
    convert()
