from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.1371/journal.pone.0342855.s001"
TITLE = "Questionnaire survey data of ceramic vases"
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# Three rating dimensions, 10 vases each; 1-7 scale
SCALES = {
    "typical": [f"Typical_{i}" for i in range(1, 11)],
    "novel":   [f"Novel_{i}"   for i in range(1, 11)],
    "liking":  [f"Liking_{i}"  for i in range(1, 11)],
}

COV_MAP = {"Gender": "cov_gender", "Age": "cov_age", "Study": "cov_study"}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    url = "https://ndownloader.figshare.com/files/63414918"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    import io
    return pd.read_excel(io.BytesIO(r.content), sheet_name="最新")


def convert():
    df = fetch_data()
    df = df.rename(columns=COV_MAP)
    cov_cols = list(COV_MAP.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_index()

    for scale, items in SCALES.items():
        long = df[["ID"] + cov_cols + items].melt(
            id_vars=["ID"] + cov_cols,
            value_vars=items,
            var_name="item",
            value_name="resp",
        )
        long = long.rename(columns={"ID": "id"})
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"wu2026_{scale}.csv"
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
            "notes":          "1-7 rating of ceramic vase stimuli; 3 dimensions "
                              "(typicality, novelty, liking); N=200 Chinese undergrads; "
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
