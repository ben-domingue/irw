#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/OLOMAI
# DOI: 10.7910/DVN/OLOMAI
# License: CC0 1.0
#
# "The Trait-State-Experience Pathway: State Affect Links Temperament to
# Daily Emotional Experience" (Nabizadehchianeh, 2026, Harvard Dataverse).
# Raw file (ALL_data.csv.tab) bundles the 39-item TEMPS-A (Temperament
# Evaluation of Memphis, Pisa, Paris and San Diego Autoquestionnaire, short
# form) binary (0/1) items -- S1-S39 -- alongside derived TEMPS-A subscale
# totals (cyclothymic/depressive/irritable/hyperthymic/anxious,
# TEMPSA.Total), Positive/Negative-affect composite scores, and SAM
# (Self-Assessment Manikin) pleasure/arousal/dominance ratings. Only the
# raw S1-S39 binary items are shipped here -- the rest are derived
# composites or a different instrument (SAM), out of scope for this table
# per datastandard.md's one-instrument-per-file rule. 3 duplicate IDs (out
# of 716 rows for 713 unique participants) dropped -- this is what
# triggered the original triage "dup_id_item" QC failure.

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

FILE_URL = "https://dataverse.harvard.edu/api/access/datafile/13686506"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEMS = [f"S{i}" for i in range(1, 40)]
COV_MAP = {"ID": "id", "Sex": "cov_sex", "Age": "cov_age"}


def convert():
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(pd.io.common.BytesIO(r.content), sep="\t")
    df = df.rename(columns=COV_MAP)

    # Drop the 3 duplicate-ID rows (keep first occurrence) -- these are
    # what caused the original triage dup_id_item QC failure.
    df = df.drop_duplicates(subset=["id"], keep="first")
    assert df["id"].nunique() == len(df), "id still not unique after dedup"

    cov_cols = ["cov_sex", "cov_age"]
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= 0) & (long["resp"] <= 1)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "nabizadehchianeh_2026_tempsa"
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

    try:
        import pyreadr
        pyreadr.write_rdata(str(out_path).replace(".csv", ".RData"), long, df_name="d")
    except Exception as e:
        print(f"WARNING: could not write RData for {out_name}: {e}")


if __name__ == "__main__":
    convert()
