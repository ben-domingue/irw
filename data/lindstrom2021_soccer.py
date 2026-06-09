from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.17045/sthlmuni.14980251.v1"
TITLE = ("Data and code for - Personality and Team Identification Predict "
         "Violent Intentions Among Soccer Supporters")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

SCALES = {
    "honesty_humility": [f"HH{i}R" if i in (1,2,3,4,7,9) else f"HH{i}"
                         for i in range(1, 11)],
    "team_identification": ["H1", "H2", "H3"],
    "conscientiousness":   ["CN3", "CN4", "CN5", "CN6", "CN7R", "CN8", "CN9"],
    "violent_intentions":  ["VI1", "VI2", "VI3", "VI4R", "VI5R", "VI6", "VI7R"],
}

COV_MAP = {"A": "cov_age", "G": "cov_gender", "Ed": "cov_education", "SES": "cov_ses"}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    url = "https://ndownloader.figshare.com/files/29018463"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), sep=";")


def convert():
    raw = fetch_data()
    raw = raw.reset_index(drop=True)
    raw["id"] = raw.index + 1
    raw = raw.rename(columns=COV_MAP)
    cov_cols = list(COV_MAP.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_index()

    for scale, items in SCALES.items():
        present = [c for c in items if c in raw.columns]
        wide = raw[["id"] + cov_cols + present].copy()
        long = wide.melt(id_vars=["id"] + cov_cols, value_vars=present,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"lindstrom2021_{scale}.csv"
        long.to_csv(OUT_DIR / fname, index=False)

        row = {
            "file":           fname,
            "doi":            DOI,
            "title":          TITLE,
            "scale":          scale,
            "n_participants": long["id"].nunique(),
            "n_items":        long["item"].nunique(),
            "n_responses":    len(long),
            "resp_range":     f"{int(long['resp'].min())}-{int(long['resp'].max())}",
            "license":        "cc-by",
            "notes":          f"1-7 Likert; Swedish soccer supporters; "
                              f"scale: {scale}; resp direction unverified",
            "status":         "cleaned",
        }
        existing = [r for r in existing if r.get("file") != fname]
        existing.append(row)
        print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={int(long['resp'].min())}-{int(long['resp'].max())}")

    _write_index(existing)


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
