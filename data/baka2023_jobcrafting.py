from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("Three-Wave Study on the Effects of Approach- and "
         "Avoidance-Oriented Job Crafting on Job-Related Well-Being: The "
         "Mediation Role of Satisfaction and Frustration of Basic "
         "Psychological Needs at Work (Baka & Prusik, 2023, figshare)")
URL  = "https://figshare.com/articles/dataset/Baza_repozytorium_Baka_Prusik_sav/21988799"
DOI  = "10.6084/m9.figshare.21988799"
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://ndownloader.figshare.com/files/39026075"

# Wave prefixes: no prefix = wave 1 (baseline), "f2" = wave 2, "f3" = wave 3
WAVE_PREFIXES = {1: "", 2: "f2", 3: "f3"}

# (label, n_items, valid_min, valid_max). Ranges verified against each
# item's actual value distribution, not just documented instrument ranges --
# baka2023_jcs originally showed a single resp=0 out of 52,761 rows, and
# avilesgonzalez2019_ces (a different script) showed a single resp=7 out of
# 6,449 -- both single-row outliers just past the real 1-N range, i.e. data
# entry artifacts, not genuine scale points. UWES's 0s are NOT this pattern
# (569 genuinely-distributed occurrences, matching its real 0-6 "Never" to
# "Always" scale) -- confirmed before deciding not to filter it.
SCALES = {
    # OLBI (Oldenburg Burnout Inventory), 8 items, 1-4 Likert
    "baka2023_olbi": ("OLBI", 8, 1, 4),
    # BPNSF (Basic Psychological Need Satisfaction and Frustration at Work
    # Scale), 24 items, 1-7 Likert
    "baka2023_bpnsf": ("BPNSF", 24, 1, 7),
    # UWES (Utrecht Work Engagement Scale), 17 items, 0-6 Likert
    "baka2023_uwes": ("UWES", 17, 0, 6),
    # JCS (Job Crafting Scale), 21 items, 1-5 Likert -- a single resp=0 (1 of
    # 52,761 rows) was a data-entry artifact, not a real "never" response.
    "baka2023_jcs": ("JCS", 21, 1, 5),
}

COV_COLS = {
    "M1_age": "cov_age",
    "M2_gender": "cov_gender",
    "locality": "cov_locality",
    "voivodeship": "cov_voivodeship",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_spss(pd.io.common.BytesIO(r.content), convert_categoricals=False)


def write_scale(raw: pd.DataFrame, prefix: str, n_items: int, valid_min: int,
                 valid_max: int, cov: pd.DataFrame, fname: str):
    cov_cols = list(cov.columns.drop("id"))
    frames = []
    for wave, wave_prefix in WAVE_PREFIXES.items():
        item_cols = [f"{wave_prefix}{prefix}_{i}" for i in range(1, n_items + 1)]
        items = raw[["id"] + item_cols].merge(cov, on="id")
        long = items.melt(
            id_vars=["id"] + cov_cols,
            value_vars=item_cols,
            var_name="item",
            value_name="resp",
        )
        # Strip the wave prefix so the same item name is shared across waves
        long["item"] = long["item"].str.replace(f"^{wave_prefix}", "", regex=True)
        long["wave"] = wave
        frames.append(long)
    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long[(long["resp"] >= valid_min) & (long["resp"] <= valid_max)]
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp", "wave"] + cov_cols
    long = long[col_order].sort_values(["id", "wave", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


def convert():
    print("Downloading Baza repozytorium Baka.Prusik.sav ...")
    raw = fetch_data()
    raw = raw.rename(columns={"ID": "id"})
    cov = raw[["id"] + list(COV_COLS.keys())].rename(columns=COV_COLS)

    for table, (prefix, n_items, valid_min, valid_max) in SCALES.items():
        write_scale(raw, prefix, n_items, valid_min, valid_max, cov, f"{table}.csv")


if __name__ == "__main__":
    convert()
