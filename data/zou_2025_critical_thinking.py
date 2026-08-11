from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0324486
# DOI: 10.1371/journal.pone.0324486
# Zou, Kuek, Cheng & Feng (2025), "How does task complexity and task
# difficulty affect college students' writing performance? Critical
# thinking disposition ...". S1 Data (sheet "data file-ZOU"). CC BY 4.0.
# N=201 Chinese college students. Critical thinking disposition inventory:
# 70 items (D11-D710, 7 dimensions x 10 items each), 7-point Likert scale.
# This trait measure was administered once (at writingtask==1 / baseline)
# -- the raw file repeats each student's row 3x (once per writing task
# condition) but only fills the D-columns on the first row, leaving them
# NaN on the other two; this script keeps only the non-null baseline rows.
# The companion 5-item task-difficulty perception scale (which does vary
# by task) is shipped separately as zou_2025_task_difficulty.py.
OUT_NAME = "zou_2025_critical_thinking"
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0324486.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"gender": "cov_gender", "major": "cov_major"}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="data file-ZOU")

    df = df.rename(columns={"codes": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"])
    df["id"] = df["id"].astype(int)

    # D-columns are named D11..D710 (dimension digit + item digit(s))
    item_cols = [c for c in df.columns if c.startswith("D") and len(c) >= 3
                 and c[1].isdigit()]

    df = df.rename(columns=COV_RENAME)
    cov_cols = [c for c in COV_RENAME.values() if c in df.columns]

    # Trait measure administered once per student -- keep only rows where
    # the disposition items are populated (baseline / writingtask==1).
    df = df.dropna(subset=item_cols, how="all")

    # Verify one row per student after filtering.
    assert df["id"].nunique() == len(df), "expected exactly one baseline row per student"

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / f"{OUT_NAME}.csv"
    long.to_csv(out_path, index=False)
    print(f"{OUT_NAME}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
