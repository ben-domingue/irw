#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0170000
# DOI: 10.1371/journal.pone.0170000
# Supporting Information: https://doi.org/10.1371/journal.pone.0170000.s001
#
# HDRS-17 (Hamilton Depression Rating Scale, 17-item) raw item-level data
# used for a Rasch analysis of the depression severity continuum. Item 5
# (intermediate insomnia) has a documented single missing value coded as
# sentinel 999 (paper: "One subject had a missing value on HDRS-17 item 5
# ... and was excluded from HDRS-17 analysis") -- filtered out here.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0170000.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"HamD{i}Baixa" for i in range(1, 18)]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns={"Codigo": "id"})
    assert df["id"].nunique() == len(df)

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    # sentinel missing-value code (documented in the paper for item 5)
    long = long[long["resp"] != 999]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "alves_2017_hamd17.csv", index=False)
    print(f"alves_2017_hamd17.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
