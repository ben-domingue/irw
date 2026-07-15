from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("Intergenerational Transmission of Social Anxiety: The Role of "
         "Parents' Fear of Negative Child Evaluation and Their "
         "Self-Referent and Child-Referent Interpretation Biases "
         "(Dülger, Van Bockstaele, Majdandžić & de Vente, 2024, "
         "Cognitive Therapy and Research) -- word-fragment completion task")
URL  = "https://osf.io/384h5/"
DOI  = "10.1007/s10608-024-10490-0"
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://osf.io/download/9qrd5/"

# word_completion_coded.sav is already trial-level long format (one row per
# subject x word fragment), unlike most sources this pipeline processes --
# no melt needed, just column selection/renaming.


def convert():
    print("Downloading word_completion_coded.sav ...")
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(pd.io.common.BytesIO(r.content))

    long = df.rename(columns={
        "subject": "id",
        "WordFragment": "item",
        "Completion_correct": "resp",
    })
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "dulger2024_wordcompletion.csv"
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


if __name__ == "__main__":
    convert()
