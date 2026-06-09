from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/DVN/9V2I0P"
TITLE = ("Optimizing Aging Male Symptom Questionnaire Through Genetic "
         "Algorithms Based Machine Learning Techniques")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# 17-item Aging Male Symptom (AMS) questionnaire; 1-5 ordinal
# Testo (testosterone, ng/dL) is a continuous covariate — NOT a person id.
# triage mistook it for an id (620 unique floats); actual N=1335 patients.
ITEM_COLS = [f"Q{i:02d}" for i in range(1, 18)]

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    url = "https://dataverse.harvard.edu/api/access/datafile/3655324"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def convert():
    raw = fetch_data()

    raw = raw.rename(columns={"Testo": "cov_testosterone"})
    raw = raw.reset_index(drop=True)
    raw["id"] = raw.index + 1  # row index as person id

    long = raw[["id", "cov_testosterone"] + ITEM_COLS].melt(
        id_vars=["id", "cov_testosterone"],
        value_vars=ITEM_COLS,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[long["resp"] % 1 == 0].reset_index(drop=True)  # drop imputed .5 values
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = "kim2020_ams.csv"
    long.to_csv(OUT_DIR / fname, index=False)

    row = {
        "file":           fname,
        "doi":            DOI,
        "title":          TITLE,
        "scale":          "ams",
        "n_participants": long["id"].nunique(),
        "n_items":        long["item"].nunique(),
        "n_responses":    len(long),
        "resp_range":     f"{long['resp'].min()}-{long['resp'].max()}",
        "license":        "cc0",
        "notes":          ("Aging Male Symptom (AMS) questionnaire; Korean men "
                           "N=1335; 1-5 ordinal; half-step (.5) values dropped "
                           "(6 items affected: Q05,Q06,Q08,Q09,Q11,Q17 — likely "
                           "imputed in ML preprocessing); "
                           "id=row index (Testo continuous covariate, not person id); "
                           "resp direction unverified; paper: doi:10.5534/wjmh.190077"),
        "status":         "cleaned",
    }
    existing = _load_index()
    existing = [r for r in existing if r.get("file") != fname]
    existing.append(row)
    _write_index(existing)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


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
