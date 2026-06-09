from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "https://osf.io/58xb9/"
TITLE = ("The Body in Focus: A Transdiagnostic Comparison of Body Checking "
         "Behavior in Bulimia Nervosa, Body Dysmorphic Disorder and Illness "
         "Anxiety Disorder")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# German clinical questionnaires answered once per participant (n≈216):
#   EDEQ  — Eating Disorder Examination Questionnaire (28 items; 0-6)
#   WI    — body image scale (14 items; scale TBC)
#   FKG   — Fragebogen Körpergefühl, body feelings questionnaire (20 items)
#   FKS   — Fragebogen Körperschema, body schema questionnaire (~17 items)
# EDEQ_Regelblutung is a binary menstruation item — excluded.
SCALES = {
    "edeq": [f"EDEQ_{i}" for i in range(1, 29)],
    "wi":   [f"WI_{i}"   for i in range(1, 15)],
    "fkg":  [f"FKG_{i}"  for i in range(1, 21)],
    "fks":  ["FKS_1", "FKS_3", "FKS_4", "FKS_5", "FKS_6", "FKS_7",
             "FKS_8", "FKS_9", "FKS_10", "FKS_11", "FKS_12", "FKS_13",
             "FKS_14", "FKS_15", "FKS_16", "FKS_17", "FKS_18"],
}

COV_MAP = {
    "vpcode (anonymized)": "id",
    "condition":           "cov_condition",
    "sample":              "cov_sample",   # 1=BN, 2=BDD, 3=IAD
    "sex":                 "cov_sex",
    "age":                 "cov_age",
}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    r = requests.get(
        "https://api.osf.io/v2/nodes/58xb9/files/osfstorage/",
        headers=UA, timeout=30,
    )
    r.raise_for_status()
    files = r.json().get("data", [])
    dl = next(
        f["links"]["download"]
        for f in files
        if f["attributes"]["name"].endswith(".xlsx")
    )
    r2 = requests.get(dl, headers=UA, timeout=60)
    r2.raise_for_status()
    return pd.read_excel(io.BytesIO(r2.content))


def convert():
    raw = fetch_data()
    raw = raw.rename(columns=COV_MAP)

    # Drop duplicate rows (~8 out of 224; keep first occurrence per vpcode)
    raw = raw.drop_duplicates(subset=["id"]).reset_index(drop=True)

    cov_cols = ["cov_condition", "cov_sample", "cov_sex", "cov_age"]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_index()

    for scale, items in SCALES.items():
        present = [c for c in items if c in raw.columns]
        if not present:
            print(f"  WARNING: no columns for scale {scale}")
            continue

        long = raw[["id"] + cov_cols + present].melt(
            id_vars=["id"] + cov_cols,
            value_vars=present,
            var_name="item",
            value_name="resp",
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"opladen2025_{scale}.csv"
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
            "notes":          (f"German clinical sample (BN/BDD/IAD); N≈216; "
                               f"cov_sample: 1=BN 2=BDD 3=IAD; "
                               f"FKS_2 absent from data; WI items are binary (1-2); "
                               f"EDEQ items 13-18 are frequency counts (0-28+) not "
                               f"0-6 ordinal — resp direction unverified; "
                               f"OSF: osf.io/58xb9"),
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
