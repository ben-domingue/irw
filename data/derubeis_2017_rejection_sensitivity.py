from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0185802
# DOI: 10.1371/journal.pone.0185802
# De Rubeis, Lugo, Witthoeft, Suetterlin, Pawelzik & Voegele (2017),
# "Rejection sensitivity as a vulnerability marker for depressive symptom
# deterioration in men". S1 File (.sav). CC BY 4.0. N=72 male inpatients
# with complete data at all three time points (intake, end-of-treatment/
# discharge, 6-month follow-up); paper confirms listwise deletion/complete-
# case analysis, no imputation. Two raw-item instruments repeated across
# waves, shipped as two tables with a `wave` column (1=intake,
# 2=discharge, 3=6-month follow-up; ARSQ was only administered at intake
# and discharge, so it has no wave-3 rows):
#   - BDI (Beck Depression Inventory): 21 items (0-3), plus item 19 split
#     into 19a/19b per the source columns -> 22 raw item columns per wave.
#   - ARSQ (Adult Rejection Sensitivity Questionnaire): 20 hypothetical
#     situations, each rated on two sub-items (A = anxiety/concern rating,
#     B = acceptance-likelihood rating), both 1-6 -> 40 raw item columns
#     per wave.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0185802.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = {"Age": "cov_age", "sex": "cov_sex", "highest_education": "cov_education"}

BDI_SUFFIXES = [str(i) for i in range(1, 19)] + ["19a", "19b", "20", "21"]
ARSQ_SUFFIXES = [f"{i}{letter}" for i in range(1, 21) for letter in ("A", "B")]

WAVE_PREFIX = {1: "intake", 2: "discharge", 3: "6MF"}


def fetch_df() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as tmp:
        tmp.write(r.content)
        tmp.flush()
        df, _meta = pyreadstat.read_sav(tmp.name)
    return df.rename(columns={"Participant_ID": "id", **COV_COLS})


def build_instrument(df: pd.DataFrame, instrument_prefix: str, suffixes: list[str],
                      waves: list[int]) -> pd.DataFrame:
    cov_names = list(COV_COLS.values())
    frames = []
    for wave in waves:
        prefix = WAVE_PREFIX[wave]
        # BDI_discharge__20 has a double underscore typo in the source file
        col_map = {}
        for suf in suffixes:
            candidates = [f"{instrument_prefix}_{prefix}_{suf}", f"{instrument_prefix}_{prefix}__{suf}"]
            src_col = next((c for c in candidates if c in df.columns), None)
            if src_col is None:
                raise KeyError(f"missing column for {instrument_prefix} {prefix} {suf}")
            col_map[src_col] = f"{instrument_prefix}_{suf}"
        sub = df[["id"] + cov_names + list(col_map.keys())].rename(columns=col_map)
        sub["wave"] = wave
        long = sub.melt(id_vars=["id", "wave"] + cov_names,
                         value_vars=list(col_map.values()),
                         var_name="item", value_name="resp")
        frames.append(long)
    out = pd.concat(frames, ignore_index=True)
    out["resp"] = pd.to_numeric(out["resp"], errors="coerce")
    out = out.dropna(subset=["resp"]).reset_index(drop=True)
    return out[["id", "item", "resp", "wave"] + cov_names]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = fetch_df()

    bdi = build_instrument(df, "BDI", BDI_SUFFIXES, waves=[1, 2, 3])
    # Data-entry error: a single BDI_9 cell = 11 (BDI items are scored 0-3,
    # except 19b which is a binary 0-1 sub-item); isolated to one respondent/
    # wave, not a genuine scale point. Drop per datastandard.md's "data entry
    # errors at known values" rule.
    bad = (bdi["item"] != "BDI_19b") & (bdi["resp"] > 3)
    print(f"dropping {bad.sum()} BDI data-entry error row(s): "
          f"{bdi.loc[bad, ['id', 'item', 'wave', 'resp']].to_dict('records')}")
    bdi = bdi.loc[~bad].reset_index(drop=True)
    arsq = build_instrument(df, "ARSQ", ARSQ_SUFFIXES, waves=[1, 2])

    for name, long in [
        ("derubeis_2017_bdi", bdi),
        ("derubeis_2017_arsq", arsq),
    ]:
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
