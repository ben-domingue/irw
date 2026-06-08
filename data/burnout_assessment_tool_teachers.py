from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

REPO_ROOT  = Path(__file__).resolve().parent.parent
QUEUE_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "queue" / "10_7910_dvn_nfrees.csv"
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
OUT_FILE   = OUT_DIR / "burnout_assessment_tool_teachers.csv"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/dvn/nfrees"
TITLE = "A new validation of Burnout Assessment Tool: An IRT Analysis Among Teachers"
SCALE = "BAT (Burnout Assessment Tool)"

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]


def convert() -> pd.DataFrame:
    df = pd.read_csv(QUEUE_FILE)

    age = df[df["item"] == "Age"][["id", "resp"]].rename(columns={"resp": "cov_age"})
    bat = df[df["item"] != "Age"].copy()

    out = bat.merge(age, on="id", how="left")
    out = out[["id", "item", "resp", "cov_age"]]
    out = out.sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_FILE, index=False)

    _update_index(out)

    print(f"{OUT_FILE.name}: rows={len(out)} ids={out['id'].nunique()} "
          f"items={out['item'].nunique()} resp_range={out['resp'].min()}-{out['resp'].max()}")
    return out


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
        "license":        "unknown",
        "notes":          "BAT C (23 items) and BAT S (10 items) kept together; Age converted to cov_age",
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
