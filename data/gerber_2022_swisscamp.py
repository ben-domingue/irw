from __future__ import annotations

"""
Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0276665
DOI: 10.1371/journal.pone.0276665
SI file: journal.pone.0276665_S1_Data.xls (CC BY 4.0)

Gerber, Gentaz & Malsert (2022), "The effects of Swiss summer camp on the
development of socio-emotional abilities in children", PLoS ONE 17(10):
e0276665.

The 92-item raw file bundles three distinct measurement instruments, each
administered pre- and post- (two-week gap), under one shared item-numbering
sequence:

  1. Adapted Self-Report Altruism Scale (Witt & Boleman 2009, adaptation of
     Rushton et al.'s Self-Report Altruism Scale) -- 14 items, PREALT#/POSTALT#,
     0 (never) - 4 (very often).
  2. Self-assessment questionnaire / self-esteem (Maintier & Alaphilippe) --
     9 items, PREEST#/POSTEST#, -2 (much less than others) to +2 (much more
     than others).
  3. French EAS (Emotionality, Activity, Sociability, Shyness) temperament
     questionnaire -- 20 items, 4 subscales x 5 items, columns named
     "<n>_PRE<SUBSCALE><k>[R]" / "<n>_POST<SUBSCALE><k>[R]", 1 (strongly
     disagree) - 5 (strongly agree). Subscales: TIM = timidite/shyness,
     EMO = emotionality, SOC = sociability, ACT = activity. Items with an
     "R" suffix are reverse-worded in the source instrument; per the paper's
     own scoring convention these are recoded before being summed into a
     subscale score, so we flip them here (recoded = 6 - raw on the 1-5
     scale) so that higher resp always means more of the construct across
     all items in a subscale.

Remaining columns (S8*/S9*/S10*/Q10*/Q12*) are one-off camp-specific or
control-group-specific control questions (e.g. "is this your first camp",
"which camp theme"), asymmetric between the two study arms and not part of
any validated scale -- they are dropped rather than forced into cov_* or a
4th single-item table.

Sentinel: raw file uses the literal string "." for missing/skipped
responses throughout.
"""

from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file?"
          "type=supplementary&id=10.1371/journal.pone.0276665.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# EAS pre-test raw column -> (subscale, item#, reversed?)
EAS_PRE_COLS = [
    "1_PRETIM1", "2_PREEMO1", "3_PRESOC1", "4_PREACT1", "5_PRESOC2",
    "6_PREEMO2", "7_PREACT2R", "8_PRETIM2R", "9_PREACT3", "10_PRESOC3",
    "11_PREEMO3", "12_PRETIM3R", "13_PREACT4", "14_PRETIM4", "15_PREEMO4",
    "16_PRESOC4R", "17_PREACT5R", "18_PRESOC5", "19_PREEMO5", "20_PRETIM5R",
]
EAS_POST_COLS = [c.replace("PRE", "POST") for c in EAS_PRE_COLS]

SUBSCALE_NAMES = {"TIM": "shyness", "EMO": "emotionality", "SOC": "sociability", "ACT": "activity"}


def _parse_eas_colname(raw: str) -> tuple[str, str, bool]:
    """'7_PREACT2R' -> ('ACT', 'ACT2', True); '1_PRETIM1' -> ('TIM','TIM1',False)"""
    suffix = raw.split("_", 1)[1]  # e.g. PREACT2R / POSTACT2R
    body = suffix.replace("PRE", "", 1) if suffix.startswith("PRE") else suffix.replace("POST", "", 1)
    reversed_item = body.endswith("R")
    core = body[:-1] if reversed_item else body
    # core like ACT2, TIM1, SOC5, EMO3
    subscale = core[:3]
    return subscale, core, reversed_item


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(pd.io.common.BytesIO(r.content), sheet_name="RawData", header=0)
    return df


def clean_resp(series: pd.Series) -> pd.Series:
    out = pd.to_numeric(series.replace(".", pd.NA), errors="coerce")
    return out


def build_covariates(df: pd.DataFrame) -> pd.DataFrame:
    cov = pd.DataFrame({"id": df["Participant"].astype(int)})
    cov["treat"] = (df["Condition"] == 1).astype(int)  # 1 = camp group, 0 = control group
    cov["cov_age"] = clean_resp(df["Q1AGE"])
    cov["cov_sex"] = clean_resp(df["Q4SEX"])
    cov["cov_class"] = clean_resp(df["Q3CLAS"])
    return cov


def build_two_wave_scale(df: pd.DataFrame, cov: pd.DataFrame,
                          pre_cols: list[str], post_cols: list[str],
                          item_names: list[str], resp_min: float, resp_max: float,
                          item_family: list[str] | None = None) -> pd.DataFrame:
    frames = []
    for wave, cols in ((1, pre_cols), (2, post_cols)):
        wide = df[["Participant"] + cols].copy()
        wide.columns = ["id"] + item_names
        wide["id"] = wide["id"].astype(int)
        long = wide.melt(id_vars=["id"], value_vars=item_names, var_name="item", value_name="resp")
        long["resp"] = clean_resp(long["resp"])
        long["wave"] = wave
        frames.append(long)
    long = pd.concat(frames, ignore_index=True)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[(long["resp"] >= resp_min) & (long["resp"] <= resp_max)].reset_index(drop=True)

    if item_family is not None:
        fam_map = dict(zip(item_names, item_family))
        long["item_family"] = long["item"].map(fam_map)

    long = long.merge(cov, on="id", how="left")
    col_order = ["id", "item", "resp", "wave", "treat", "cov_age", "cov_sex", "cov_class"]
    if item_family is not None:
        col_order.append("item_family")
    long = long[col_order].sort_values(["id", "wave", "item"]).reset_index(drop=True)
    return long


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch_raw()
    cov = build_covariates(df)

    # --- 1. Altruism scale (14 items, 0-4) ---
    alt_items = [f"ALT{i}" for i in range(1, 15)]
    alt_pre = [f"PREALT{i}" for i in range(1, 15)]
    alt_post = [f"POSTALT{i}" for i in range(1, 15)]
    alt_long = build_two_wave_scale(df, cov, alt_pre, alt_post, alt_items, 0, 4)
    write_scale(alt_long, "gerber_2022_altruism.csv")

    # --- 2. Self-esteem / self-assessment scale (9 items, -2 to +2) ---
    est_items = [f"EST{i}" for i in range(1, 10)]
    est_pre = [f"PREEST{i}" for i in range(1, 10)]
    est_post = [f"POSTEST{i}" for i in range(1, 10)]
    est_long = build_two_wave_scale(df, cov, est_pre, est_post, est_items, -2, 2)
    write_scale(est_long, "gerber_2022_selfesteem.csv")

    # --- 3. EAS temperament (20 items, 4 subscales, 1-5, R-items flipped) ---
    eas_item_names = []
    eas_family = []
    reversed_flags = []
    for raw_col in EAS_PRE_COLS:
        subscale, core, is_rev = _parse_eas_colname(raw_col)
        eas_item_names.append(core)
        eas_family.append(SUBSCALE_NAMES[subscale])
        reversed_flags.append(is_rev)

    eas_long = build_two_wave_scale(df, cov, EAS_PRE_COLS, EAS_POST_COLS, eas_item_names,
                                     1, 5, item_family=eas_family)
    rev_items = {name for name, rev in zip(eas_item_names, reversed_flags) if rev}
    rev_mask = eas_long["item"].isin(rev_items)
    eas_long.loc[rev_mask, "resp"] = 6 - eas_long.loc[rev_mask, "resp"]
    write_scale(eas_long, "gerber_2022_eas_temperament.csv")


if __name__ == "__main__":
    convert()
