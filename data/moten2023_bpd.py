from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/dvn/o7zbmw"
TITLE = ("Perceptions About How Racism Contributes to the Development of "
         "Borderline Personality Disorder")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# 24-item BPD checklist (Zanarini-style); row 0 in the file is a Qualtrics label row
Q8_ITEMS = [f"Q8_{i}" for i in range(1, 25)]

RESP_MAP = {"False": 0, "Slightly True": 1, "Mainly True": 2, "Very True": 3}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    url = "https://dataverse.harvard.edu/api/access/datafile/7513547"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    # Row 0 is Qualtrics label row; rows 1+ are real responses
    df = df.iloc[1:].reset_index(drop=True)
    df = df[df["ResponseId"].notna() & (df["ResponseId"] != "Response ID")]
    return df


def convert():
    df = fetch_data()

    df["id"] = df["ResponseId"]
    df["cov_age"]    = df["Q1"]
    df["cov_race"]   = df["Q2"]
    df["cov_gender"] = df["Q4"]

    cov_cols = ["cov_age", "cov_race", "cov_gender"]
    wide = df[["id"] + cov_cols + Q8_ITEMS].copy()

    long = wide.melt(
        id_vars=["id"] + cov_cols,
        value_vars=Q8_ITEMS,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = long["resp"].map(RESP_MAP)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "moten2023_bpd.csv"
    long.to_csv(OUT_DIR / fname, index=False)

    existing = _load_index()
    row = {
        "file":           fname,
        "doi":            DOI,
        "title":          TITLE,
        "scale":          "bpd",
        "n_participants": long["id"].nunique(),
        "n_items":        long["item"].nunique(),
        "n_responses":    len(long),
        "resp_range":     f"{int(long['resp'].min())}-{int(long['resp'].max())}",
        "license":        "cc0",
        "notes":          "0-3 ordinal (False/Slightly True/Mainly True/Very True); "
                          "24-item BPD checklist; N=11 PoC adults with BPD (US); "
                          "text responses recoded to 0-3; resp direction unverified",
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
