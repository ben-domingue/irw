#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0228450
# DOI: 10.1371/journal.pone.0228450
# SI: S1 File (10.1371/journal.pone.0228450.s001), SPSS .sav
#
# Professional Decision-Making in Medicine (PDM) measure: 16 binary
# (correct/incorrect) items, administered pre and post (wave). The
# pdm.o/c/h/q/e.pre|pst columns are subscale aggregates and pspq.fs.*
# columns are already-averaged factor scores (fractional, non-integer) -
# both excluded as composites, not raw items.

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0228450.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

RESP_MAP = {"correct": 1, "incorrect": 0}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))

    df = df.rename(columns={"partID": "id", "sample": "cov_sample",
                             "is.female": "cov_is_female"})
    assert df["id"].nunique() == len(df)

    pre_items = [f"pdm.pre.item{i}" for i in range(1, 17)]
    pst_items = [f"pdm.pst.item{i}" for i in range(1, 17)]

    frames = []
    for wave, items in [(1, pre_items), (2, pst_items)]:
        sub = df[["id", "cov_sample", "cov_is_female"] + items].copy()
        rename = {c: f"item_{i+1}" for i, c in enumerate(items)}
        sub = sub.rename(columns=rename)
        long = sub.melt(id_vars=["id", "cov_sample", "cov_is_female"],
                         value_vars=list(rename.values()),
                         var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(str).str.strip().str.lower().map(RESP_MAP)
        long["wave"] = wave
        frames.append(long)

    long = pd.concat(frames, ignore_index=True)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long["cov_is_female"] = pd.to_numeric(long["cov_is_female"], errors="coerce")

    out_cols = ["id", "item", "resp", "wave", "cov_sample", "cov_is_female"]
    long = long[out_cols].sort_values(["id", "wave", "item"]).reset_index(drop=True)

    os.makedirs(OUT_DIR, exist_ok=True)
    fname = "antes_2020_pdm.csv"
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
