from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0335734
# DOI: 10.1371/journal.pone.0335734
# PORTRAIT-10: 10 items (Health, Pain, Medication, Mental health,
# Alcohol/drug use, Housing, Support, Income, Health needs, Perceived
# complexity), each scored 0-4 (Likert), administered at baseline and
# follow-up (wave 1/2). Paper confirms "Answers to questions are scored
# from 0 to 4 (Likert type)". The raw file's follow-up block is missing
# for 86/245 participants (35.1%), matching the paper's own reported
# "attrition rate of 35.1% from the initial assessment to follow-up" --
# genuine attrition, not imputation, so those rows are dropped via the
# standard dropna rather than filled.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0335734.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ITEMS = ["Health", "Pain", "Medication", "Mental health", "Alcohol/drug use",
         "Housing", "Support", "Income", "Health needs", "Perceived complexity"]


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    # Row 0 is a merged section banner ("Baseline Portrait-10" / "Follow-up
    # Portrait-10"); real column headers are row 1.
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Feuil1", header=1)
    return df.rename(columns={"record_id": "id"})


def convert():
    df = fetch()
    assert df["id"].nunique() == len(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Follow-up columns are inconsistently capitalized in the source
    # ("Alcohol/Drug use_2" vs baseline's "Alcohol/drug use") -- match
    # case-insensitively rather than assuming the same casing.
    col_lookup = {c.lower(): c for c in df.columns}

    frames = []
    for item in ITEMS:
        label = item.lower().replace("/", "_").replace(" ", "_")
        base_col = col_lookup[item.lower()]
        fu_col = col_lookup[f"{item}_2".lower()]

        b = df[["id", base_col]].rename(columns={base_col: "resp"}).copy()
        b["item"] = label
        b["wave"] = 1
        frames.append(b)

        f = df[["id", fu_col]].rename(columns={fu_col: "resp"}).copy()
        f["item"] = label
        f["wave"] = 2
        frames.append(f)

    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"]]

    out_path = OUT_DIR / "page_2025_portrait10.csv"
    long.to_csv(out_path, index=False)
    print(f"page_2025_portrait10: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
