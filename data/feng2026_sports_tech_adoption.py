from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

REPO_ROOT  = Path(__file__).resolve().parent.parent
QUEUE_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "queue" / "10_7910_dvn_zdnsfj.csv"
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/dvn/zdnsfj"
TITLE = "Questionnaire survey data on adolescents' intention to adopt intelligent sports assistance robots"

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]

SUBSCALES = {
    "perceived_usefulness":    ["PU1", "PU2", "PU3", "PU4"],
    "perceived_ease_of_use":   ["PEOU1", "PEOU2", "PEOU3", "PEOU4"],
    "autonomy":                ["AUT1", "AUT2", "AUT3", "AUT4"],
    "competence":              ["COMP1", "COMP2", "COMP3", "COMP4"],
    "ec":                      ["EC1", "EC2", "EC3", "EC4", "EC5"],   # abbrev unverified
    "intrinsic_motivation":    ["IM1", "IM2", "IM3", "IM4"],
    "behavioral_intention":    ["BI1", "BI2", "BI3"],
}

COVARIATE_MAP = {
    "Gender":                                   "cov_gender",
    "Age":                                      "cov_age",
    "School year":                              "cov_school_year",
    "City tier":                                "cov_city_tier",
    "Weekly exercise frequency":                "cov_exercise_freq",
    "Experience with \nsmart fitness devices":  "cov_experience_smart_devices",
}


def convert():
    df = pd.read_csv(QUEUE_FILE)

    all_item_names = [item for items in SUBSCALES.values() for item in items]
    cov_names = set(COVARIATE_MAP.keys())

    # Pivot covariates to wide.
    cov_rows = df[df["item"].isin(cov_names)].copy()
    cov_wide = (
        cov_rows
        .pivot(index="id", columns="item", values="resp")
        .rename(columns=COVARIATE_MAP)
        .reset_index()
    )

    item_rows = df[df["item"].isin(all_item_names)].copy()
    merged = item_rows.merge(cov_wide, on="id", how="left")
    cov_cols = [c for c in merged.columns if c.startswith("cov_")]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_index()

    for scale, items in SUBSCALES.items():
        fname = f"feng2026_{scale}.csv"
        out = merged[merged["item"].isin(items)][["id", "item", "resp"] + cov_cols].copy()
        out = out.sort_values(["id", "item"]).reset_index(drop=True)
        out.to_csv(OUT_DIR / fname, index=False)

        row = {
            "file":           fname,
            "doi":            DOI,
            "title":          TITLE,
            "scale":          scale,
            "n_participants": out["id"].nunique(),
            "n_items":        out["item"].nunique(),
            "n_responses":    len(out),
            "resp_range":     f"{int(out['resp'].min())}-{int(out['resp'].max())}",
            "license":        "cc0",
            "notes":          "1-7 Likert; resp direction unverified; EC subscale label unverified",
            "status":         "cleaned",
        }
        existing = [r for r in existing if r.get("file") != fname]
        existing.append(row)

        print(f"{fname}: ids={out['id'].nunique()} items={out['item'].nunique()} "
              f"resp={int(out['resp'].min())}-{int(out['resp'].max())}")

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
