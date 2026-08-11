#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0326490
# DOI: 10.1371/journal.pone.0326490
# Supporting Information: https://doi.org/10.1371/journal.pone.0326490.s001
#
# Survey of 329 Chinese SMEs on relationship networks, strategic
# orientation, knowledge transfer, and open innovation behavior. Four
# distinct instruments identified by column prefix, each on a 5-point
# Likert scale:
#   SN (SN1-1..SN2-4, 8 items)  - Relationship Network (West & Bogers)
#   SO (SO3-1..SO3-3, 3 items)  - Innovation Strategic Orientation (Huang)
#   KT (KT-1..KT-4, 4 items)    - Knowledge Transfer (Cuevas-Rodriguez et al.)
#   OI (OI1-1..OI2-4, 9 items)  - Open Innovation Behavior (Lichtenthaler)

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0326490.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = {
    "ni_2025_relationship_network": re.compile(r"^SN\d-\d$"),
    "ni_2025_strategic_orientation": re.compile(r"^SO\d-\d$"),
    "ni_2025_knowledge_transfer": re.compile(r"^KT-\d$"),
    "ni_2025_open_innovation": re.compile(r"^OI\d-\d$"),
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    df = fetch_data()
    df = df.rename(columns={"NO.": "id"})
    assert df["id"].nunique() == len(df)

    for out_name, pattern in SCALES.items():
        item_cols = [c for c in df.columns if pattern.match(str(c))]
        if not item_cols:
            print(f"  no columns matched for {out_name}")
            continue
        long = df.melt(id_vars=["id"], value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"]]

        OUT_DIR.mkdir(parents=True, exist_ok=True)
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
