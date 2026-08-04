#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0308623
# DOI: 10.1371/journal.pone.0308623
# "Cross-cultural adaptation and reliability of the European Portuguese version
#  of the Musculoskeletal Health Questionnaire: A methodological study"
#  (Ribeiro et al. 2024, PLOS ONE)
#
# S3 Appendix (journal.pone.0308623_S3_Appendix.xlsx) contains baseline (T0)
# item-level responses to the 14-item Portuguese MSK-HQ (0-4 scale, "MSK-HQ_Item 1"
# .. "MSK-HQ_Item 14"). "MSK-HQ-PT (T0)"/"MSK-HQ-PT (T1)" are pre-computed total
# scores (excluded); T1 item-level responses were not collected/shared, only the
# T1 total. No person id column exists in the source file -- row index is used.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0308623.s003"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"MSK-HQ_Item {i}" for i in range(1, 15)]

COV_RENAME = {
    "Age": "cov_age",
    "Gender": "cov_gender",
    "BMI": "cov_bmi",
    "Duration of symptoms": "cov_symptom_duration",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="Folha1")


def convert() -> None:
    print("Downloading journal.pone.0308623_S3_Appendix.xlsx …")
    raw = fetch_data()

    raw = raw.reset_index(drop=True)
    raw.insert(0, "id", raw.index + 1)
    raw = raw.rename(columns=COV_RENAME)

    cov_cols = list(COV_RENAME.values())
    item_names = [f"msk{i}" for i in range(1, 15)]
    sub = raw[["id"] + cov_cols + ITEM_COLS].copy()
    sub = sub.rename(columns=dict(zip(ITEM_COLS, item_names)))

    long = sub.melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_names,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "ribeiro_2024_msk_hq.csv"
    long.to_csv(OUT_DIR / fname, index=False)
    print(
        f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
        f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
    )


if __name__ == "__main__":
    convert()
