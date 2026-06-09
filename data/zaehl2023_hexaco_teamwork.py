from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "https://osf.io/jb94w/"
TITLE = ("The Influence of HEXACO Personality Traits on the Teamwork Quality "
         "in Student Software Teams")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

# HEXACO-60: items F01r–F60r (60 items, 1-5 Likert)
HEXACO_ITEMS = [f"F{i:02d}r" if str(i) in
                "1,9,10,12,14,15,20,21,24,26,28,30,31,32,35,41,42,44,46,48,49,52,53,56,57,59,60".split(",")
                else f"F{i:02d}"
                for i in range(1, 61)]

# Teamwork Quality (TWQ) subscales (all 1-5 Likert)
TWQ_SCALES = {
    "twq_communication": ["CMNC01","CMNC02","CMNC03","CMNC04r","CMNC05",
                           "CMNC06r","CMNC07r","CMNC08","CMNC09","CMNC10"],
    "twq_coordination":  ["CRDN1", "CRDN2", "CRDN3", "CRDN4r"],
    "twq_balance":       ["BLNC1", "BLNC2", "BLNC3r"],
    "twq_support":       [f"SPRT{i}" for i in range(1, 7)],
    "twq_commitment":    ["COMT1", "COMT2", "COMT3", "COMT4r"],
    "twq_cohesion":      [f"COHS{i:02d}" if i not in (2, 6) else f"COHS{i:02d}r"
                          for i in range(1, 11)],
}

COV_MAP = {"Gender": "cov_gender", "Age": "cov_age", "Degree Program": "cov_degree"}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    url = "https://osf.io/download/k4syv/"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), sep=";")


def _melt_scale(raw, id_col, cov_cols, items, scale_name, fname):
    present = [c for c in items if c in raw.columns]
    wide = raw[[id_col] + cov_cols + present].copy()
    long = wide.melt(id_vars=[id_col] + cov_cols, value_vars=present,
                     var_name="item", value_name="resp")
    long = long.rename(columns={id_col: "id"})
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    long.to_csv(OUT_DIR / fname, index=False)
    return long


def convert():
    raw = fetch_data()
    raw = raw.rename(columns=COV_MAP)
    cov_cols = list(COV_MAP.values())
    id_col = "id"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_index()

    all_scales = {"hexaco": HEXACO_ITEMS, **TWQ_SCALES}

    for scale, items in all_scales.items():
        fname = f"zaehl2023_{scale}.csv"
        long = _melt_scale(raw, id_col, cov_cols, items, scale, fname)

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
            "notes":          f"Student software teams (N=54); scale: {scale}; "
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
