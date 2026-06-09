from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.6084/m9.figshare.29488523.v2"
TITLE = "AI Literacy Questionnaire data"
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# 50 items from the AI Literacy Questionnaire (Skalka & Przybyła-Kasperek, 2025)
# Subscales: L(5), RE(6), R(6), SG(5), CM(4), A(5), IM(4), S(5), C(5), BI(5)
ITEM_COLS = (
    [f"L{i}"  for i in range(1, 6)]  +
    [f"RE{i}" for i in range(1, 7)]  +
    [f"R{i}"  for i in range(1, 7)]  +
    [f"SG{i}" for i in range(1, 6)]  +
    [f"CM{i}" for i in range(1, 5)]  +
    [f"A{i}"  for i in range(1, 6)]  +
    [f"IM{i}" for i in range(1, 5)]  +
    [f"S{i}"  for i in range(1, 6)]  +
    [f"C{i}"  for i in range(1, 6)]  +
    [f"BI{i}" for i in range(1, 6)]
)

COV_MAP = {
    "year":                   "cov_year",
    "Grade (year of study):": "cov_grade",
    "Age":                    "cov_age",
    "Gender":                 "cov_gender",
    "Country":                "cov_country",
}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    # Direct download URL from figshare article 29488523
    url = "https://ndownloader.figshare.com/files/56034941"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content))


def convert():
    raw = fetch_data()

    # user_id resets each survey year (2022/2023/2024 cohorts) →
    # composite id avoids duplicates across cohorts
    raw["id"] = raw["year"].astype(int) * 10000 + raw["user_id"].astype(int)
    raw = raw.rename(columns=COV_MAP)
    cov_cols = list(COV_MAP.values())

    long = raw[["id"] + cov_cols + ITEM_COLS].melt(
        id_vars=["id"] + cov_cols,
        value_vars=ITEM_COLS,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "skalka2025_ai_literacy.csv"
    long.to_csv(OUT_DIR / fname, index=False)

    row = {
        "file":           fname,
        "doi":            DOI,
        "title":          TITLE,
        "scale":          "ai_literacy",
        "n_participants": long["id"].nunique(),
        "n_items":        long["item"].nunique(),
        "n_responses":    len(long),
        "resp_range":     f"{int(long['resp'].min())}-{int(long['resp'].max())}",
        "license":        "cc-by",
        "notes":          ("AI Literacy Questionnaire; Polish university students; "
                           "3 cohorts 2022-2024; id = year*10000+user_id (resets "
                           "per year); 10 subscales (L,RE,R,SG,CM,A,IM,S,C,BI) "
                           "kept as single scale file; resp direction unverified"),
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
