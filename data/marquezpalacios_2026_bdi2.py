#!/usr/bin/env python3
# Source: https://osf.io/6dutb/
# License: CC BY 4.0 (OSF node license id 563c1cf88c5e4a3877f9e96a resolved
# via GET https://api.osf.io/v2/licenses/563c1cf88c5e4a3877f9e96a/ ->
# "CC-By Attribution 4.0 International")
#
# "Psychometric Properties of the BDI-II in Mexican University Students"
# (Marquez-Palacios et al., 2026, OSF). The data file (BDI.dat) triaged as
# no_usable_file because its .dat extension isn't in the pipeline's
# recognized tabular-format list -- a genuine data file was hiding behind
# an unrecognized extension. Confirmed via the project's own CODEBOOK.txt:
# tab-separated, no header row, 21 columns = the 21 BDI-II items, each
# 0-3 ordinal (0=symptom absent ... 3=symptom severe). No id column in the
# source file -- used row index as id (N=508, one row per respondent, no
# apparent duplication).

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

FILE_URL = "https://osf.io/download/6a1c674ba968ef7935aad5fc/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEMS = [f"BDI{i}" for i in range(1, 22)]


def convert():
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(pd.io.common.BytesIO(r.content), sep="\t", header=None,
                      names=ITEMS)
    df.insert(0, "id", range(1, len(df) + 1))

    long = df.melt(id_vars=["id"], value_vars=ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 0) & (long["resp"] <= 3)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "marquezpalacios_2026_bdi2"
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
