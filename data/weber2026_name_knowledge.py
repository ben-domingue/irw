from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

REPO_ROOT  = Path(__file__).resolve().parent.parent
QUEUE_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "queue" / "10_7910_dvn_3ckjv1.csv"
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
OUT_FILE   = OUT_DIR / "weber2026_name_knowledge.csv"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.7910/dvn/3ckjv1"
TITLE = "Exploring name-based instructor-student interaction in medical teaching"
SCALE = "name-based instructor-student interaction questionnaire"

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]

# Non-item columns in the melted queue file — pivot back to wide as covariates.
COVARIATE_MAP = {
    "Semester":         "cov_semester",
    "Alter":            "cov_age",
    "Anzahl der Kurse": "cov_n_courses",
    "Namenskenntnis":   "cov_name_knowledge",   # overall name knowledge (0-5)
    "Zeit":             "cov_time",
    "Professor":        "cov_nk_professor",
    "Oberarzt":         "cov_nk_oberarzt",
    "Assistenzarzt":    "cov_nk_assistenzarzt",
    "Dozent":           "cov_nk_dozent",
    "Hilfskraft":       "cov_nk_hilfskraft",
    "Vorlesung":        "cov_format_lecture",
    "Seminar":          "cov_format_seminar",
    "Praktikum":        "cov_format_practicum",
    "Klinik":           "cov_format_clinic",
    "Online":           "cov_format_online",
    "1on1":             "cov_format_1on1",
}


def convert() -> pd.DataFrame:
    df = pd.read_csv(QUEUE_FILE)

    cov_items = set(COVARIATE_MAP.keys())
    item_rows = df[~df["item"].isin(cov_items)].copy()
    cov_rows  = df[df["item"].isin(cov_items)].copy()

    # Pivot covariates back to one row per participant.
    cov_wide = (
        cov_rows
        .pivot(index="id", columns="item", values="resp")
        .rename(columns=COVARIATE_MAP)
        .reset_index()
    )

    out = item_rows.merge(cov_wide, on="id", how="left")
    cols = ["id", "item", "resp"] + [c for c in out.columns
                                     if c.startswith("cov_")]
    out = out[cols].sort_values(["id", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_FILE, index=False)

    _update_index(out)

    print(f"{OUT_FILE.name}: rows={len(out)} ids={out['id'].nunique()} "
          f"items={out['item'].nunique()} "
          f"resp_range={int(out['resp'].min())}-{int(out['resp'].max())}")
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
        "license":        "cc0",
        "notes":          "X1-X59 are pilot questionnaire items (1-5 Likert); "
                          "name knowledge and instructor-type ratings kept as covariates; "
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
