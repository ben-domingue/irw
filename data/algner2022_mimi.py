from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("You're Prettier When You Smile: Construction and Validation of a "
         "Questionnaire to Assess Microaggressions Against Women in the "
         "Workplace (Algner & Lorenz, 2022)")
URL  = ("https://www.frontiersin.org/journals/psychology/articles/"
        "10.3389/fpsyg.2022.809862/full")
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

STUDY1_URL = "https://ndownloader.figshare.com/files/34395206"
STUDY2_URL = "https://ndownloader.figshare.com/files/34395209"

COV_COLS = {
    "duration":            "cov_duration",
    "age":                 "cov_age",
    "gender":              "cov_gender",
    "kldb":                "cov_kldb",
    "education":           "cov_education",
    "occupational status": "cov_occupational_status",
    "weeklyHours":         "cov_weekly_hours",
    "durWorklife":         "cov_dur_worklife",
    "size_workplace":      "cov_size_workplace",
    "size_residence":      "cov_size_residence",
    "feminism":            "cov_feminism",
    "equality":            "cov_equality",
    "workenvironment":     "cov_workenvironment",
}

# Study 1 (N=500): 68-item MIMI item pool + three convergent-validity scales.
# Study 2 (N=612): final MIMI-16 scale + convergent-validity scales.
# Item columns are derived from each study's own header (below) rather than
# hand-typed ranges, since several items carry an 'r' (reverse-scored) suffix
# (e.g. mi5r, mi57r) that would be easy to mistype in a manual list.
WIS_COLS   = [f"inc{i}" for i in range(1, 17)]
PSGBI_COLS = [f"PSGBI{i}" for i in range(1, 22)]
SIA_COLS   = [f"sia{i}" for i in range(1, 13)]

UWES_COLS = [f"UWES{i}" for i in range(1, 10)]
CSE_COLS  = [f"CSE{i}" for i in range(1, 13)]
OSS_COLS  = [f"OSS{i}" for i in range(1, 7)]
TIS_COLS  = [f"TIS{i}" for i in range(1, 4)]


def _fetch(url: str) -> pd.DataFrame:
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.BytesIO(r.content), sep=";", encoding="utf-8-sig")


def _load(url: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = _fetch(url)
    raw = raw.rename(columns={"lfdn": "id"})
    present_cov = [c for c in COV_COLS if c in raw.columns]
    cov = raw[["id"] + present_cov].rename(columns=COV_COLS)
    return raw, cov


def _melt_scale(raw: pd.DataFrame, item_cols: list[str], cov: pd.DataFrame) -> pd.DataFrame:
    items = raw[["id"] + item_cols]
    cov_cols = list(cov.columns.drop("id"))
    long = items.merge(cov, on="id").melt(
        id_vars=["id"] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp"] + cov_cols
    return long[col_order].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={int(long['resp'].min())}-{int(long['resp'].max())} rows={len(long)}")


def convert():
    print("Downloading Study 1 (Data_Sheet_1) ...")
    raw1, cov1 = _load(STUDY1_URL)
    mimi_pool_cols = [c for c in raw1.columns if c.startswith("mi")]
    write_scale(_melt_scale(raw1, mimi_pool_cols, cov1), "algner2022_mimi_pool.csv")
    write_scale(_melt_scale(raw1, WIS_COLS, cov1),   "algner2022_wis.csv")
    write_scale(_melt_scale(raw1, PSGBI_COLS, cov1), "algner2022_psgbi.csv")
    write_scale(_melt_scale(raw1, SIA_COLS, cov1),   "algner2022_sia.csv")

    print("Downloading Study 2 (Data_Sheet_2) ...")
    raw2, cov2 = _load(STUDY2_URL)
    mimi16_cols = [c for c in raw2.columns if c.startswith("mi")]
    write_scale(_melt_scale(raw2, mimi16_cols, cov2), "algner2022_mimi16.csv")
    write_scale(_melt_scale(raw2, UWES_COLS, cov2),   "algner2022_uwes.csv")
    write_scale(_melt_scale(raw2, CSE_COLS, cov2),    "algner2022_cse.csv")
    write_scale(_melt_scale(raw2, OSS_COLS, cov2),    "algner2022_oss.csv")
    write_scale(_melt_scale(raw2, TIS_COLS, cov2),    "algner2022_tis.csv")


if __name__ == "__main__":
    convert()
