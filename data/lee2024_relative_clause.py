from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

REPO_ROOT  = Path(__file__).resolve().parent.parent
QUEUE_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "queue" / "10_7910_dvn_k0srs8.csv"
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
OUT_FILE   = OUT_DIR / "lee2024_relative_clause.csv"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/dvn/k0srs8"
TITLE = "Advancing the Study of English Relative Clause Acquisition: A Rasch Modelling Approach"
SCALE = "relative clause comprehension (binary)"

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]

# Unnamed: 1 -> rc_01, Unnamed: 2 -> rc_02, ..., Unnamed: 18 -> rc_18
ITEM_MAP = {f"Unnamed: {i}": f"rc_{i:02d}" for i in range(1, 19)}


def convert() -> pd.DataFrame:
    df = pd.read_csv(QUEUE_FILE)
    df["item"] = df["item"].map(ITEM_MAP).fillna(df["item"])
    df = df.dropna(subset=["resp"]).sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)

    _update_index(df)

    print(f"{OUT_FILE.name}: rows={len(df)} ids={df['id'].nunique()} "
          f"items={df['item'].nunique()} "
          f"resp_range={int(df['resp'].min())}-{int(df['resp'].max())}")
    return df


def _update_index(df: pd.DataFrame) -> None:
    row = {
        "file":           OUT_FILE.name,
        "doi":            DOI,
        "title":          TITLE,
        "scale":          SCALE,
        "n_participants": df["id"].nunique(),
        "n_items":        df["item"].nunique(),
        "n_responses":    len(df),
        "resp_range":     f"{int(df['resp'].min())}-{int(df['resp'].max())}",
        "license":        "cc0",
        "notes":          "18-item binary (0/1) relative clause comprehension test; "
                          "item labels rc_01-rc_18 (original labels lost in Excel multi-row header); "
                          "see Appendix A.docx for item text",
        "status":         "cleaned",
    }

    existing = []
    if INDEX_FILE.exists():
        with open(INDEX_FILE, newline="") as f:
            existing = [r for r in csv.DictReader(f) if r.get("file") != row["file"]]

    with open(INDEX_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=INDEX_FIELDS)
        writer.writeheader()
        writer.writerows(existing)
        writer.writerow(row)


if __name__ == "__main__":
    convert()
