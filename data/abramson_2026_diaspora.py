"""Abramson, Menon & Yakter (2026) -- Jewish-American diaspora attachment survey experiment.

Source: https://doi.org/10.7910/DVN/NGRR1Q
DOI: 10.7910/DVN/NGRR1Q
Data: data_wave1_2022-1.tab (file 14145868), data_wave2_2024-1.tab (file 14145867)
License: CC0 1.0

Pre-registered two-wave survey experiment on Jewish-Americans (N = 1,200 per
wave; 719 wave-2 respondents are wave-1 repeats). Respondents read one of three
appeal vignettes or a control text, then answered four Likert grids. The
deposit's README documents every variable and the two reverse-coded items.

Tables written
--------------
abramson_2026_israel_policy      Q3grid_1-4, policies toward Israel,   1-5
abramson_2026_israel_attachment  Q4grid_1-3, attachment to Israel,     1-5
abramson_2026_mobilization       Q6grid_1-4, mobilization,             1-11
abramson_2026_jewish_identity    Q8grid_1-7, aspects of Jewish identity, 1-5

Not exported: Q5_1, Q7, Q9a_scale, Q10 are single-item measures; Q3_index,
Q4_index and Q6_index are means of the grids above; `antisemitism`, `orthodox`,
`orcon`, `attend`, `member`, `frIL`, `holocaust`, `age_c2*`, `qcats`, `qage`
are recodes built for the analysis.

Scale points: every grid value reconstructs the deposit's own index exactly
(mean of the items, with Q3grid_3 and Q4grid_2 reversed as the README states),
which confirms there is no in-range "don't know" code hiding in these columns.
Reverse-coded items are left as collected, per the IRW standard.

Person ids: the two waves' `caseid` ranges are disjoint. Wave-2 repeat
respondents carry `caseid_w1`, their wave-1 id, which is used as `id` so the
panel links; wave-2 respondents new in 2024 keep their own `caseid`.

Treatment: `treatment_group` is 1=Control, 2=Homeland Threat, 3=Homeland Threat
+ Past Trauma, 4=Homeland Threat + US Antisemitism. `treat` collapses this to
0/1 as the standard requires; the specific arm is kept as cov_treatment_arm.
"""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.7910/DVN/NGRR1Q"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
BASE = "https://dataverse.harvard.edu/api/access/datafile/"
WAVES = {1: 14145868, 2: 14145867}  # data_wave1_2022-1.tab, data_wave2_2024-1.tab

COV_MAP = {
    "weight": "cov_survey_weight",
    "gender": "cov_gender",
    "birthyr": "cov_birthyr",
    "educ": "cov_educ",
    "faminc_new": "cov_faminc",
    "inputstate": "cov_state",
    "pid3": "cov_pid3",
    "Q2": "cov_denomination",
}

SCALES = [
    ("abramson_2026_israel_policy", [f"Q3grid_{i}" for i in range(1, 5)], (1, 5)),
    ("abramson_2026_israel_attachment", [f"Q4grid_{i}" for i in range(1, 4)], (1, 5)),
    ("abramson_2026_mobilization", [f"Q6grid_{i}" for i in range(1, 5)], (1, 11)),
    ("abramson_2026_jewish_identity", [f"Q8grid_{i}" for i in range(1, 8)], (1, 5)),
]

# (index column, item columns, items to reverse before averaging) -- used only to
# confirm the raw codes are genuine scale points, never written to the output.
INDEX_CHECKS = [
    ("Q3_index", [f"Q3grid_{i}" for i in range(1, 5)], ["Q3grid_3"]),
    ("Q4_index", [f"Q4grid_{i}" for i in range(1, 4)], ["Q4grid_2"]),
    ("Q6_index", [f"Q6grid_{i}" for i in range(1, 5)], []),
]


def fetch(file_id: int) -> pd.DataFrame:
    r = requests.get(f"{BASE}{file_id}", headers=UA, timeout=300)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), sep="\t", low_memory=False)


def check_indices(df: pd.DataFrame, wave: int) -> None:
    for index_col, items, reversed_items in INDEX_CHECKS:
        vals = df[items].apply(pd.to_numeric, errors="coerce").copy()
        for col in reversed_items:
            vals[col] = 6 - vals[col]
        diff = (vals.mean(axis=1) - pd.to_numeric(df[index_col], errors="coerce")).abs()
        if diff.max() > 1e-9:
            raise ValueError(
                f"wave {wave}: {index_col} does not reconstruct from its items "
                f"(max abs diff {diff.max():.4g}) -- recheck the coding")


def build_frame() -> pd.DataFrame:
    frames = []
    for wave, file_id in WAVES.items():
        raw = fetch(file_id)
        check_indices(raw, wave)
        if raw["caseid"].nunique() != len(raw):
            raise ValueError(f"wave {wave}: caseid is not unique")

        df = raw.rename(columns=COV_MAP)
        df["id"] = raw["caseid"]
        if "caseid_w1" in raw.columns:
            linked = raw["caseid_w1"].notna()
            df.loc[linked, "id"] = raw.loc[linked, "caseid_w1"]
        df["id"] = df["id"].astype("int64")
        df["wave"] = wave
        df["treat"] = (pd.to_numeric(raw["treatment_group"], errors="coerce") != 1).astype(int)
        df["cov_treatment_arm"] = pd.to_numeric(raw["treatment_group"], errors="coerce")
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    dupes = combined.duplicated(["id", "wave"]).sum()
    if dupes:
        raise ValueError(f"{dupes} duplicate id/wave pairs after panel linking")
    return combined


def make_scale(df: pd.DataFrame, items: list[str], bounds: tuple[int, int]) -> pd.DataFrame:
    cov_cols = list(COV_MAP.values()) + ["cov_treatment_arm"]
    keys = ["id", "wave", "treat"]
    long = df[keys + cov_cols + items].melt(
        id_vars=keys + cov_cols,
        value_vars=items,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    lo, hi = bounds
    long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
    long["resp"] = long["resp"].astype(int)
    return (long[["id", "item", "resp", "wave", "treat"] + cov_cols]
            .sort_values(["id", "wave", "item"])
            .reset_index(drop=True))


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = build_frame()
    for name, items, bounds in SCALES:
        long = make_scale(df, items, bounds)
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f} "
              f"waves={sorted(long['wave'].unique())}")


if __name__ == "__main__":
    convert()
