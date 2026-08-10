#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0267032
# DOI: 10.1371/journal.pone.0267032
#
# d'Ussel et al. (2022) "Factors associated with psychological symptoms in
# hospital workers of a French hospital during the COVID-19 pandemic:
# Lessons from the first wave." PLOS ONE. License: CC BY 4.0.
#
# S1 Dataset (XLSX, N=819) has raw item-level responses for two clinical
# scales, one file per scale (datastandard.md "one scale per file"):
#   - PTSD Checklist (PCL-17): PCL_* (17 items, 1-5 scale)
#   - Hospital Anxiety and Depression Scale (HADS-14): HAD_* (14 items,
#     0-3 scale; includes both anxiety and depression subscales)
# result_pcl/result_anxiety/result_depression are precomputed
# classification/composite columns and are excluded.

import os

import pandas as pd
import requests
import io

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0267032.s003"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "gender": "cov_gender",
    "age": "cov_age",
    "profession": "cov_profession",
    "work location": "cov_work_location",
}

PCL_COLS = ["PCL_memories", "PCL_dreams", "PCL_repetition", "PCL_upset", "PCL_physical_reaction",
            "PCL_avoid_talking", "PCL_avoid_situation", "PCL_difficulty_memory", "PCL_loss_interest",
            "PCL_distant", "PCL_emotionally_numb ", "PCL_future", "PCL_sleep", "PCL_irritability",
            "PCL_concentration", "PCL_defensive", "PCL_watchful"]

HAD_COLS = ["HAD_jumpy", "HAD_fear", "HAD_worry", "HAD_decontract", "HAD_anxiety", "HAD_restless",
            "HAD_panic", "HAD_enjoy", "HAD_laugh", "HAD_enjoy.1", "HAD_slow", "HAD_appearence",
            "HAD_look_forward", "HAD_distraction"]

SCALES = {
    "dussel_2022_pcl17": (PCL_COLS, 1, 5),
    "dussel_2022_hads14": (HAD_COLS, 0, 3),
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    print("Fetching S1 Dataset (XLSX)...")
    raw = fetch_raw()
    df = raw.rename(columns={"ID": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).copy()
    df["id"] = df["id"].astype(int)
    if not df["id"].is_unique:
        df = df.reset_index(drop=True)
        df["id"] = df.index + 1

    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    os.makedirs(OUT_DIR, exist_ok=True)
    for out_name, (item_cols, lo, hi) in SCALES.items():
        sub = df[["id"] + cov_cols + item_cols].copy()
        sub = sub.rename(columns=lambda c: c.strip() if c in item_cols else c)
        item_cols_clean = [c.strip() for c in item_cols]
        sub.columns = ["id"] + cov_cols + item_cols_clean
        for c in item_cols_clean:
            sub[c] = pd.to_numeric(sub[c], errors="coerce")
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols_clean,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)].reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols].sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"{out_name}.csv"
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
