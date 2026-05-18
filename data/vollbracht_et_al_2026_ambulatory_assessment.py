from __future__ import annotations

import os
import re
from pathlib import Path

import pandas as pd
import rdata

BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR / "Supplemental Material" / "datasets"
IN_RDA = DATASETS_DIR / "dataset_emoverse_withRTs.rda"

OUT_DIR = BASE_DIR / "vollbracht_et_al_2026_ambulatory_assessment"
OUT_CSV = OUT_DIR / "vollbracht_et_al_2026_ambulatory_assessment.csv"

ITEM_MAP: dict[str, tuple[str, str]] = {
    "stress": ("stress",  "stress_RT"),
    "pum1":   ("mood1",   "mood1_RT"),
    "pum2":   ("mood4.r", "mood4_RT"),
    "pum3":   ("mood6",   "mood6_RT"),
    "pum4":   ("mood8.r", "mood8_RT"),
    "wt1":    ("mood2",   "mood2_RT"),
    "wt2":    ("mood5.r", "mood5_RT"),
    "ct1":    ("mood3",   "mood3_RT"),
    "ct2":    ("mood7.r", "mood7_RT"),
    "att1":   ("nae5",    "nae5_RT"),
    "att2":   ("nae7",    "nae7_RT"),
    "att3":   ("nae9",    "nae9_RT"),
    "cla1":   ("ncla6.r",  "ncla6_RT"),
    "cla2":   ("ncla10.r", "ncla10_RT"),
    "cla3":   ("ncla12.r", "ncla12_RT"),
}

COV_CANDIDATES = ("gender", "age", "smart", "experience", "careless")


def _time_scheduled_to_seconds(s: object) -> float:
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return float("nan")
    t = str(s).strip()
    if not t:
        return float("nan")
    m = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$", t)
    if not m:
        return float("nan")
    h, mn = int(m.group(1)), int(m.group(2))
    sec = int(m.group(3)) if m.group(3) else 0
    return float(h * 3600 + mn * 60 + sec)


def _date_seconds_since_start(d: pd.DataFrame) -> pd.Series:
    if "day" not in d.columns or "time_scheduled" not in d.columns:
        return pd.Series([pd.NA] * len(d), dtype="Float64")
    day = pd.to_numeric(d["day"], errors="coerce")
    tsec = d["time_scheduled"].map(_time_scheduled_to_seconds)
    raw = day * 86400.0 + tsec
    gmin = raw.min(skipna=True)
    if pd.isna(gmin):
        return pd.Series([pd.NA] * len(d), dtype="Float64")
    return raw - float(gmin)


def _load_emoverse_df() -> pd.DataFrame:
    if not IN_RDA.is_file():
        raise FileNotFoundError(f"Missing input: {IN_RDA}")
    parsed = rdata.read_rda(IN_RDA)
    if "data" not in parsed:
        raise KeyError(f"Expected object 'data' in {IN_RDA}, got {list(parsed.keys())}")
    d = parsed["data"]
    if not isinstance(d, pd.DataFrame):
        raise TypeError(f"Expected DataFrame, got {type(d)}")
    d.columns = [str(c) for c in d.columns]
    return d


def convert() -> dict[str, pd.DataFrame]:
    d = _load_emoverse_df()

    for c in ("PARTICIPANT_ID", "cond", "occ_running"):
        if c not in d.columns:
            raise KeyError(f"Missing required column: {c}")
    for irw_item, (resp_c, rt_c) in ITEM_MAP.items():
        for col in (resp_c, rt_c):
            if col not in d.columns:
                raise KeyError(f"Missing column for {irw_item}: {col}")

    cov_keep = [c for c in COV_CANDIDATES if c in d.columns]
    date_sec = _date_seconds_since_start(d)

    frames: list[pd.DataFrame] = []
    for irw_item, (resp_col, rt_col) in ITEM_MAP.items():
        block = pd.DataFrame(
            {
                "id": d["PARTICIPANT_ID"],
                "item": irw_item,
                "resp": pd.to_numeric(d[resp_col], errors="coerce"),
                "rt": pd.to_numeric(d[rt_col], errors="coerce"),
                "date": date_sec,
                "trial_occasion": pd.to_numeric(d["occ_running"], errors="coerce"),
                "cov_group": pd.to_numeric(d["cond"], errors="coerce"),
            }
        )
        for c in cov_keep:
            block[f"cov_{c}"] = d[c]
        frames.append(block)

    long = pd.concat(frames, ignore_index=True)
    long = long.dropna(subset=["resp"])

    core = ["id", "item", "resp"]
    other = ["trial_occasion", "rt", "date"]
    cov_cols = sorted([c for c in long.columns if c.startswith("cov_")])
    long = long[core + other + cov_cols]
    long = long.sort_values(["id", "trial_occasion", "item"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_CSV, index=False)

    likert = long[long["cov_group"].ne(2) | long["cov_group"].isna()]
    slider = long[long["cov_group"].eq(2) & long["cov_group"].notna()]
    rng = (long["resp"].min(), long["resp"].max())
    print(
        f"{OUT_CSV.name}: rows={len(long)} ids={long['id'].nunique()} "
        f"items={long['item'].nunique()} resp_range={rng} "
        f"(likert cov_group!=2: {len(likert)}, slider cov_group==2: {len(slider)})"
    )
    return {"combined": long}


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    convert()
