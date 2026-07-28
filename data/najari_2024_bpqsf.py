#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0306348
# DOI: 10.1371/journal.pone.0306348
# Supporting Information: https://doi.org/10.1371/journal.pone.0306348.s001
#
# The raw file bundles the three BPQ-SF (Body Perception Questionnaire -
# Short Form, Persian) subscales: Body Awareness (q1-q46, 1-5), Autonomic
# Reactivity (s1-s21, 1-4), and Stress Symptoms (W1-W12, 1-5). Per the IRW
# standard (one scale per file), this produces three output files.
# Column "s1" has one stray Persian free-text response mixed into an
# otherwise numeric column -- coerced to NaN and dropped by the standard
# numeric-cleaning step.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0306348.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "GENDER": "cov_gender",
    "MARIGE STATUS": "cov_marriage_status",
    "EDUCATION": "cov_education",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"ID": "id", **COV_RENAME})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df["id"] = df["id"].astype(int)
    return df


def melt_scale(df: pd.DataFrame, item_cols: list[str], out_name: str):
    cov_cols = list(COV_RENAME.values())
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch_data()

    q_cols = [c for c in df.columns if c.lower().startswith("q") and c[1:].isdigit()]
    s_cols = [c for c in df.columns
              if c.lower().startswith("s") and c[1:].isdigit() and c.lower() != "sex"]
    w_cols = [c for c in df.columns if c.startswith("W") and c[1:].isdigit()]

    melt_scale(df, q_cols, "najari_2024_bpqsf_awareness.csv")
    melt_scale(df, s_cols, "najari_2024_bpqsf_autonomic.csv")
    melt_scale(df, w_cols, "najari_2024_bpqsf_stress.csv")


if __name__ == "__main__":
    convert()
