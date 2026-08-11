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
# N=201 Chinese college students, each completing 3 writing tasks of
# differing complexity (writingtask 1-3, used here as `wave`). Perceived
# task-difficulty scale: 5 items (taskdifficulty1-5), 7-point Likert scale,
# re-rated after each of the 3 tasks. Companion trait measure (critical
# thinking disposition, administered once) is shipped separately as
# zou_2025_critical_thinking.py.
OUT_NAME = "zou_2025_task_difficulty"
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0324486.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = [f"taskdifficulty{i}" for i in range(1, 6)]
COV_RENAME = {"gender": "cov_gender", "major": "cov_major"}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="data file-ZOU")

    df = df.rename(columns={"codes": "id", "writingtask": "wave"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["wave"] = pd.to_numeric(df["wave"], errors="coerce")
    df = df.dropna(subset=["id", "wave"])
    df["id"] = df["id"].astype(int)
    df["wave"] = df["wave"].astype(int)

    df = df.rename(columns=COV_RENAME)
    cov_cols = [c for c in COV_RENAME.values() if c in df.columns]

    long = df.melt(id_vars=["id", "wave"] + cov_cols, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    long = long[["id", "item", "resp", "wave"] + cov_cols]
    out_path = OUT_DIR / f"{OUT_NAME}.csv"
    long.to_csv(out_path, index=False)
    print(f"{OUT_NAME}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
