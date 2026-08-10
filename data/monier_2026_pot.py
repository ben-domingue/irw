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
# health, emotion, and self-transcendence". S1 Table (.s001, XLSX). CC BY
# 4.0. 7-item Passage-of-Time judgment battery (subjective speed of time
# passing rated for present/week/month/year/5-years-ago/now-vs-before/
# aging), 7-point scale, column suffix "_7vite" ("vite" = fast in French).
# "ID" resets within each of the two diagnostic groups (Parkinson's N=68,
# Control N=58) -- combined with Group into a composite id, same as
# monier_2026_sti.py (the other scale in this file).
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0352176.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["PoTpresent_7vite", "PoTweek_7vite", "PoTmonth_7vite", "PoTyear_7vite",
             "PoT5yearago_7vite", "PoT_NowBefore_7vite", "PoTaging_7vite"]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Feuil1", header=1)

    missing = [c for c in ITEM_COLS if c not in df.columns]
    assert not missing, f"missing expected item columns: {missing}"

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
    long = df.melt(id_vars=["id"] + cov_names, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_names]
    long.to_csv(OUT_DIR / "monier_2026_pot.csv", index=False)
    print(f"rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
