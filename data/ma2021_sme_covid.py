from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/DVN/0ADT0D"
TITLE = ("Replication Data for: Valid questionnaire for small and "
         "medium-sized enterprises")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]

# DVN/WV1YJ1 contains the same 234×28 response matrix with abbreviated col names;
# 0ADT0D is processed here and WV1YJ1 is treated as a duplicate / skipped.
FILE_ID = 5019396  # "Valid questionnaires tab.xls"


def fetch_data() -> pd.DataFrame:
    url = f"https://dataverse.harvard.edu/api/access/datafile/{FILE_ID}"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    raw = fetch_data()

    raw = raw.rename(columns={"number": "id"})
    item_cols = [c for c in raw.columns if c != "id"]

    long = raw[["id"] + item_cols].melt(
        id_vars="id", value_vars=item_cols,
        var_name="item", value_name="resp",
    )

    # Slugify full English column names to lowercase_underscore item labels
    long["item"] = (
        long["item"]
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )

    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "ma2021_sme_covid.csv"
    long.to_csv(OUT_DIR / fname, index=False)

    row = {
        "file":           fname,
        "doi":            DOI,
        "title":          TITLE,
        "scale":          "sme_covid",
        "n_participants": long["id"].nunique(),
        "n_items":        long["item"].nunique(),
        "n_responses":    len(long),
        "resp_range":     f"{int(long['resp'].min())}-{int(long['resp'].max())}",
        "license":        "cc0",
        "notes":          (
            "COVID-19 impact questionnaire for SMEs in China; "
            "28 items covering financial performance, operations, costs, "
            "and government relief; 1-7 Likert; "
            "DVN/WV1YJ1 is identical and was skipped"
        ),
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
