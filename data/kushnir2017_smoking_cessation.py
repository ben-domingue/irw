from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/DVN/8LBLYS"
TITLE = ("Data Set for Unassisted Smoking Cessation: The Role of "
         "Motivation and Personality Factors")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

import re as _re

# BFI responses are stored as text labels; map to 1-5
BFI_LABEL_MAP = {
    "Disagree strongly":           1,
    "Disagree a little":           2,
    "Neither agree nor disagree":  3,
    "Agree a little":              4,
    "Agree strongly":              5,
}

# ANRT responses are stored as text labels; map to 1-5
ANRT_LABEL_MAP = {
    "Strongly disagree":    1,
    "Do NOT really agree":  2,
    "More or less agree":   3,
    "Generally agree":      4,
    "Fully agree":          5,
    # "Don't know" → NaN (dropped)
}

# FTND responses are per-item (mixed formats); standard ordinal scoring 0-3 / 0-1
FTND_ITEM_MAPS = {
    1: {"Within 5 minutes": 3, "6 - 30 minutes": 2, "31 - 60 minutes": 1, "After 60 minutes": 0},
    2: {"Yes": 1, "No": 0},
    3: {"The first one in the morning": 1, "Any other": 0},
    4: {"10 or less": 0, "11 - 20": 1, "21 - 30": 2, "31 or more": 3},
    5: {"Yes": 1, "No": 0},
    6: {"Yes": 1, "No": 0},
}

# Column prefixes to extract — item numbers resolved dynamically from raw headers
# because BFI_38 has a double open-paren typo in the source file.
# FTND_SCORE is the composite total — excluded; regex requires digit so it won't match.
SCALE_PATTERNS = {
    "bfi":  _re.compile(r"BFI_(\d+)"),
    "tsrq": _re.compile(r"TSRQ_(\d+)"),
    "anrt": _re.compile(r"ANRT_(\d+)"),
    "ftnd": _re.compile(r"FTND_(\d+)"),
}

# Exact-match patterns for covariate columns (anchored to avoid hitting AGE_SMK_* etc.)
COV_EXACT = {
    r"\(SMOKER\) What is your smoking status":     "cov_smoker_status",
    r"\(AGE\) How old are you":                    "cov_age",
    r"\(GENDER\) Gender":                          "cov_gender",
    r"\(EDUCATION\) What level of education":      "cov_education",
}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def fetch_data() -> pd.DataFrame:
    url = "https://dataverse.harvard.edu/api/access/datafile/3059090"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def _extract_scale_cols(df: pd.DataFrame) -> dict[str, list[str]]:
    """Return {scale_name: [col, ...]} sorted by item number."""
    result: dict[str, list[str]] = {}
    for scale, pat in SCALE_PATTERNS.items():
        cols = sorted(
            [c for c in df.columns if pat.search(c)],
            key=lambda c: int(pat.search(c).group(1)),
        )
        if cols:
            result[scale] = cols
    return result


def _extract_cov_cols(df: pd.DataFrame) -> dict[str, str]:
    rename = {}
    seen_targets: set[str] = set()
    for c in df.columns:
        for pat, new_name in COV_EXACT.items():
            if _re.search(pat, c) and new_name not in seen_targets:
                rename[c] = new_name
                seen_targets.add(new_name)
                break
    return rename


def convert():
    raw = fetch_data()
    cov_rename = _extract_cov_cols(raw)
    raw = raw.rename(columns=cov_rename)
    cov_cols = list(cov_rename.values())

    # Drop 2 duplicate rows (login datetime not unique for 2 participants)
    raw = raw.drop_duplicates().reset_index(drop=True)
    raw["id"] = raw.index + 1

    scales = _extract_scale_cols(raw)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_index()

    for scale, cols in scales.items():
        present = [c for c in cols if c in raw.columns]
        if not present:
            print(f"  WARNING: no columns found for scale {scale}")
            continue

        wide = raw[["id"] + cov_cols + present].copy()
        long = wide.melt(
            id_vars=["id"] + cov_cols,
            value_vars=present,
            var_name="item",
            value_name="resp",
        )
        # BFI/ANRT: text labels → int; FTND: per-item maps; TSRQ: already numeric
        if scale == "bfi":
            long["resp"] = long["resp"].map(BFI_LABEL_MAP)
        elif scale == "anrt":
            long["resp"] = long["resp"].map(ANRT_LABEL_MAP)
        elif scale == "ftnd":
            pat = SCALE_PATTERNS["ftnd"]
            long["resp"] = long.apply(
                lambda row: FTND_ITEM_MAPS[int(pat.search(row["item"]).group(1))].get(row["resp"]),
                axis=1,
            )
        else:
            long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long.sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"kushnir2017_{scale}.csv"
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
            "notes":          (f"Unassisted smoking cessation study; N≈317; "
                               f"id=row index; FTND uses standard ordinal scoring "
                               f"(items 1,4: 0-3; items 2,3,5,6: 0-1); "
                               f"resp direction unverified"),
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
