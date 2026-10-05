#!/usr/bin/env python3
"""Dora et al. (2024), momentary self-control demands and next-morning alcohol
consequences in two experience sampling studies of college drinkers, via the
openESM harmonised copy.

Source: https://zenodo.org/records/22809550 (openESM 0023_dora)
DOI: 10.5281/zenodo.22809550
Original deposit: https://osf.io/rh2sw/ (OSF, CC BY 4.0;
    Data/bayes.ema.tutorial.data.csv)
Paper: Dora J, McCabe CJ, van Lissa CJ, Witkiewitz K, King KM (2024). A Tutorial
    on Analyzing Ecological Momentary Assessment Data in Psychological Research
    With Bayesian (Generalized) Mixed-Effects Models. Advances in Methods and
    Practices in Psychological Science 7(1). doi:10.1177/25152459241235875
    (preprint doi:10.31234/osf.io/jc938). The data were collected in two
    earlier studies (Witkiewitz et al. 2012; Smith et al. 2022).
Data: 0023_dora_ts.tsv (responses); bayes.ema.tutorial.data.csv from OSF
    (https://osf.io/download/chb5m/) for the person-level covariates, which
    openESM does not ship
License: CC BY 4.0 (openESM copy and OSF deposit)
Item text: not shipped. The paper describes the items ("to what extent they
    needed to control or fix their mood ...") but does not quote them, and no
    codebook is deposited.

213 undergraduates in two studies: study 1 (127 people, up to 14 days x 5
signals) and study 2 (86 people, up to 22 days x 3 signals). Same items in
both; ids do not overlap.

Tables written
--------------
dora_2024_selfcontrol_demands    4 items, every signal, 0 ("not at all") to
                                 100 ("very much"): needed to control or fix
                                 one's mood, control or fix one's thoughts,
                                 deal with anything stressful; felt
                                 overwhelmed (adapted from Muraven et al. 2005)
dora_2024_alcohol_consequences   4 yes/no items, reported after a drinking
                                 night: hangover, vomit (nausea from
                                 drinking), blackout (failing to remember
                                 events), hurt (intoxication-related injury)

Coding notes
------------
* dora_2024_selfcontrol_demands: `wave` is each person's survey number in
  time order. There are no timestamps, so surveys are ordered on (day,
  signal), ties broken by file order. File order agrees with (day, signal)
  for 99.8% of consecutive rows within person.
* dora_2024_alcohol_consequences: one report per person-day, and `wave` is
  the study day. The consequences describe the previous night and were asked
  once a day, but study 1 copies each day's answers onto every signal of
  that day (identical in all 740 person-days with more than one row);
  shipping them per signal would repeat each answer up to five times. Study
  2 has one report per day except 3 person-days with two: 2 identical
  (collapsed), 1 conflicting (dropped). The two tables' waves therefore
  index different things -- surveys and days -- and do not join.
* Ties: in study 2, 439 pairs of surveys share person, day and signal, in the
  openESM copy and the OSF original alike, with different responses. In 431
  pairs (429 at signal 1, 2 at signal 3) the first row in file order carries
  the consequence items -- the morning report -- and the second does not;
  those are kept in file order, morning report first. In the other 8 pairs
  (2 at signal 1, 6 at signal 2) neither row has consequence items, so
  nothing orders them, and their 16 surveys are dropped.
* 748 study-2 rows have no day or signal and hold only a drink count; they
  carry no item responses and are dropped.
* `cov_study` (study1/study2) is the source study. cov_gender, cov_age and
  cov_ddq_typical_drinks ("typical amount of drinks consumed per week
  computed from DDQ", per the OSF R code) come from the OSF file, joined on
  id; constant within person.

Columns not shipped
-------------------
alc_drinks    Drink count the previous day (0 to 30+), a count rather than an
              item response.
alc_intox     Single-item intoxication rating (0-6); one item is not a scale.
alc_onset     Hour drinking began.
day, beep, hour  Folded into `wave`; hour of submission only, no date.
"""

import os
import sys

import pandas as pd
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

REC = "22809550"
TS_FILE = "0023_dora_ts.tsv"
OSF_URL = "https://osf.io/download/chb5m/"
AF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                  "automated_finding")
OUTDIR = os.path.join(AF, "irw_output")
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

TABLES = {
    "dora_2024_selfcontrol_demands": (
        ["control_fixmood", "control_fixthought", "dealt_stress",
         "felt_overwhelm"], range(0, 101), 185),
    "dora_2024_alcohol_consequences": (
        ["alc_hangover", "alc_vomit", "alc_blackout", "alc_hurt"],
        range(0, 2), 213),
}
COVS = ["cov_study", "cov_gender", "cov_age", "cov_ddq_typical_drinks"]


def fetch(url, path):
    if not os.path.exists(path):
        r = requests.get(url, headers=HEADERS, timeout=600)
        r.raise_for_status()
        with open(path, "wb") as fh:
            fh.write(r.content)
    return path


def load():
    path = os.path.join("/tmp", f"zenodo_{REC}_{TS_FILE}")
    if not os.path.exists(path):
        api = requests.get(f"https://zenodo.org/api/records/{REC}",
                           headers=HEADERS, timeout=60).json()
        url = next(f["links"]["self"] for f in api["files"]
                   if f["key"] == TS_FILE)
        fetch(url, path)
    df = pd.read_csv(path, sep="\t")
    osf = pd.read_csv(fetch(OSF_URL, "/tmp/osf_rh2sw_tutorial_data.csv"),
                      dtype={"PID": str})
    return df, osf


def covariates(osf):
    # openESM stores ids as integers, dropping the leading zeros of the OSF
    # PIDs; the integer form is collision-free (213 -> 213)
    osf["id"] = osf["PID"].astype("int64")
    assert osf.groupby("PID")["id"].nunique().eq(1).all()
    assert osf["id"].nunique() == osf["PID"].nunique() == 213
    cols = {"study": "cov_study", "gender": "cov_gender", "age": "cov_age",
            "DDQ.typ.drinks": "cov_ddq_typical_drinks"}
    per = osf.groupby("id")[list(cols)].nunique(dropna=True)
    assert (per <= 1).all().all()
    cov = osf.groupby("id")[list(cols)].first().reset_index().rename(
        columns=cols)
    assert cov["cov_gender"].isin(
        ["female", "male", "other", "genderqueer"]).all()
    return cov


def daily(df, cols):
    """One consequences report per person-day; wave = study day."""
    rows = df[df[cols].notna().any(axis=1)]
    per_day = rows.groupby(["id", "day"])[cols]
    s1 = rows["study"] == "study1"
    assert (rows[s1].groupby(["id", "day"])[cols].nunique() <= 1).all().all()
    conflict = (per_day.nunique() > 1).any(axis=1)
    assert conflict.sum() == 1
    rows = rows.set_index(["id", "day"]).drop(conflict[conflict].index)
    # first non-missing value per item; values agree within the day
    rows = rows.groupby(["id", "day"])[cols + COVS].first().reset_index()
    assert len(rows) == 752 + 1731 - 1
    return rows.assign(wave=rows["day"].astype(int))


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    df, osf = load()
    assert len(df) == 9366 and df["id"].nunique() == 213, df.shape
    items = [i for cols, _, _ in TABLES.values() for i in cols]

    df["row"] = range(len(df))
    n = len(df)
    noday = df["day"].isna()
    assert not df.loc[noday, items].notna().any().any()
    assert (noday & (df["study"] == "study2")).sum() == noday.sum() == 748
    df = df[~noday]
    assert n - len(df) == 748

    key = ["id", "day", "beep"]
    tied = df.duplicated(key, keep=False)
    assert (df.loc[tied, "study"] == "study2").all()
    pairs = df[tied].groupby(key)
    assert pairs.ngroups == 439 and (pairs.size() == 2).all()
    # a pair is ordered when exactly one row is the morning report (has
    # consequence items) and it comes first in file order
    cons = TABLES["dora_2024_alcohol_consequences"][0]
    pairs = df[tied].sort_values("row").assign(
        has_cons=lambda x: x[cons].notna().any(axis=1).map({True: "C",
                                                            False: "-"}))
    pattern = pairs.groupby(key)["has_cons"].transform("".join)
    assert pattern.groupby([pairs[c] for c in key]).first().value_counts() \
        .to_dict() == {"C-": 431, "--": 8}
    unordered = pairs[pattern == "--"]
    assert len(unordered) == 16
    df = df.drop(unordered.index)

    cov = covariates(osf)
    df = df.merge(cov, on="id", how="left", validate="many_to_one")
    assert (df["cov_study"] == df["study"]).all()

    for table, (cols, scale, n_people) in TABLES.items():
        if table == "dora_2024_alcohol_consequences":
            rows = daily(df, cols)
        else:
            rows = df[df[cols].notna().any(axis=1)]
            rows = rows.sort_values(["id", "day", "beep", "row"],
                                    kind="stable")
            rows = rows.assign(wave=rows.groupby("id").cumcount() + 1)
        long = rows.melt(id_vars=["id", "wave"] + COVS, value_vars=cols,
                         var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp", "wave"] + COVS]
        long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)

        assert long["resp"].between(scale[0], scale[-1]).all(), table
        assert long["id"].nunique() == n_people, (table,
                                                  long["id"].nunique())
        assert not long.duplicated(["id", "item", "wave"]).any()
        bad = [c for c in run_qc(long) if c.status == "fail"]
        assert not bad, (table, [(c.name, c.detail) for c in bad])

        path = os.path.join(OUTDIR, f"{table}.csv")
        long.to_csv(path, index=False)
        print(f"{path}: {long['id'].nunique()} people x "
              f"{long['item'].nunique()} items = {len(long):,} responses, "
              f"max wave {long['wave'].max()}")


if __name__ == "__main__":
    main()
