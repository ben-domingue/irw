#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0209546
# DOI: 10.1371/journal.pone.0209546
# S1 Data (SAV) -- physician motivation tool developed/assessed in Lahore,
# Pakistan. Three item blocks (5-point Likert, 1-5), each a distinct
# construct per the tool's three sections:
#   I1-I22  -- Individual/intrinsic motivation factors
#   Org1-Org36 -- Organizational/workplace factors
#   SC1-SC15 (SC3 is "CS4" in the raw file, kept as-is) -- Social/co-worker
#      and interpersonal factors
# Written as three separate scale files. Covariates: age, gender, marital
# status (A1-A3).

import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://doi.org/10.1371/journal.pone.0209546.s001"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = "/tmp/_malik_2018.sav"
    with open(tmp, "wb") as f:
        f.write(r.content)
    df, meta = pyreadstat.read_sav(tmp)
    os.remove(tmp)
    return df


def build(df, item_cols, item_prefix, out_name):
    d = df[["A1", "A2", "A3"] + item_cols].copy()
    d = d.rename(columns={"A1": "cov_age", "A2": "cov_gender",
                           "A3": "cov_marital_status"})
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)

    item_map = {c: f"{item_prefix}{i+1}" for i, c in enumerate(item_cols)}
    d = d.rename(columns=item_map)
    item_names = list(item_map.values())
    cov_names = ["cov_age", "cov_gender", "cov_marital_status"]

    long = d.melt(id_vars=["id"] + cov_names, value_vars=item_names,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    # All three scales are 1-5 Likert. Drop non-integer values (mean-imputed
    # cells found in org_5) and out-of-range sentinels (a single 14 found in
    # org_5, clearly a data-entry error against hundreds of legitimate 1-5
    # responses).
    is_whole = (long["resp"] % 1 == 0)
    in_range = long["resp"].between(1, 5)
    long = long[is_whole & in_range].reset_index(drop=True)

    out_cols = ["id", "item", "resp"] + cov_names
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

    i_cols = [f"I{i}" for i in range(1, 23)]
    build(df, i_cols, "ind_", "malik_2018_individual_motivation.csv")

    org_cols = [f"Org{i}" for i in range(1, 37)]
    build(df, org_cols, "org_", "malik_2018_organizational_motivation.csv")

    # SC3 is stored as "CS4" in the raw file (typo in source) -- keep the
    # original mapping order (SC1, SC2, CS4, SC5, SC6, ...).
    sc_cols = ["SC1", "SC2", "CS4"] + [f"SC{i}" for i in range(5, 16)]
    build(df, sc_cols, "social_", "malik_2018_social_motivation.csv")


if __name__ == "__main__":
    convert()
