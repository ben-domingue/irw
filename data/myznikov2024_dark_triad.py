from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "https://osf.io/h6gqf/"
TITLE = ("Properties of resting state functional connectivity associated with "
         "integrated combined subscales of Dark Triad")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# Dirty Dozen Dark Triad (DDDT): 4 items per subscale (1-5), stored as sum scores (4-20)
ITEMS = {
    "narcissism":       "DDDT - Narcissism",
    "psychopathy":      "DDDT - Psychopathy",
    "machiavellianism": "DDDT - Machiavellianism ",
}

COV_MAP = {
    "Sex (-1 - М, 1 - F)": "cov_sex",
    "Age (years)":          "cov_age",
}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    url = "https://osf.io/download/hmy8u/"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), sheet_name="Лист1")


def convert():
    raw = fetch_data()
    raw = raw.rename(columns=COV_MAP)
    raw = raw.rename(columns={"Subject ID": "id"})
    cov_cols = list(COV_MAP.values())

    long_rows = []
    for item_name, col in ITEMS.items():
        sub = raw[["id"] + cov_cols + [col]].copy()
        sub = sub.rename(columns={col: "resp"})
        sub["item"] = item_name
        long_rows.append(sub)

    long = pd.concat(long_rows, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "myznikov2024_dark_triad.csv"
    long.to_csv(OUT_DIR / fname, index=False)

    existing = _load_index()
    row = {
        "file":           fname,
        "doi":            DOI,
        "title":          TITLE,
        "scale":          "dark_triad",
        "n_participants": long["id"].nunique(),
        "n_items":        long["item"].nunique(),
        "n_responses":    len(long),
        "resp_range":     f"{int(long['resp'].min())}-{int(long['resp'].max())}",
        "license":        "cc0",
        "notes":          "DDDT subscale sum scores (4-20); narcissism/psychopathy/machiavellianism; "
                          "N=129 healthy Russian participants; resting-state fMRI study; "
                          "resp direction unverified",
        "status":         "cleaned",
    }
    existing = [r for r in existing if r.get("file") != fname]
    existing.append(row)
    _write_index(existing)

    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())}")


def _load_index():
    if not INDEX_FILE.exists():
        return []
    with open(INDEX_FILE, newline="") as f:
        return list(csv.DictReader(f))


def _write_index(rows):
    with open(INDEX_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=INDEX_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    convert()
