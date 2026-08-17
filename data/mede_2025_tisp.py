#!/usr/bin/env python3
"""TISP — Trust in Science and Science-Related Populism (68 countries).

Source data : https://osf.io/5c3qd/  (02_data/survey-data/ds_main.csv)
Paper       : Mede, N. G., Cologna, V., Berger, S., et al. (2025). Perceptions of
              science, science communication, and climate change attitudes in 68
              countries - the TISP dataset. Scientific Data, 12, 114.
DOI         : 10.1038/s41597-024-04100-7
License     : CC BY 4.0 (OSF node license resolves to
              "CC-By Attribution 4.0 International")
GitHub issue: https://github.com/ben-domingue/irw/issues/1597

`ds_main` is the cleaned, unweighted dataset of all 71,922 valid participants
(88 samples, 68 countries, 37 languages).  `ds_final` is the same data plus
post-stratification weights and drops a further ~2.4k cases; `ds_full` is the
raw uncleaned export.  We use `ds_main` so the full valid sample is preserved.

Fifteen multi-item batteries are written as separate tables.  Every response
range below was read off the master questionnaire
(05_survey-materials/questionnaire/master/core-questionnaire_english.docx),
which lists each block's numbered answer options verbatim; the four validated
scales are additionally confirmed against the paper's Technical Validation
section.  Ranges were not inferred from the observed data.

One battery needed filtering: CLIM_POLSUPPORT's options are
"Not at all (1) / Moderately (2) / Very much (3) / Not applicable (4)", so 4 is
a non-response code sitting inside the observed range, not a scale point.  It
is dropped via the scale's valid max of 3.  Every other battery's options are a
plain 1-5 or 1-7 ladder with no extra category.

The paper contains no imputation language (no occurrence of "imput", "MICE",
"LOCF", "mean substitution"); missing responses are left missing in ds_main and
are dropped here.  Computed scale means are deliberately not treated as items.

Single-item measures in the same file (BENEFIT_ONESELF, TRUST_METHOD,
TRUST_PEW, CLIM_TRUST, BENEFIT_REGION_*) are deliberately not written out --
IRW does not take single-item tables.
"""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# OSF file id for 02_data/survey-data/ds_main.csv
OSF_FILE = "6644c44b2eacc4913f09719a"
SRC_URL = f"https://osf.io/download/{OSF_FILE}/"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# out_name -> (column prefix, valid min, valid max)
# Valid max is the questionnaire's highest *substantive* option — for
# CLIM_POLSUPPORT that is 3, which drops the "Not applicable (4)" code.
SCALES = {
    # --- the four scales validated in the data descriptor -----------------
    "mede_2025_trust_scientists": ("TRUST_SCI_", 1, 5),
    "mede_2025_scipop": ("SCIPOP_", 1, 5),
    "mede_2025_outspokenness": ("OUTSPOKEN_", 1, 5),
    "mede_2025_sdo": ("SDO_", 1, 10),
    # --- further batteries in the same questionnaire ----------------------
    "mede_2025_sciinfo": ("SCIINFO_", 1, 7),           # never – once or more per day
    "mede_2025_sciengage": ("SCIENGAGE_", 1, 7),       # never – once or more per day
    "mede_2025_normperc": ("NORMPERC_", 1, 5),         # strongly disagree – strongly agree
    "mede_2025_willvul": ("WILLVUL_", 1, 5),           # not at all – very strongly
    "mede_2025_goals_priority": ("GOALS_PRIO_", 1, 5),  # very low – very high priority
    "mede_2025_goals_tackle": ("GOALS_TACKLE_", 1, 5),  # not at all – very strongly
    "mede_2025_clim_emotions": ("CLIM_EMO_", 1, 5),    # not at all – very strongly
    "mede_2025_clim_government": ("CLIM_GOV_", 1, 5),  # strongly disagree – strongly agree
    "mede_2025_clim_polsupport": ("CLIM_POLSUPPORT_", 1, 3),  # 4 = "not applicable"
    "mede_2025_clim_weather_past": ("CLIM_WEATHERPAST_", 1, 5),    # not at all – very much
    "mede_2025_clim_weather_future": ("CLIM_WEATHERFUTU_", 1, 5),  # not at all – very much
}

COV_MAP = {
    "LAB": "cov_sample",             # collaborating team that fielded the sample
    "COUNTRY_NAME": "cov_country",
    "COUNTRY_CONT": "cov_continent",
    "UserLanguage": "cov_language",  # language the survey was taken in
    "DEM_GENDER": "cov_gender",      # 0 = male, 1 = female, 2 = other
    "DEM_AGE": "cov_age",
    "DEM_AGEGRP": "cov_agegroup",
    "DEM_EDU": "cov_education",
    "DEM_INCOME_USD": "cov_income_usd",
    "DEM_POL_conservative": "cov_pol_conservative",
    "DEM_POL_right": "cov_pol_right",
    "DEM_RELIGIOUS": "cov_religious",
    "DEM_RESIDENCE": "cov_urban",    # 0 = rural, 1 = urban
}

# Numeric covariates stored with a comma decimal separator in the source CSV.
COMMA_DECIMAL = {"DEM_INCOME_USD"}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SRC_URL, headers=UA, timeout=600)
    r.raise_for_status()
    # semicolon-delimited, UTF-8 with BOM and a handful of invalid bytes in
    # free-text columns we do not carry through
    return pd.read_csv(
        io.BytesIO(r.content),
        sep=";",
        low_memory=False,
        encoding="utf-8-sig",
        encoding_errors="replace",
    )


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    # ID_QUALTRICS is unique per row but is a non-numeric string, so per the data
    # standard we use the row index as `id` instead.
    df = df.reset_index(drop=True).copy()
    df.insert(0, "id", df.index + 1)
    assert df["id"].nunique() == len(df)

    for src in COMMA_DECIMAL:
        df[src] = pd.to_numeric(
            df[src].astype(str).str.replace(",", ".", regex=False), errors="coerce"
        )

    keep = ["id"] + list(COV_MAP) + [
        c for c in df.columns if any(c.startswith(p) for p, _, _ in SCALES.values())
    ]
    return df[keep].rename(columns=COV_MAP)


def make_scale(df: pd.DataFrame, prefix: str, lo: int, hi: int) -> pd.DataFrame:
    items = sorted(c for c in df.columns if c.startswith(prefix))
    cov_cols = [c for c in df.columns if c.startswith("cov_")]

    long = df.melt(
        id_vars=["id"] + cov_cols,
        value_vars=items,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long[(long["resp"] >= lo) & (long["resp"] <= hi)]
    # all documented scales are integer-valued; a fractional value would signal
    # an aggregate or an imputed cell
    assert (long["resp"] % 1 == 0).all()

    return long[["id", "item", "resp"] + cov_cols].reset_index(drop=True)


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = prepare(fetch_raw())

    for out_name, (prefix, lo, hi) in SCALES.items():
        long = make_scale(df, prefix, lo, hi)
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(
            f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
            f"items={long['item'].nunique()} "
            f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}"
        )


if __name__ == "__main__":
    convert()
