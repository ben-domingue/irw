from __future__ import annotations

import csv
import re
from pathlib import Path

import pandas as pd

REPO_ROOT  = Path(__file__).resolve().parent.parent
QUEUE_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "queue" / "10_7910_dvn_shwnk1.csv"
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
OUT_FILE   = OUT_DIR / "cordova2019_clinical_edu_environment.csv"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/dvn/shwnk1"
TITLE = "Perception of clinical educational environment by students of physiotherapy"
SCALE = "clinical educational environment (DREEM-based)"

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def _short_label(full_text: str) -> str:
    """Extract leading item number and zero-pad: '3. Tengo...' -> 'item_03'."""
    m = re.match(r"^(\d+)\.", str(full_text).strip())
    return f"item_{int(m.group(1)):02d}" if m else full_text


def convert() -> pd.DataFrame:
    df = pd.read_csv(QUEUE_FILE)

    df["item"] = df["item"].apply(_short_label)
    df = df.sort_values(["id", "item"]).reset_index(drop=True)

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
        "notes":          "40-item DREEM-based instrument for physiotherapy interns (Chilean adaptation); "
                          "item labels item_01-item_40 from numbered Spanish question text; "
                          "resp direction unverified",
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
