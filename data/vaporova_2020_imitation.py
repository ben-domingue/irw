#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0235595
# S1 Data: https://doi.org/10.1371/journal.pone.0235595.s001
# DOI: 10.1371/journal.pone.0235595
#
# Vaporova & Zmyj (2020), "Social evaluation and imitation of prosocial and
# antisocial agents in infants, children, and adults", PLOS ONE.
#
# The S1 Data file ("prosociality_data" sheet) is a stacked two-block sheet:
# an "Infants and Children:" block (rows 4-98, 0-indexed) followed by an
# "Adults:" block (rows 101-127) that uses an entirely different, non-
# overlapping set of columns (no imitation task was administered to adults).
# The imitation scale (3 binary items: pulling the mitten off, shaking the
# mitten, putting the mitten back on) only exists in the Infants/Children
# block, which is itself a completely regular single-header table once
# sliced out -- no further reconstruction needed.

import io
import os
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SRC_URL = ("https://journals.plos.org/plosone/article/file?"
           "type=supplementary&id=10.1371/journal.pone.0235595.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def convert():
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content), sheet_name="prosociality_data", header=None)

    # Infants/Children block: header at row 3, data rows 4-98 (0-indexed)
    block = raw.iloc[4:99].reset_index(drop=True)
    block.columns = range(block.shape[1])

    # Positional column map (see header row 3 in the raw sheet):
    # 0 id | 3 Analyzability imitation (0=exclude,1=analyzable)
    # 13 Imitation_pulling mitten off | 14 Imitation_shaking the mitten
    # 15 Imitation_putting mitten back on | 16 Imitation_sum score (aggregate, exclude)
    df = block[[0, 3, 13, 14, 15]].copy()
    df.columns = ["id", "analyzable_imitation", "item_pulling_off",
                  "item_shaking", "item_putting_back_on"]

    # Keep only children flagged analyzable for the imitation task -- this
    # also cleanly removes the sentinel 99 codes used for excluded rows.
    df = df[df["analyzable_imitation"] == 1].drop(columns=["analyzable_imitation"])

    df["id"] = df["id"].astype(str)
    assert df["id"].nunique() == len(df), "id not unique"

    item_cols = ["item_pulling_off", "item_shaking", "item_putting_back_on"]
    long = df.melt(id_vars=["id"], value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp"]
    long = long[out_cols]

    out_name = "vaporova_2020_imitation"
    csv_path = os.path.join(OUT_DIR, out_name + ".csv")
    long.to_csv(csv_path, index=False)
    try:
        import pyreadr
        pyreadr.write_rdata(os.path.join(OUT_DIR, out_name + ".RData"),
                             long, df_name="d")
    except ImportError:
        long.to_pickle(os.path.join(OUT_DIR, out_name + ".rdata_fallback.pkl"))

    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
