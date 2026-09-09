#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0163656
# DOI: 10.1371/journal.pone.0163656
# Supporting Information: https://doi.org/10.1371/journal.pone.0163656.s001
#
# Four raw-item scales among unemployed adults, N≈1123: Subjective
# Happiness Scale (SHS, 4 items), Satisfaction With Life Scale (SWLS, 5
# items), Emotional Intelligence scale (16 items, "ie16" in the raw file
# is the 16th EI item -- a naming typo, not a different construct;
# renamed to ei16), Suicide Behaviours Questionnaire (SBQ, 4 items).
#
# `cuestionario` (retriage's "id") is NOT a person identifier -- rows
# sharing the same cuestionario value have different ages/sexes (spot-
# checked directly), so it's some kind of batch/version code, and using
# it as id would incorrectly merge up to 10 different unemployed adults
# into one. No real repeated-measures/wave structure exists either (no
# person is genuinely re-surveyed). Row index used as id instead; this
# is a single cross-sectional sample, not longitudinal. IE_total,
# Happiness_Scores, LifeSatisfaction_Scores, SuicideBehaviours_Scores,
# and the Z*/Sat_IE/Fel_IE columns are all derived aggregates, excluded.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0163656.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"age": "cov_age", "sex": "cov_sex", "marital_status": "cov_marital_status",
              "length_unemployment": "cov_length_unemployment",
              "unemployment_benefits": "cov_unemployment_benefits",
              "level_education": "cov_education"}

SCALES = {
    "extremera_2016_shs": [f"shs{i}" for i in range(1, 5)],
    "extremera_2016_swls": [f"swls{i}" for i in range(1, 6)],
    "extremera_2016_sbq": [f"sbq{i}" for i in range(1, 5)],
}
EI_COLS = [f"ei{i}" for i in range(1, 16)] + ["ie16"]

# The PRINTED response options of each instrument, as an inclusive (min, max)
# per item; "*" applies to every item in the scale. A response outside its own
# item's printed options is not a response, and is dropped.
#
# SHS, SWLS and the 16 EI items are plain 1-7 Likerts.
#
# The SBQ-R (Osman et al. 2001) is not: its four items print different numbers
# of options, and this deposit stores the printed OPTION NUMBER rather than the
# instrument's collapsed scoring code.
#
#   sbq1  1-6   1; 2; 3a; 3b; 4a; 4b
#   sbq2  1-5   never / rarely / sometimes / often / very often
#   sbq3  1-5   1 (no); 2a; 2b; 3a; 3b
#   sbq4  0-6   never .. very likely
#
# Every observed value matches those sets exactly, with one exception: `sbq3`
# carries 0 twice in 961 responses, and item 3 prints no option 0 (#1973). Same
# shape as the two SWLS zeros this file already dropped -- an isolated blank
# stored as 0 rather than missing. The deposit's own SuicideBehaviours_Scores
# column sums them straight through (rows 768 and 1080 score 3 and 5), so the
# authors did not decode 0 either.
#
# Note for anyone scoring this table: totals here run to 19, not the SBQ-R's
# published 3-18, because these are printed option numbers -- sbq1's six
# options collapse to 4 scoring levels and sbq3's five to 3. That is the
# encoding, not a defect, and it is unrelated to the two zeros.
VALID_RANGE = {
    "extremera_2016_shs":  {"*": (1, 7)},
    "extremera_2016_swls": {"*": (1, 7)},
    "extremera_2016_ei":   {"*": (1, 7)},
    "extremera_2016_sbq":  {"sbq1": (1, 6), "sbq2": (1, 5),
                             "sbq3": (1, 5), "sbq4": (0, 6)},
}

# A range spec is meant to remove a handful of stray codes. If it ever removes
# more than this, the spec is wrong about the encoding rather than the data
# being that bad, and silently deleting the scale would be the worst outcome.
MAX_DROPPED_FRACTION = 0.01


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"ie16": "ei16", **COV_RENAME})
    df["id"] = df.index
    return df


def drop_out_of_range(long, out_name):
    """Remove responses outside their own item's printed options."""
    spec = VALID_RANGE[out_name]
    lo = long["item"].map(lambda i: spec.get(i, spec.get("*"))[0])
    hi = long["item"].map(lambda i: spec.get(i, spec.get("*"))[1])
    keep = long["resp"].between(lo, hi)
    if not keep.all():
        gone = long.loc[~keep].groupby(["item", "resp"]).size()
        print(f"  {out_name}: dropped {int((~keep).sum())} out-of-range response(s): "
              + ", ".join(f"{i}={r} x{n}" for (i, r), n in gone.items()))
        frac = (~keep).sum() / len(long)
        assert frac <= MAX_DROPPED_FRACTION, (
            f"{out_name}: {frac:.1%} of responses are outside their item's "
            f"printed options -- check VALID_RANGE against the instrument "
            f"before assuming the data is at fault")
    return long.loc[keep].reset_index(drop=True)


def melt_scale(df, cov_cols, item_cols, out_name):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = drop_out_of_range(long, out_name)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    for out_name, item_cols in SCALES.items():
        melt_scale(df, cov_cols, item_cols, out_name)
    melt_scale(df, cov_cols, [f"ei{i}" for i in range(1, 17)], "extremera_2016_ei")


if __name__ == "__main__":
    convert()
