#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC7304420
# DOI: 10.7717/peerj.9215
#
# Amarilla-Donoso et al. (2020), "Quality of life after hip fracture: a
# 12-month prospective study." PeerJ. CC BY 4.0. N=224.
# Supplementary file peerj-08-9215-s001.sav is a longitudinal (baseline,
# 1-month, 6-month, 1-year) hip-fracture cohort with four raw-item
# instruments: the 12-item SF-12 health survey, the 5-item EQ-5D, the
# 10-item Barthel Index of ADL, and the 8-item Lawton-Brody IADL scale.
# Each is written as its own file (one scale per file) with a `wave`
# column (1=baseline .. 4=1-year) rather than one column per timepoint.
# Pre-computed totals/subdomain scores (*_INDEX, dependency_level*,
# GUIJON_*, PCS/MCS, etc.) are excluded as aggregates per
# datastandard.md. No PII in the source file (study ID only, no names).

import io
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7304420/supplementaryFiles"
MEMBER = "peerj-08-9215-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

WAVES = [("BASAL", 1), ("1Month", 2), ("6Month", 3), ("1year", 4)]

SF12_ITEMS = ["RGH1", "PF02", "PF04", "RP2", "RP3", "RE2", "RE3", "RBP2",
              "RMH3", "RVT2", "MH4", "SF2"]
EQ5D_ITEMS = ["EQ5D1", "EQ5D2", "EQ5D3", "EQ5D4", "EQ5D5"]
LAWTON_ITEMS = list(range(1, 9))

COV_RENAME = {
    "AGE": "cov_age",
    "SEX": "cov_sex",
    "education_level": "cov_education",
    "CIVIL_STATUS": "cov_marital_status",
    "INCOME_MONTHLY": "cov_income",
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with zf.open(MEMBER) as f:
        df, _meta = pyreadstat.read_sav(io.BytesIO(f.read()))
    return df


def melt_wave(df: pd.DataFrame, col_to_item: dict, wave_num: int, cov_cols: list[str]) -> pd.DataFrame:
    cols = list(col_to_item.keys())
    keep = df[["id"] + cols + cov_cols].copy()
    long = keep.melt(id_vars=["id"] + cov_cols, value_vars=cols,
                      var_name="item", value_name="resp")
    long["item"] = long["item"].map(col_to_item)  # map() is order-independent, safe for melt output
    long["wave"] = wave_num
    return long


def write_scale(pieces: list[pd.DataFrame], cov_cols: list[str], out_name: str):
    long = pd.concat(pieces, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    raw = fetch_raw()
    raw = raw.rename(columns={"ID_BASDAT": "id"})
    assert raw["id"].nunique() == len(raw)
    raw["id"] = raw["id"].astype(int)
    raw = raw.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    # SF-12
    pieces = []
    for wave_suffix, wave_num in WAVES:
        col_to_item = {f"{item}_{wave_suffix}": item for item in SF12_ITEMS}
        pieces.append(melt_wave(raw, col_to_item, wave_num, cov_cols))
    write_scale(pieces, cov_cols, "amarilla_2020_sf12.csv")

    # EQ-5D
    pieces = []
    for wave_suffix, wave_num in WAVES:
        col_to_item = {f"{item}_{wave_suffix}": item for item in EQ5D_ITEMS}
        pieces.append(melt_wave(raw, col_to_item, wave_num, cov_cols))
    write_scale(pieces, cov_cols, "amarilla_2020_eq5d.csv")

    # Barthel Index (baseline column naming differs: BBASAL_N vs BARTHEL<wave>_N)
    barthel_wave_cols = {
        "BASAL": {f"BBASAL_{i}": f"barthel_{i}" for i in range(1, 11)},
        "1Month": {f"BARTHEL1Month_{i}": f"barthel_{i}" for i in range(1, 11)},
        "6Month": {f"BARTHEL6Month_{i}": f"barthel_{i}" for i in range(1, 11)},
        "1year": {f"BARTHEL1year_{i}": f"barthel_{i}" for i in range(1, 11)},
    }
    pieces = []
    for wave_suffix, wave_num in WAVES:
        pieces.append(melt_wave(raw, barthel_wave_cols[wave_suffix], wave_num, cov_cols))
    write_scale(pieces, cov_cols, "amarilla_2020_barthel.csv")

    # Lawton-Brody IADL (baseline column naming differs: LYBRODYBASALn vs LYBRODY<wave>n)
    lb_wave_cols = {
        "BASAL": {f"LYBRODYBASAL{i}": f"lawtonbrody_{i}" for i in LAWTON_ITEMS},
        "1Month": {f"LYBRODY1Month{i}": f"lawtonbrody_{i}" for i in LAWTON_ITEMS},
        "6Month": {f"LYBRODY6Month{i}": f"lawtonbrody_{i}" for i in LAWTON_ITEMS},
        "1year": {f"LYBRODY1year{i}": f"lawtonbrody_{i}" for i in LAWTON_ITEMS},
    }
    pieces = []
    for wave_suffix, wave_num in WAVES:
        pieces.append(melt_wave(raw, lb_wave_cols[wave_suffix], wave_num, cov_cols))
    write_scale(pieces, cov_cols, "amarilla_2020_lawton_brody.csv")


if __name__ == "__main__":
    convert()
