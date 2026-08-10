from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0152479
# DOI: 10.1371/journal.pone.0152479
# Janoff-Bulman & Carnes (2016), "Social Justice and Social Order: Binding
# Moralities across the Political Spectrum". CC BY 4.0.
#
# S1 File (Study 1, N=311) and S2 File (Study 2, N=295) both contain the
# 30-item Model of Moral Motives (MMM) Scale: 6 subscales (proscriptive/
# prescriptive x self/other/group -- column prefixes SPRO/SPRE/OPRO/OPRE/
# GPRO/GPRE), 5 items each, all rated on the paper's stated 7-point scale
# (1=strongly disagree, 7=strongly agree). Verified 1-7 integer, no NaNs,
# id column unique==nrows in both files.
#
# Kept as two SEPARATE output tables rather than merged: the paper's Study 2
# Methods text does not state the MMM administration was "identical to
# Study 1" (no such confirming language found), so per datastandard.md's
# multi-sample-merge rule they are not combined.
#
# S3 File (Study 3) is excluded entirely -- it is country-level aggregate
# data (Country, Tight, GDPPC, etc., N=32 countries), not individual item
# responses, and is out of scope for this table.
#
# Excluded from items: Restraint5i/Reliance5i/NoHarm5i/Helping5i/Order5i/
# Justice5i (5-item subscale composite means, continuous, non-integer --
# aggregate scores per datastandard.md, not raw resp) and MC_* (standardized
# manipulation-check indices, Study 1 only) and Catch1/Catch2 (attention-
# check items, Study 2 only, constant zero -- no variance, not real items).
#
# Covariates kept: cov_female (0/1), cov_age. In Study 2's Age column, two
# clear data-entry errors (6 and 1983, the latter almost certainly a birth
# year typed into an age field) were set to NaN and dropped from the
# covariate only (rows/responses retained).
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

STUDIES = [
    ("study1", "https://journals.plos.org/plosone/article/file"
               "?type=supplementary&id=10.1371/journal.pone.0152479.s001",
     "janoffbulman_2016_moralmotives_s1"),
    ("study2", "https://journals.plos.org/plosone/article/file"
               "?type=supplementary&id=10.1371/journal.pone.0152479.s002",
     "janoffbulman_2016_moralmotives_s2"),
]

ITEM_PREFIXES = ("SPRO_", "SPRE_", "OPRO_", "OPRE_", "GPRO_", "GPRE_")


def _process_one(url: str, out_name: str) -> None:
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    df, meta = pyreadstat.read_sav(io.BytesIO(r.content))

    item_cols = [c for c in df.columns if c.startswith(ITEM_PREFIXES)]

    df = df.rename(columns={"ID": "id", "Female": "cov_female", "Age": "cov_age"})
    # Two isolated data-entry errors in Study 2's Age field (6, 1983) --
    # covariate only, not part of resp.
    df.loc[(df["cov_age"] < 15) | (df["cov_age"] > 100), "cov_age"] = float("nan")

    cov_cols = [c for c in ["cov_female", "cov_age"] if c in df.columns]

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp", "id"]).reset_index(drop=True)
    long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    for _, url, out_name in STUDIES:
        _process_one(url, out_name)


if __name__ == "__main__":
    convert()
