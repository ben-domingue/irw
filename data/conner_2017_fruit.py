from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0171206
# DOI: 10.1371/journal.pone.0171206
# RCT (3 arms: control/EMI/FVI, kept as cov_condition since it's not a
# binary treat/control comparison) with baseline + follow-up measures of
# CES-D, HADS-Anxiety subscale, Flourishing Scale, Vitality, Curiosity and
# Exploration Inventory, and Life Orientation Test (all "r"-prefixed at
# follow-up, per datastandard.md's wave rules), plus a baseline-only Big
# Five Inventory (personality trait, not re-measured). The daily-diary
# mood items ("mood1-21"/"rmood1-21", 6 adjectives repeated across the
# 13-day intervention period) are not shipped here -- the day-by-adjective
# mapping needs more codebook time than this pass had.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0171206.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "age": "cov_age",
    "gender": "cov_gender",
    "condition": "cov_condition",
    "NZEurop": "cov_nz_european",
}

WAVE_SCALES = {
    "conner_2017_cesd": ("cesd", 20),
    "conner_2017_hads_anxiety": ("hads", 7),
    "conner_2017_flourishing": ("fs", 8),
    "conner_2017_vitality": ("vital", 4),
    "conner_2017_curiosity": ("cei", 10),
    "conner_2017_lot": ("lot", 6),
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = fetch()
    df = df.rename(columns={"ID": "id"})
    df = df.rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    assert df["id"].nunique() == len(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, (prefix, n_items) in WAVE_SCALES.items():
        pre_cols = [f"{prefix}{i}" for i in range(1, n_items + 1)]
        post_cols = [f"r{prefix}{i}" for i in range(1, n_items + 1)]

        long0 = df.melt(id_vars=["id"] + cov_cols, value_vars=pre_cols,
                        var_name="item", value_name="resp")
        long0["item"] = "item" + long0["item"].str.replace(prefix, "", regex=False)
        long0["wave"] = 0
        long1 = df.melt(id_vars=["id"] + cov_cols, value_vars=post_cols,
                        var_name="item", value_name="resp")
        long1["item"] = "item" + long1["item"].str.replace(f"r{prefix}", "", regex=False)
        long1["wave"] = 1
        long = pd.concat([long0, long1], ignore_index=True)
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        # vitality is a genuine continuous 0-100 VAS; the other scales are
        # integer Likert -- a handful of isolated non-integer cells turned
        # up (1-2 per table, no imputation language in the paper) and are
        # dropped as data-entry errors rather than kept.
        if prefix != "vital":
            long = long[long["resp"] == long["resp"].round()]
        long = long[["id", "item", "resp", "wave"] + cov_cols]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

    bfi_cols = [f"bfi{i}" for i in range(1, 45)]
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=bfi_cols,
                   var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[long["resp"] == long["resp"].round()]
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / "conner_2017_bfi.csv"
    long.to_csv(out_path, index=False)
    print(f"conner_2017_bfi: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
