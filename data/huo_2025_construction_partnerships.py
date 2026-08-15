#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0334555
# DOI: 10.1371/journal.pone.0334555
#
# Huo et al. 2025, "The impacts of project uncertainty and relationship
# conflict on relationship continuity in construction: The role of
# political skill." Single SI file (journal.pone.0334555_S1_File.xls, CC
# BY), N=230, no person-ID or demographic covariate columns in the source
# -- row index used as id. Four scales in the same file, item counts
# confirmed against the paper's own Measures section text (not just column
# count): u1-u8 = project uncertainty (8 items, Barki et al./Song &
# Montoya-Weiss/Sakka et al./Jun et al.), r1-r4 = relationship conflict
# (4 items), c1-c3 = relationship continuity (3 items, Celuch et al.),
# p1-p8 = political skill (8-item shortened self-reported PSI,
# Vigoda-Gadot & Meisler, adapted from Ferris et al.). All five-point
# Likert, 1 "Strongly/Completely Disagree" to 5 "Strongly/Completely
# Agree".

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0334555.s001")

SCALES = {
    "huo_2025_project_uncertainty.csv": [f"u{i}" for i in range(1, 9)],
    "huo_2025_relationship_conflict.csv": [f"r{i}" for i in range(1, 5)],
    "huo_2025_relationship_continuity.csv": [f"c{i}" for i in range(1, 4)],
    "huo_2025_political_skill.csv": [f"p{i}" for i in range(1, 9)],
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    long = df.melt(
        id_vars=["id"],
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    return long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)


def convert():
    print("Downloading journal.pone.0334555_S1_File.xls ...")
    df = fetch_data()
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for fname, item_cols in SCALES.items():
        long = build_long(df, item_cols)
        long.to_csv(OUT_DIR / fname, index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
