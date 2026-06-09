from __future__ import annotations

import csv
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT  = Path(__file__).resolve().parent.parent
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/DVN/SNLKUE"
TITLE = ("Replication Data for: Tell Me Who Is Your Leader, and I Will Tell You "
         "Who You Are: Foreign Leaders' Perceived Personality and Public Attitudes "
         "toward Their Countries and Citizenry")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]

# Five .tab files — one per study/experiment
STUDIES = {
    "s1e1_germany_israel": 3109066,
    "s1e2_israel_us":      3109067,
    "s2e1_germany_us":     3109068,
    "s2e2_turkey_us":      3109069,
    "s2e3_cedria_us":      3109070,
}

# Personality items present in all 5 studies with 1-5 Likert responses.
# c22, c24, c29 are binary (0/1 or 1/2) — excluded.
# c17 and c25 appear only in S2/most studies; c27_1/c27_2, c28_1/c28_2 vary by study.
# Core: 14 items consistent across all studies.
PERSONALITY_ITEMS = ["c1", "c2", "c3", "c4", "c5", "c8",
                     "c10", "c11", "c13", "c14", "c15", "c16", "c18", "c26"]

# Attitude items: a3 (0-5), a4 and a5 (1-5 with -99 as NA), a6 is binary (skipped)
ATTITUDE_ITEMS = ["a3", "a4", "a5"]


def fetch_study(file_id: int) -> pd.DataFrame:
    url = f"https://dataverse.harvard.edu/api/access/datafile/{file_id}"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), sep="\t")


def load_all_studies() -> pd.DataFrame:
    frames = []
    for study_name, file_id in STUDIES.items():
        df = fetch_study(file_id)
        # Standardize column names to lowercase
        df.columns = df.columns.str.lower()
        df["cov_study"] = study_name
        df["id"] = study_name + "_" + df.index.astype(str)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def make_personality(combined: pd.DataFrame) -> pd.DataFrame:
    keep = ["id", "cov_study", "positive_negative", "age", "educ"] + PERSONALITY_ITEMS
    # Only keep columns that actually exist
    keep = [c for c in keep if c in combined.columns]
    df = combined[keep].copy()
    df = df.rename(columns={
        "positive_negative": "cov_condition",
        "age":               "cov_age",
        "educ":              "cov_educ",
    })
    for col in ["cov_age", "cov_educ"]:
        if col in df.columns:
            df[col] = df[col].replace(0, pd.NA)
    cov_cols = [c for c in df.columns if c.startswith("cov_")]
    long = df[["id"] + cov_cols + PERSONALITY_ITEMS].melt(
        id_vars=["id"] + cov_cols,
        value_vars=PERSONALITY_ITEMS,
        var_name="item",
        value_name="resp",
    )
    # Replace 0 and -99 with NaN (missing/sentinel codes)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long.loc[long["resp"].isin([0, -99]), "resp"] = pd.NA
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp"] + cov_cols
    return long[col_order].sort_values(["id", "item"]).reset_index(drop=True)


def make_attitudes(combined: pd.DataFrame) -> pd.DataFrame:
    keep = ["id", "cov_study", "positive_negative", "age", "educ"] + ATTITUDE_ITEMS
    keep = [c for c in keep if c in combined.columns]
    df = combined[keep].copy()
    df = df.rename(columns={
        "positive_negative": "cov_condition",
        "age":               "cov_age",
        "educ":              "cov_educ",
    })
    for col in ["cov_age", "cov_educ"]:
        if col in df.columns:
            df[col] = df[col].replace(0, pd.NA)
    cov_cols = [c for c in df.columns if c.startswith("cov_")]
    att_cols = [c for c in ATTITUDE_ITEMS if c in df.columns]
    long = df[["id"] + cov_cols + att_cols].melt(
        id_vars=["id"] + cov_cols,
        value_vars=att_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long.loc[long["resp"].isin([0, -99]), "resp"] = pd.NA
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp"] + cov_cols
    return long[col_order].sort_values(["id", "item"]).reset_index(drop=True)


def _write_output(long: pd.DataFrame, fname: str, scale: str, notes: str):
    long.to_csv(OUT_DIR / fname, index=False)
    row = {
        "file":           fname,
        "doi":            DOI,
        "title":          TITLE,
        "scale":          scale,
        "n_participants": long["id"].nunique(),
        "n_items":        long["item"].nunique(),
        "n_responses":    len(long),
        "resp_range":     f"{long['resp'].min()}-{long['resp'].max()}",
        "license":        "cc0",
        "notes":          notes,
        "status":         "cleaned",
    }
    existing = _load_index()
    existing = [r for r in existing if r.get("file") != fname]
    existing.append(row)
    _write_index(existing)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    combined = load_all_studies()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    personality = make_personality(combined)
    _write_output(
        personality,
        "balmas2018_leader_personality.csv",
        "leader_personality",
        (
            "Perceived personality ratings of foreign leaders/citizens; "
            "5 studies pooled (s1e1-s2e3) via cov_study; "
            "14 core 1-5 Likert items (c1-c26) common to all studies; "
            "0 and -99 treated as NA; cov_condition=Positive_Negative; "
            "license field shows 'additional terms' but content is empty (Dataverse artifact)"
        ),
    )

    attitudes = make_attitudes(combined)
    _write_output(
        attitudes,
        "balmas2018_leader_attitudes.csv",
        "leader_attitudes",
        (
            "Public attitude items toward foreign countries/citizenry; "
            "5 studies pooled via cov_study; "
            "items a3, a4, a5; 1-5 Likert; "
            "0 and -99 both treated as NA (s1e1 uses -99, s1e2-s2e3 use 0 as missing sentinel); "
            "a6 (binary) excluded"
        ),
    )


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
