#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0241335
# DOI: 10.1371/journal.pone.0241335
# Supporting Information: https://doi.org/10.1371/journal.pone.0241335.s012
#
# Medical students in Cyprus, N=182. Three raw-item scales in Greek:
#   MBI  -- Maslach Burnout Inventory (15 items), standard 7-point
#           frequency scale exported as Greek text, mapped Never=0 ..
#           Every day=6.
#   WHO5 -- WHO-5 Well-Being Index (5 items, MH_1..MH_5), already numeric
#           0/20/40/60/80/100.
#   PSQI_disturbance -- Pittsburgh Sleep Quality Index component-5
#           sub-items (Q5a-j, 10 items), 4-point frequency scale exported
#           as Greek text, mapped Not during past month=0 .. 3+ times a
#           week=3.
# Confirmed both Greek category sets are identical across every item in
# their respective scale before building the map (not assumed from one
# column). PSQI_total/MBI_EE/DP/PA and all *_category/*_cat columns are
# aggregates, excluded. Q1-Q4 (bedtime/wake time/minutes/hours, mixed
# time-of-day and duration formats) and Q6-Q9 (single differently-worded
# PSQI components) and the unlabeled c1-c7 block were left out -- no
# uniform item battery, and c1-c7's construct isn't identified anywhere
# in the source metadata or paper.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0241335.s012")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Gender": "cov_sex", "Age_range": "cov_age_range",
              "Marital": "cov_marital_status", "Study_year": "cov_study_year"}

MAP_MBI = {
    "Ποτέ": 0,
    "Λίγες Φορές το Χρόνο": 1,
    "Μία Φορά τον Μήνα ή Κάπως Λιγότερο": 2,
    "Δύο ή Τρεις Φορές τον Μήνα": 3,
    "Μία φορά την Εβδομάδα": 4,
    "Αρκετές Φορές την Εβδομάδα": 5,
    "Κάθε Ημέρα": 6,
}
MAP_PSQI = {
    "Όχι κατά τις τελευταίες 30 ημέρες": 0,
    "Λιγότερο από 1 φορά την εβδομάδα": 1,
    "Μία ή δύο φορές την εβδομάδα": 2,
    "3 ή περισσότερες φορές την εβδομάδα": 3,
}

MBI_COLS = [c for c in
            [f"MBI_{i}_EE" for i in range(1, 6)]
            + [f"MBI_{i}_DP" for i in range(6, 10)]
            + [f"MBI_{i}_PA" for i in range(10, 16)]]
WHO5_COLS = ["MH_1", "MH_2", "MH_3_r", "MH_4", "MH_5_r"]
PSQI_COLS = [f"Q5{c}" for c in "abcdefghij"]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns={"ID": "id", **COV_RENAME})


def melt_mapped(df, cov_cols, item_cols, value_map, out_name):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(value_map)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    save(long, cov_cols, out_name)


def melt_numeric(df, cov_cols, item_cols, out_name):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    save(long, cov_cols, out_name)


def save(long, cov_cols, out_name):
    long = long[["id", "item", "resp"] + cov_cols]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_mapped(df, cov_cols, MBI_COLS, MAP_MBI, "nteveros_2021_mbi")
    melt_numeric(df, cov_cols, WHO5_COLS, "nteveros_2021_who5")
    melt_mapped(df, cov_cols, PSQI_COLS, MAP_PSQI, "nteveros_2021_psqi_disturbance")


if __name__ == "__main__":
    convert()
