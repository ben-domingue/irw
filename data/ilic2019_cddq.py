from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/DVN/NV9GJD"
TITLE = ("Psychological distress among women with abnormal Pap smear results "
         "in Serbia: validity and reliability of the Cervical Dysplasia "
         "Distress Questionnaire")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# Var1 = participant ID; Var2–Var24 = 23 CDDQ items (1–4 Likert)
ITEM_COLS = [f"Var{i}" for i in range(2, 25)]

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    url = "https://dataverse.harvard.edu/api/access/datafile/3441423"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    raw = fetch_data()
    raw = raw.rename(columns={"Var1": "id"})
    rename_map = {f"Var{i}": f"item_{i-1:02d}" for i in range(2, 25)}
    raw = raw.rename(columns=rename_map)
    item_cols = [f"item_{i:02d}" for i in range(1, 24)]

    long = raw[["id"] + item_cols].melt(
        id_vars="id", value_vars=item_cols, var_name="item", value_name="resp"
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "ilic2019_cddq.csv"
    long.to_csv(OUT_DIR / fname, index=False)

    row = {
        "file":           fname,
        "doi":            DOI,
        "title":          TITLE,
        "scale":          "cddq",
        "n_participants": long["id"].nunique(),
        "n_items":        long["item"].nunique(),
        "n_responses":    len(long),
        "resp_range":     f"{int(long['resp'].min())}-{int(long['resp'].max())}",
        "license":        "cc0",
        "notes":          ("Cervical Dysplasia Distress Questionnaire (CDDQ); "
                           "Serbian women N=154; 1-4 Likert; "
                           "original column names Var2-Var24 → item_01-item_23; "
                           "resp direction unverified"),
        "status":         "cleaned",
    }
    existing = _load_index()
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
