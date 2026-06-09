from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.3389/fpsyg.2022.1014794.s001"
TITLE = ("Data_Sheet_1_Self-esteem mediated relations between loneliness and "
         "social anxiety in Chinese adolescents with left-behind experience")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

COV_MAP = {
    "age":                  "cov_age",
    "grade":                "cov_grade",
    "sex":                  "cov_sex",
    "ONLY CHILD":           "cov_only_child",
    "Left-behind type":     "cov_left_behind_type",
    "father's job":         "cov_father_job",
    "mother's job":         "cov_mother_job",
    "family income":        "cov_family_income",
    "father's education":   "cov_father_education",
    "mother's education":   "cov_mother_education",
}

# Scale boundaries confirmed from response distributions (max values: CLS=5, SES=4, SASC=3)
# CLS: A1-A24 present (16 items; 8 items removed from original numbering A1-A24)
# SES: A25-A34 (10 items, contiguous)
# SASC: A35-A48 (14 items; Chinese version is 14-item, not 10)
SCALES = {
    "cls":  ["A1","A3","A4","A6","A8","A9","A10","A12",
             "A14","A16","A17","A18","A20","A21","A22","A24"],
    "ses":  [f"A{i}" for i in range(25, 35)],
    "sasc": [f"A{i}" for i in range(35, 49)],
}

SCALE_NOTES = {
    "cls":  ("Children's Loneliness Scale (CLS; 16 items); 1-5; "
             "8 items absent from file (likely removed during adaptation)"),
    "ses":  "Rosenberg Self-Esteem Scale (SES; 10 items); 1-4",
    "sasc": ("Social Anxiety Scale for Children (SASC; 14 items); 1-3; "
             "Chinese version has 14 items vs 10 in original"),
}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    # Resolve download URL via figshare API (article 21515877)
    r = requests.get("https://api.figshare.com/v2/articles/21515877",
                     headers=UA, timeout=30)
    r.raise_for_status()
    files = r.json().get("files", [])
    url = next(f["download_url"] for f in files
               if f["name"].lower().endswith(".csv"))
    r2 = requests.get(url, headers=UA, timeout=60)
    r2.raise_for_status()
    return pd.read_csv(io.BytesIO(r2.content))


def convert():
    raw = fetch_data()

    # `number` (student number) resets per class/grade → use row index as id
    raw = raw.reset_index(drop=True)
    raw["id"] = raw.index + 1
    raw = raw.rename(columns=COV_MAP)
    cov_cols = list(COV_MAP.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_index()

    for scale, items in SCALES.items():
        present = [c for c in items if c in raw.columns]
        long = raw[["id"] + cov_cols + present].melt(
            id_vars=["id"] + cov_cols,
            value_vars=present,
            var_name="item",
            value_name="resp",
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"chen2022_{scale}.csv"
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
            "notes":          (f"Chinese left-behind adolescents N=303; "
                               f"id=row index (student number resets per class); "
                               f"{SCALE_NOTES[scale]}; resp direction unverified"),
            "status":         "cleaned",
        }
        existing = [r for r in existing if r.get("file") != fname]
        existing.append(row)
        print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={int(long['resp'].min())}-{int(long['resp'].max())}")

    # Remove the old single-file entry if present
    existing = [r for r in existing
                if r.get("file") != "chen2022_left_behind_adolescents.csv"]
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
