#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0249943
# DOI: 10.1371/journal.pone.0249943
# Jelinek et al. (2021), "Measuring depression in adolescence: Evaluation of
# a hierarchical factor model of the Children's Depression Inventory and
# measurement invariance across boys and girls", PLOS ONE. CC BY 4.0.
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0249943.s001

from __future__ import annotations

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0249943.s001"

# 27 raw CDI items; "R" suffix marks the item's own reverse-worded phrasing
# in this instrument, not a duplicate of a same-numbered non-R column.
ITEM_COLS = ["cdi1", "cdi2R", "cdi3", "cdi4", "cdi5R", "cdi6", "cdi7R", "cdi8R",
             "cdi9", "cdi10R", "cdi11R", "cdi12", "cdi13R", "cdi14", "cdi15R",
             "cdi16R", "cdi17", "cdi18R", "cdi19", "cdi20", "cdi21R", "cdi22",
             "cdi23", "cdi24R", "cdi25R", "cdi26", "cdi27"]
COV_RENAME = {
    "sub_sample": "cov_sub_sample",
    "sex_male": "cov_sex_male",
    "age": "cov_age",
    "family_complete": "cov_family_complete",
}
COV_COLS = list(COV_RENAME.values())


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"ID": "id", **COV_RENAME})

    long = df.melt(id_vars=["id"] + COV_COLS, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + COV_COLS]

    path = os.path.join(OUT_DIR, "jelinek_2021_cdi.csv")
    long.to_csv(path, index=False)
    print(f"jelinek_2021_cdi: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
