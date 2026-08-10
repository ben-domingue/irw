from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0352176
# DOI: 10.1371/journal.pone.0352176
# Monier, Droit-Volet, Dambrun, Monceau, Delaby, Rieu et al. (2026),
# "Parkinson's disease and awareness of the passage of time: Perceived
# health, emotion, and self-transcendence". S1 Table (.s001, XLSX, only SI
# file on the article). CC BY 4.0.
# The raw sheet has a banner row above the real header row -- read with
# header=1. 10-item French Self-Transcendence Inventory (STI1-STI10),
# 7-point scale. "ID" resets within each of the two diagnostic groups
# (Parkinson's N=68, Control N=58), so it is not unique on its own --
# combined with Group into a composite id. One isolated out-of-range value
# (STI1=8 on an otherwise 1-7 scale, single occurrence) dropped as a data
# entry error. See also monier_2026_pot.py for the second scale
# (Passage-of-Time judgment items) in this same file.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0352176.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"STI{i}_" for i in range(1, 11)]  # prefix match, French labels vary


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Feuil1", header=1)

    item_cols = [c for c in df.columns if any(c.startswith(p) for p in ITEM_COLS)]
    assert len(item_cols) == 10, item_cols

    df = df.rename(columns={
        "Group_1Parkison2_Control": "cov_group",
        "Age": "cov_age",
    })
    # Trailing blank rows in the sheet have no group assignment (and no data) --
    # drop before building the id.
    df = df.dropna(subset=["cov_group"]).reset_index(drop=True)
    df["cov_group"] = df["cov_group"].map({1.0: "parkinson", 2.0: "control"})
    df["id"] = df["cov_group"] + "_" + df["ID"].astype(int).astype(str)
    assert df["id"].nunique() == len(df)

    cov_names = ["cov_group", "cov_age"]
    long = df.melt(id_vars=["id"] + cov_names, value_vars=item_cols,
                    var_name="item", value_name="resp")
    # Standardize item labels to STI1..STI10 (source headers carry French text).
    long["item"] = long["item"].str.extract(r"(STI\d+)")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_names]
    long.to_csv(OUT_DIR / "monier_2026_sti.csv", index=False)
    print(f"rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
