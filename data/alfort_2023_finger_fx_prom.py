#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0288506
# DOI: 10.1371/journal.pone.0288506
#
# "Finger fractures: Epidemiology and treatment based on 21341 fractures
# from the Swedish Fracture register" (Alfort et al., 2023)
#
# S1 File (SAV), N=21341 fracture cases. Alongside injury/treatment
# registry fields, the file contains raw per-item Patient-Reported Outcome
# Measure (PROM) responses collected at baseline (PRO0) and follow-up
# (PRO1): 45 items across three item blocks (`Diffic*` = difficulty
# performing an activity, `Often*` = how often a symptom occurs,
# `Bother*` = how much a problem bothers the patient), each raw-scored
# 1-5, consistent with a single validated hand/arm PROM instrument (not
# named explicitly in the paper's Data Availability text, but structurally
# a DASH-family instrument). Only a subset of the 21341 registered
# fractures completed the PROM (~5300 at baseline), but that subset is far
# above the N>=100 floor. `*Index` columns (DailyActIndex, EmotionalIndex,
# ArmHandFuncIndex, MobilityIndex, FunctionIndex, BotherIndex) are
# composite subscale scores and are excluded from resp, as are the EQ-5D
# items (a separate, distinct instrument -- would need its own file, but
# EQ-5D dimensions here are single-item 1-3/1-5 severity ratings without
# enough item count to be useful alone, so left unshipped this batch).
# PRO0/PRO1 are stacked as wave=0/1. No PII: reviewed all 211 raw columns
# -- no names, emails, or dates of birth; the only dates present are
# clinical event dates (ER visit, registration, treatment), and
# Trt_MainSurgeon{1-4} are hospital-internal surgeon codes, not patient
# identifiers.

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATA_URL = "https://doi.org/10.1371/journal.pone.0288506.s002"

BLOCKS = ["Diffic", "Often", "Bother"]

COV_MAP = {
    "Inj_Age": "cov_age",
    "Inj_Sex": "cov_sex",
    "finger": "cov_finger",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(DATA_URL, headers=UA, timeout=120)
    r.raise_for_status()
    from io import BytesIO
    return pd.read_spss(BytesIO(r.content))


def item_cols_for(df: pd.DataFrame, prefix: str) -> list[str]:
    cols = [c for c in df.columns if c.startswith(prefix)]
    # exclude the composite *Index columns
    return [c for c in cols if not c.endswith("Index")]


def convert():
    print("Downloading S1 File …")
    df = fetch_data()
    df = df.rename(columns={"ID": "id"})
    df = df.rename(columns=COV_MAP)
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id not unique"

    cov_cols = list(COV_MAP.values())
    frames = []
    for wave, wprefix in [(0, "PRO0_"), (1, "PRO1_")]:
        item_cols = []
        for block in BLOCKS:
            item_cols += item_cols_for(df, f"{wprefix}{block}")
        sub = df[["id"] + cov_cols + item_cols].copy()
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["item"] = long["item"].str.replace(wprefix, "", regex=False)
        long["wave"] = wave
        frames.append(long)

    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp", "wave"] + cov_cols
    long = long[out_cols].sort_values(["id", "wave", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "alfort_2023_finger_fx_prom.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
