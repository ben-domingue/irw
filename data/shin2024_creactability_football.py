from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

REPO_ROOT  = Path(__file__).resolve().parent.parent
QUEUE_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "queue" / "10_6084_m9_figshare_26789680_v3.csv"
OUT_DIR    = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned"
INDEX_FILE = REPO_ROOT / "automated_finding" / "irw_output" / "cleaned_index.csv"

DOI   = "10.6084/m9.figshare.26789680.v3"
TITLE = "Validation of 'Creactability' Scale in Football: A Rasch Modeling Approach"

INDEX_FIELDS = ["file", "doi", "title", "scale", "n_participants", "n_items",
                "n_responses", "resp_range", "license", "notes", "status"]

SUBSCALES = {
    "quickness":    ["Quickness1", "Quickness2", "Quickness3"],
    "creativity":   ["Creativity1", "Creativity2", "Creativity3"],
    "adaptability": ["Adaptability1", "Adaptability2", "Adaptability3"],
    # "test" items (test1-3) present in figshare data but not part of the
    # validated creactability scale (paper documents only these 3 subscales).
}

# Team/player performance stats — not scale items.
COVARIATE_MAP = {
    "ranking":       "cov_ranking",
    "team_group":    "cov_team_group",
    "win":           "cov_win",
    "draw":          "cov_draw",
    "loss":          "cov_loss",
    "odds_winning":  "cov_odds_winning",
    "point":         "cov_point",
    "scored":        "cov_scored",
    "conced":        "cov_conced",
    "goal_differ":   "cov_goal_differ",
    "position_2":    "cov_position",
    "Career":        "cov_career_years",
}


def convert():
    df = pd.read_csv(QUEUE_FILE)

    all_items = [item for items in SUBSCALES.values() for item in items]
    cov_names = set(COVARIATE_MAP.keys())

    cov_wide = (
        df[df["item"].isin(cov_names)]
        .pivot(index="id", columns="item", values="resp")
        .rename(columns=COVARIATE_MAP)
        .reset_index()
    )

    item_rows = df[df["item"].isin(all_items)].copy()
    merged = item_rows.merge(cov_wide, on="id", how="left")
    cov_cols = [c for c in merged.columns if c.startswith("cov_")]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    existing = _load_index()

    for scale, items in SUBSCALES.items():
        fname = f"shin2024_creactability_{scale}.csv"
        out = merged[merged["item"].isin(items)][["id", "item", "resp"] + cov_cols].copy()
        out = out.sort_values(["id", "item"]).reset_index(drop=True)
        out.to_csv(OUT_DIR / fname, index=False)

        row = {
            "file":           fname,
            "doi":            DOI,
            "title":          TITLE,
            "scale":          f"creactability_{scale}",
            "n_participants": out["id"].nunique(),
            "n_items":        out["item"].nunique(),
            "n_responses":    len(out),
            "resp_range":     f"{int(out['resp'].min())}-{int(out['resp'].max())}",
            "license":        "cc-by",
            "notes":          "1-7 Likert; football player sample (n=241); "
                              "team performance stats kept as covariates; "
                              "resp direction unverified",
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
