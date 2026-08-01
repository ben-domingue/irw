from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0159386
# DOI: 10.1371/journal.pone.0159386
# Rowe, Fontaine, Lauver et al. (2016), "Neuromuscular Strain Increases
# Symptom Intensity in Chronic Fatigue Syndrome". S1 File. CC BY 4.0.
# 2x2 design: chronic fatigue syndrome (CFS) vs healthy controls x
# neuromuscular-strain maneuver vs sham. N=80.
#
# Three separate instruments -> three output files:
#   rowe_2016_symptoms: 5 symptom items (fatigue/body pain/lightheadedness/
#     concentration/headache), each a 0-10 self-rated intensity VAS,
#     repeated across 7 timepoints (baseline/5min/10min/15min/peak/
#     post-maneuver/24hr later) -> wave column. "ch"-prefixed change-score
#     columns (e.g. FatiguechPk) are derived deltas, not shipped.
#   rowe_2016_bai: Beck Anxiety Inventory, 21 items, 0-3, baseline only
#     (column labels literally confirm "Beck Anxiety Index question N").
#   rowe_2016_mfi20: Multidimensional Fatigue Inventory, 20 items, 1-5,
#     baseline only. "R"-suffixed columns (e.g. MFI2R) are reverse-scored
#     recalculated duplicates of the same item (confirmed by MFI2R's own
#     label "recalculated") -- excluded, along with the 5 MFIGfat/
#     MFIPhyfat/MFIRact/MFIRmotiv/MFIMfat subscale-total columns.
# CESD in the same file is a single pre-computed total score, not raw
# items -- not shipped.
#
# Two isolated data-entry errors dropped (caught in QC, 2026-08-01):
# MFI8 and MFI15 each had exactly one respondent (of 80) with a 0 --
# MFI-20 is a strict 1-5 scale everywhere else in the instrument, no
# other item ever goes below 1. Also two symptom-item values: respondent
# ID 230 had 9.5 in both FatiguePOST and BodypainPOST at the same wave --
# the only 2 fractional values among 2,800 otherwise-clean integer 0-10
# readings, isolated to one respondent/wave.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0159386.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Group": "cov_group", "Sex": "cov_sex", "Age": "cov_age"}

# (wave label, {output item name: source column name})
SYMPTOM_WAVES = [
    ("baseline", {"fatigue": "FatigueBase", "bodypain": "BodypainBase",
                   "lightheaded": "LHeadBase", "concentration": "ConcBase",
                   "headache": "HeadBase"}),
    ("5min", {"fatigue": "Fatigue5", "bodypain": "Bodypain5",
              "lightheaded": "Lhead5", "concentration": "Concen5",
              "headache": "Head5"}),
    ("10min", {"fatigue": "Fatigue10", "bodypain": "Bodypain10",
               "lightheaded": "Lhead10", "concentration": "Concen10",
               "headache": "Head10"}),
    ("15min", {"fatigue": "Fatigue15", "bodypain": "Bodypain15",
               "lightheaded": "Lhead15", "concentration": "Concen15",
               "headache": "Head15"}),
    ("peak", {"fatigue": "Fatiguepk", "bodypain": "Bodypainpk",
              "lightheaded": "LHpk", "concentration": "Concpk",
              "headache": "Headpk"}),
    ("post", {"fatigue": "FatiguePOST", "bodypain": "BodypainPOST",
              "lightheaded": "LheadPOST", "concentration": "ConcenPOST",
              "headache": "HeadPOST"}),
    ("24hr", {"fatigue": "Fatigue24", "bodypain": "Bodypain24",
              "lightheaded": "Lhead24", "concentration": "Concen24",
              "headache": "Head24"}),
]


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = fetch().rename(columns={"ID": "id", **COV_MAP})
    cov_cols = list(COV_MAP.values())
    assert df["id"].nunique() == len(df)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for wave, item_map in SYMPTOM_WAVES:
        for item_name, col in item_map.items():
            sub = df[["id"] + cov_cols + [col]].rename(columns={col: "resp"})
            sub["item"] = item_name
            sub["wave"] = wave
            rows.append(sub)
    long = pd.concat(rows, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # isolated data-entry anomaly: ID 230's FatiguePOST/BodypainPOST were
    # the only 2 fractional values among 2,800 otherwise-integer readings
    long = long[~((long["id"] == 230) & (long["wave"] == "post") &
                  (long["item"].isin(["fatigue", "bodypain"])))]
    long = long[["id", "item", "resp", "wave"] + cov_cols]
    long.to_csv(OUT_DIR / "rowe_2016_symptoms.csv", index=False)
    print(f"rowe_2016_symptoms: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} waves={long['wave'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

    bai_cols = [f"BAIq{i}" for i in range(1, 22)]
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=bai_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]
    long.to_csv(OUT_DIR / "rowe_2016_bai.csv", index=False)
    print(f"rowe_2016_bai: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

    mfi_cols = [f"MFI{i}" for i in range(1, 21)]
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=mfi_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    # isolated data-entry errors: MFI8 and MFI15 each had exactly one
    # respondent with a 0 on an otherwise strict 1-5 scale
    long = long[long["resp"] != 0]
    long = long[["id", "item", "resp"] + cov_cols]
    long.to_csv(OUT_DIR / "rowe_2016_mfi20.csv", index=False)
    print(f"rowe_2016_mfi20: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
