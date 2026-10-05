#!/usr/bin/env python3
"""Bringmann et al. (2013), momentary mood in an experience sampling study
nested in a randomised trial of mindfulness-based cognitive therapy, via the
openESM harmonised copy.

Source: https://zenodo.org/records/17347474 (openESM 0010_geschwind)
DOI: 10.5281/zenodo.17347474
Original deposit: PLOS ONE supporting information S4,
    doi:10.1371/journal.pone.0060188.s004 (CC BY 4.0, as is the article)
Paper: Bringmann LF, Vissers N, Wichers M, Geschwind N, Kuppens P, Peeters F,
    Borsboom D, Tuerlinckx F (2013). A Network Approach to Psychopathology: New
    Insights into Clinical Longitudinal Data. PLOS ONE 8(4), e60188.
    doi:10.1371/journal.pone.0060188
Data: 0010_geschwind_ts.tsv, 0010_geschwind_static.tsv
License: CC BY 4.0 for the original; openESM lists its copy as CC BY-NC 4.0.
    The table carries the NC terms (datastandard.md, "Before you start").
Item text: not shipped. The paper gives English glosses of the items ("I feel
    cheerful", "I am worrying at the moment", ...) but neither the Dutch wording
    participants saw nor the scale anchors, and openESM ships no codebook for
    this record.

openESM names the record after Geschwind, whose MBCT trial (Geschwind et al.
2011) collected the data; the deposit is the supplement of Bringmann et al.,
so the table is named for that paper.

129 residual-depression patients, ten semi-random beeps a day in two six-day
periods: a baseline, and a second period 2-3 months later after randomisation
to mindfulness-based cognitive therapy (n = 63) or a waiting list (n = 66). Six
items, all 7-point: cheerful, relaxed, worried, fearful, sad (1..7) and the
pleasantness of the most important event since the previous beep (-3..+3).

Coding notes
------------
* `wave` = study_period * 100 + (day - 1) * 10 + beep: 1..100 for the
  baseline period, 101..200 for the second. There is no timestamp, so the
  schedule position is the only time information, as in
  dejonckheere_2018_esm_affect. Most people stop after six days; the 160
  answered prompts on days 7-10 are kept, since their position is known.
* `treat` = therapy (1 = MBCT, 0 = waiting list), from the static file. It is
  the randomised group, so it is constant within person across both periods,
  including the baseline before therapy began; `wave` separates the periods.
  63 MBCT / 66 waiting list, as in the paper.
* Every person-period-day has an 11th row with no beep number. 2,558 of these
  2,600 rows are empty; the other 42 (14 people) are almost all worried = 1
  and nothing else. Without a beep they cannot be placed in time, so all 2,600
  are dropped.
* pleasantness holds one -4 (id 10853, period 1, day 1, beep 9) on a -3..+3
  scale, present in the original S4 file too. That single response is
  dropped as a data-entry error; the person's other five items at that beep
  are kept.
* 434 prompts are partly answered; the missing items are dropped per item in
  the melt.

Columns not shipped
-------------------
day, beep, study_period  Folded into `wave`.
neuroticism   Per-person neuroticism scale score from the static file. A
              composite, not a response or a background covariate; the
              item-level data are not in the deposit.
"""

import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

REC = "17347474"
TS_FILE = "0010_geschwind_ts.tsv"
STATIC_FILE = "0010_geschwind_static.tsv"
TABLE = "bringmann_2013_esm_mood"
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# item -> allowed range
ITEMS = {
    "cheerful": range(1, 8),
    "relaxed": range(1, 8),
    "worried": range(1, 8),
    "fearful": range(1, 8),
    "sad": range(1, 8),
    "pleasantness": range(-3, 4),
}


def load(filename):
    path = os.path.join("/tmp", f"zenodo_{REC}_{filename}")
    if not os.path.exists(path):
        api = requests.get(f"https://zenodo.org/api/records/{REC}",
                           headers=HEADERS, timeout=60).json()
        url = next(f["links"]["self"] for f in api["files"]
                   if f["key"] == filename)
        r = requests.get(url, headers=HEADERS, timeout=600)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return pd.read_csv(path, sep="\t")


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    df = load(TS_FILE)
    static = load(STATIC_FILE)
    assert len(df) == 28600 and df["id"].nunique() == 130, df.shape
    assert (df.groupby("id").size() == 220).all()

    items = list(ITEMS)
    n = len(df)
    nobeep = df["beep"].isna()
    assert nobeep.sum() == 2600
    assert df.loc[nobeep, items].notna().any(axis=1).sum() == 42
    df = df[~nobeep].copy()
    assert n - len(df) == 2600
    assert not df.duplicated(["id", "study_period", "day", "beep"]).any()
    assert df["beep"].between(1, 10).all() and df["day"].between(1, 10).all()

    df["wave"] = (df["study_period"] * 100 + (df["day"] - 1) * 10
                  + df["beep"]).astype(int)

    # therapy: one non-missing value per person (the static file has a blank
    # row per id as well)
    static = static.dropna(subset=["therapy"])
    assert not static["id"].duplicated().any()
    assert static["therapy"].value_counts().to_dict() == {0: 66, 1: 63}
    df = df.merge(static[["id", "therapy"]], on="id", how="left",
                  validate="many_to_one")
    df = df.rename(columns={"therapy": "treat"})

    long = df.melt(id_vars=["id", "wave", "treat"], value_vars=items,
                   var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    bad_pleas = (long["item"] == "pleasantness") & (long["resp"] == -4)
    assert bad_pleas.sum() == 1
    long = long[~bad_pleas]

    assert long["treat"].notna().all()
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    long["treat"] = long["treat"].astype(int)
    long = long[["id", "item", "resp", "wave", "treat"]]
    long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)

    for item, scale in ITEMS.items():
        r = long.loc[long["item"] == item, "resp"]
        assert r.between(scale[0], scale[-1]).all(), item
    assert long["id"].nunique() == 129
    assert not long.duplicated(["id", "item", "wave"]).any()
    assert (long.groupby("id")["treat"].nunique() == 1).all()
    bad = [c for c in run_qc(long) if c.status == "fail"]
    assert not bad, [(c.name, c.detail) for c in bad]

    path = os.path.join(OUTDIR, f"{TABLE}.csv")
    long.to_csv(path, index=False)
    print(f"{path}: {long['id'].nunique()} people x {long['item'].nunique()} "
          f"items = {len(long):,} responses, max wave {long['wave'].max()}")


if __name__ == "__main__":
    main()
