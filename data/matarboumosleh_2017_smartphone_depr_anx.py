#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0182239
# DOI: 10.1371/journal.pone.0182239
# Supporting Information: https://doi.org/10.1371/journal.pone.0182239.s001 (S1 Dataset, XLS)
#
# Three distinct instruments in one raw file -> three separate output tables
# (one scale per file, per datastandard.md):
#   1. matarboumosleh_2017_spai26 -- 26-item Smartphone Addiction Inventory
#      (SPAI), 4-point Likert (1=strongly disagree .. 4=strongly agree).
#      Subscale/total aggregate columns (Compulsive_Behavior,
#      Functional_Impairment, Withdrawal, Tolerance, TotAddiction_Score)
#      are excluded -- composites, not raw items.
#   2. matarboumosleh_2017_phq2 -- PHQ-2 depression screener, 2 items,
#      0-3 scale. Depression_score (the 0-6 total) excluded.
#   3. matarboumosleh_2017_gad2 -- GAD-2 anxiety screener, 2 items, 0-3
#      scale. Anxiety_score (the 0-6 total) excluded.
#
# Missing values are coded as the literal string "." throughout the raw
# file (confirmed: every item and demographic column mixes int and "."
# string values) -- pd.to_numeric(errors="coerce") turns these into NaN,
# which are then dropped. Kept demographic covariates: AGE, Gender,
# Faculty, Class, Prsnlty_type (self-reported Type A/B personality).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0182239.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "AGE": "cov_age",
    "Gender": "cov_gender",
    "Faculty": "cov_faculty",
    "Class": "cov_class",
    "Prsnlty_type": "cov_personality_type",
}

SPAI_ITEMS = [
    "ExcessveSmrtPhn_Use", "TnseStp_Smrtphn_Use", "hook_smrtPhn",
    "Rstlss_NoSmrtphn", "Vig_SmrtPhnUse", "SmrtPhnUse_MreTmeMny",
    "SlptLss4HrsMreTh1_SmrtPhnUse", "SameTmeIntrnt_Ngtv_Relations",
    "UpstStp_SmrtPhnUse", "RcntSigIncTime_SmrtPhnUseWk",
    "FailCntrlImplse_smrtphnUse", "FavorSmrtPhn_SpndTimefrnds",
    "PainBckEye_ExcSmrtPhnUse", "FrstThghtSmrtphnUse_WakeUp",
    "NgtveSchlJob_SmrtPhnUse", "MissStp_SmrtPhnUse",
    "DcreasdFmlyIntrction_SmrtPhnUse", "DcreasdHobbies_SmrtPhnUse",
    "UrgeSmrtPhnUse_OnceStpUse", "LifeJoylss_NoSmrtPhn",
    "NgtvePhysHlthEffcts_SmrtPhnUse", "Spnd_LsstimeSmrtPhn_EffortsUselss",
    "DcreasdSlpTimeQulty_SmrtPhnUse", "IncrsdTimeSmrtPhnUse_SameSatsfction",
    "CannotHveMeal_NosmrtPhn", "TiredDaytime_latenightSmrtPhnUse",
]
PHQ2_ITEMS = ["Lttl_IntrstDoingThngs", "Feel_Deprssd"]
GAD2_ITEMS = ["Feel_anxious", "NotAble_Stpworry"]

SCALES = [
    ("matarboumosleh_2017_spai26", SPAI_ITEMS, 1, 4),
    ("matarboumosleh_2017_phq2", PHQ2_ITEMS, 0, 3),
    ("matarboumosleh_2017_gad2", GAD2_ITEMS, 0, 3),
]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"ID": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    return df


def convert():
    df = fetch_data()
    cov_cols = list(COV_RENAME.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for out_name, item_cols, lo, hi in SCALES:
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]

        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()} rows={len(long)}")


if __name__ == "__main__":
    convert()
