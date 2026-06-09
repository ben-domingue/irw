from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.6084/m9.figshare.30195541.v1"
TITLE = ("Dataset for: Sleep Quality as a Mediator Between Lifestyle and "
         "Cognitive and Agentic Student Engagement")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# EET = Educational Engagement with Technology (29 items, 1-6 Likert)
# ENG_* = Student Engagement subscales (1-7 Likert)
SCALES = {
    "eet":           [f"EET_{i:02d}" for i in range(1, 30)],
    "eng_emotional": [f"ENG_EMO_{i:02d}" for i in range(1, 10)],
    "eng_comprehensive": [f"ENG_COMP_{i:02d}" for i in range(1, 13)],
    "eng_cognitive": [f"ENG_COGN_{i:02d}" for i in range(1, 13)],
    "eng_agentic":   [f"ENG_AGEN_{i:02d}" for i in range(1, 11)],
}

COV_MAP = {"AGE": "cov_age", "SEX": "cov_sex",
           "WEIGHT": "cov_weight", "HEIGHT": "cov_height"}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    url = "https://ndownloader.figshare.com/files/58188073"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), sep=";")


def convert():
    raw = fetch_data()
    raw = raw.rename(columns=COV_MAP)
    raw = raw.rename(columns={"Unnamed: 0": "id"})
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

        fname = f"merlo2025_{scale}.csv"
        long.to_csv(OUT_DIR / fname, index=False)

        scale_label = ("1-6 Likert" if scale == "eet" else "1-7 Likert")
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
            "notes":          f"{scale_label}; N=1065 Italian students; scale: {scale}; "
                              "PSQI and TECH scales excluded (non-ordinal format); "
                              "resp direction unverified",
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
