from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/dvn/atlxc5"
TITLE = ("Replication Data for: Insight into the mechanism of non-compliance "
         "tasks on conscientiousness")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# Five subscales; item names match column headers in raw file
SCALES = {
    "noncompliance":    [f"NT{i}" for i in range(1, 9)],   # Non-compliance Tasks
    "self_efficacy":    [f"SE{i}" for i in range(1, 8)],   # Self-Efficacy
    "emotional_exhaust":[f"EE{i}" for i in range(1, 5)],   # Emotional Exhaustion
    "turnover_intent":  [f"TI{i}" for i in range(1, 5)],   # Turnover Intention
    "unethical_behav":  [f"UB{i}" for i in range(1, 5)],   # Unethical Behavior
}

COV_MAP = {
    "Gender":            "cov_gender",
    "Age":               "cov_age",
    "Educational level": "cov_education",
    "Trade type":        "cov_trade_type",
    "Work experience":   "cov_work_experience",
}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    url = "https://dataverse.harvard.edu/api/access/datafile/7374586"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    raw = fetch_data()
    raw = raw.rename(columns=COV_MAP)
    raw = raw.rename(columns={"Number": "id"})
    cov_cols = list(COV_MAP.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_index()

    for scale, items in SCALES.items():
        wide = raw[["id"] + cov_cols + items].copy()
        long = wide.melt(
            id_vars=["id"] + cov_cols,
            value_vars=items,
            var_name="item",
            value_name="resp",
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"xu2024_{scale}.csv"
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
            "license":        "cc0",
            "notes":          f"Likert scale; subscale: {scale}; "
                              "N=414 Chinese employees; resp direction unverified",
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
