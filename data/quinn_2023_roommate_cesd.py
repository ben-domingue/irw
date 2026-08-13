#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0286709
# DOI: 10.1371/journal.pone.0286709
#
# "Understanding the role of depressive symptoms in academic outcomes: A
# longitudinal study of college roommates". S1 Data (.s006, SPSS .sav) is the
# raw actor/partner dyadic dataset for 245 same-sex freshman roommate dyads
# (490 individuals). This script keeps only each individual's own ("_A" =
# actor) self-reported CES-D (20 items, 0-3 scale) responses at three survey
# waves (source labels CESD1/CESD3/CESD4 -> wave 1/2/3); partner-report
# ("_P") columns are the roommate's proxy report of the *other* person and
# are dropped to avoid double counting/ambiguous focal-unit assignment.
# `id` = Dyad_ID*10 + Indiv_ID (unique per individual, verified). No PII
# (no names; GPA/test scores are academic performance covariates, not
# identifying). CC BY 4.0.

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0286709.s006")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

WAVE_MAP = {"CESD1": 1, "CESD3": 2, "CESD4": 3}


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    tmp = os.path.join(OUT_DIR, "_tmp_quinn_2023.sav")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(tmp, "wb") as f:
        f.write(r.content)

    import pyreadstat
    df, meta = pyreadstat.read_sav(tmp)
    os.remove(tmp)

    df["id"] = (df["Dyad_ID"] * 10 + df["Indiv_ID"]).astype(int)
    assert df["id"].nunique() == len(df), "id column is not unique per row"

    long_frames = []
    for src_prefix, wave in WAVE_MAP.items():
        item_cols = [f"{src_prefix}_{i}_A" for i in range(1, 21)]
        item_cols = [c for c in item_cols if c in df.columns]
        sub = df[["id"] + item_cols].copy()
        long = sub.melt(id_vars=["id"], value_vars=item_cols,
                         var_name="item", value_name="resp")
        # rename item to a wave-agnostic CESD_1..CESD_20 label
        long["item"] = long["item"].str.replace(
            rf"^{src_prefix}_(\d+)_A$", r"CESD_\1", regex=True)
        long["wave"] = wave
        long_frames.append(long)

    long = pd.concat(long_frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # CES-D items are scored 0-3
    long = long[(long["resp"] >= 0) & (long["resp"] <= 3)]

    out_cols = ["id", "item", "resp", "wave"]
    long = long[out_cols]

    out_path = os.path.join(OUT_DIR, "quinn_2023_roommate_cesd.csv")
    long.to_csv(out_path, index=False)
    print(f"quinn_2023_roommate_cesd: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
