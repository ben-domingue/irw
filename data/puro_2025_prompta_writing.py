from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0337342
# DOI: 10.1371/journal.pone.0337342
# Puro et al. (2025), "PROMPTa - A multifaceted assessment approach to
# develop writing skills". S1 Data. CC BY 4.0. N=46 students.
# The raw file has two side-by-side column blocks for the same 46
# students (matching row order/"Student name" index); only the first,
# simpler block is shipped -- Pre Test, 3 timed-writing-task scores each
# across 3 rounds (T1D1-T3D3), and Post Test (11 items total). The second
# block (P/M/E-suffixed columns, consistently higher values) appears to
# be a different rubric/decomposition of the same tasks, but its exact
# meaning isn't documented in the file and isn't shipped.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0337342.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEM_COLS = ["Pre Test", "T1D1", "T1D2", "T1D3", "T2D1", "T2D2", "T2D3",
             "T3D1", "T3D2", "T3D3", "Post Test"]


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), header=1)


def convert():
    df = fetch().rename(columns={"Student name": "id"})
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    long = df.melt(id_vars=["id"], value_vars=ITEM_COLS, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]
    out_path = OUT_DIR / "puro_2025_prompta_writing.csv"
    long.to_csv(out_path, index=False)
    print(f"puro_2025_prompta_writing: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
