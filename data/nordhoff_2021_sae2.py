#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0260953
# DOI: 10.1371/journal.pone.0260953
# Supporting Information: https://doi.org/10.1371/journal.pone.0260953.s001
#
# Online survey on perceived safety and trust in SAE Level 2 partially
# automated cars. Three named Likert (1-5) instruments extracted by column
# prefix: TRUST (12 items), MOTIVE (4 items), SAFETY (6 items). Sentinel
# code 99 ("I prefer not to respond" / "Not applicable to me", per the
# paper's methods) is filtered out. No person-identifier column exists in
# the shared file, so row index is used as id.

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0260953.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "nordhoff_2021_trust": re.compile(r"^TRUST\d+_"),
    "nordhoff_2021_motive": re.compile(r"^MOTIVE\d+_"),
    "nordhoff_2021_safety": re.compile(r"^SAFETY\d+_"),
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    return df


def convert():
    df = fetch_data()

    for out_name, pattern in SCALES.items():
        item_cols = [c for c in df.columns if pattern.match(str(c))]
        if not item_cols:
            print(f"  no columns matched for {out_name}")
            continue
        long = df.melt(id_vars=["id"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long[long["resp"] != 99]  # sentinel: prefer not to respond / N/A
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"]]

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
