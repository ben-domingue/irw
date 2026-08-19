#!/usr/bin/env python3
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/GNUL8E
# DOI (data): 10.7910/DVN/GNUL8E
# DOI (paper): 10.1093/qje/qjaa011
#
# Caplin, Csaba, Leahy & Nov (2020), "Rational Inattention, Competitive
# Supply, and Psychometrics", Quarterly Journal of Economics 135(3),
# 1681-1724. CC0 1.0. Replication data for a perceptual-decision
# experiment: 814 participants (usercode) each completed a fixed 40-round
# task judging which of several polygon shapes appeared most often in a
# briefly-shown display, under randomized monetary-incentive levels.
# `Round` (1-40) is a consistent trial-position index across every
# participant, so it's used as the item id even though the specific
# shape/incentive configuration for a given round number was randomized
# independently per participant (confirmed: `Incentives` and shape counts
# both vary across users at a fixed `Round`) -- it identifies trial
# position, not a shared stimulus, the same way trial number is commonly
# used as an item id in other repeated-trial perceptual/cognitive-task
# datasets in this warehouse.
#
# `Correct` (already 0/1) is the raw per-round response. `time_round` is
# confirmed to already be in seconds: summed per participant it equals
# `total time (min) * 60` exactly for all 814 users, so it's used as `rt`
# with no unit conversion. `date/time` (session start, constant per
# participant) is parsed to Unix seconds.
#
# Dropped as not fitting the schema: `Score` (a cumulative running total
# across rounds -- a composite, not a raw response), `BonusResult` and
# `Clock Stop Digits` (derived/ambiguous, not raw responses), and the
# per-round stimulus-design columns (`Incentives`, `Decoys/*`,
# `non-decoys/*`, `Number of Shape/*`, `Round Mudding/*`, `m`, `max`,
# `mudding`, `n`) -- these vary at the person-round level (not constant
# per item), so they don't fit either `cov_*` (person-invariant) or
# `itemcov_*` (item-invariant), and there's no standard response-level
# column for them. `N` and `TotalRound` are constant across the whole
# file (24 and 40 respectively) and carry no information.
#
# No PII: `usercode` is an anonymized hash, no names/emails/GPS present.

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

FILE_URL = "https://dataverse.harvard.edu/api/access/datafile/3790830"
MEMBER = "data/experimental_data.csv"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch_data() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        with zf.open(MEMBER) as f:
            return pd.read_csv(f)


def convert():
    df = fetch_data()

    df = df.rename(columns={
        "usercode": "id",
        "Correct": "resp",
        "Round": "item",
        "time_round": "rt",
        "age": "cov_age",
        "sex": "cov_sex",
    })

    df["item"] = df["item"].astype(int).map(lambda n: f"round_{n:02d}")
    df["resp"] = pd.to_numeric(df["resp"], errors="coerce")
    df["rt"] = pd.to_numeric(df["rt"], errors="coerce")
    df["date"] = (
        pd.to_datetime(df["date/time"], format="%d/%m/%Y - %H:%M:%S", errors="coerce")
        .astype("int64") // 10**9
    )

    long = df[["id", "item", "resp", "rt", "date", "cov_age", "cov_sex"]].copy()
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "caplin_2020_rational_inattention.csv"
    long.to_csv(out_path, index=False)
    print(f"caplin_2020_rational_inattention.csv: rows={len(long)} "
          f"ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
