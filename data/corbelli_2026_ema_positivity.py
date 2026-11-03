#!/usr/bin/env python3
# Source: https://zenodo.org/records/21970195
# DOI: 10.5281/zenodo.21970195 (dataset). Paper: Corbelli, G., Zambelli, M.,
#   Zasso, S., Di Brango, N., Lopez-Perez, B., & Zuffiano, A. (2026). Modeling
#   intensive longitudinal data: A tutorial comparing dynamic structural
#   equation modeling and psychometric network analysis. Behavior Research
#   Methods (the deposit README names the journal; no article DOI is given).
# Deposit: Corbelli, G. (2026). [Data set and code]. Zenodo.
# Data: ema_positivity.rds (one data frame, 11,176 rows x 14 columns: ID, EMA,
#   DAY, H4, BEEP, age, gender + 7 momentary items), read with pyreadr.
#   sha256 660c26513424bbe84040a6292ce607fa2e6b263d9bfd034277c28d1764ba9f34
# Codebook: none as a file. The README lists the deposit; the item names and
#   the design ("166 adults three times daily for 28 days") come from the
#   Zenodo description and reproducible_code.Rmd.
# License: CC BY 4.0 (resolved from the Zenodo record's metadata, cc-by-4.0)
#
# Real data, not simulated: the README gives the ethics approval (Liverpool
# Hope University, S14-01-2019 NF001) and the British Academy/Leverhulme grant
# (SRG18R1\181444) the data were collected under.
#
# Found by the repos monthly sweep of 2026-11-02 (recoverable_format).
#
# Design: 166 adults, ecological momentary assessment three times a day for 28
#   days (84 scheduled prompts). The file holds only answered prompts (11,176;
#   15-84 per person, median 70) and every item is answered on every one, so
#   there are no all-missing rows to drop.
#   `wave` = the source EMA column, the scheduled prompt number 1..84; asserted
#   equal to (DAY - 1) * 3 + BEEP. Missed prompts leave gaps in `wave`.
#   No `date`: the deposit has no timestamps. H4 (an index that tracks 2*EMA
#   to within +-1) is a schedule index, not a clock time, and is not carried.
#
# ONE output table, the whole momentary questionnaire, as the ESM precedents
#   do (dejonckheere_2018_esm_affect):
#   corbelli_2026_ema_positivity  7 items, 1-5:
#     ls     life satisfaction  } the three "facets of positivity" the paper
#     se     self-esteem        } models (single items, one per facet)
#     opt    optimism           }
#     happy, calm               positive affect
#     angry, sad                negative affect
#   Item codes are the source column names, lower-cased.
#   Response anchors are NOT documented in the deposit; every item uses all of
#   1-5 and nothing else, so 1-5 is shipped as recorded. Negative-affect items
#   are not reversed.
#
# Plausibility check (2026-11-02, after other deposits in this batch looked
#   generated): pooled r is positive among the five positive items (.48-.87,
#   LS-OPT .87) and between angry and sad (.54), and negative across the two
#   groups (-.21 to -.48); person-mean correlations show the same pattern. No
#   duplicated (ID, EMA) rows. Read as real EMA data.
#
# Covariates:
#   cov_age     the source gives age as fractional years to nine decimals
#               (e.g. 38.735113), i.e. days of age, which is close to a date of
#               birth. COARSENED to whole years (floor), which datastandard
#               permits; the finer value is not carried.
#   cov_gender  carried as the source's 0/1 code. The coding is NOT documented
#               in the deposit (the knitted output reports 45 zeros and 121
#               ones, 72.9% ones); it is not relabelled.
#
# Item text: NOT shipped -- not in hand. The deposit gives item names only
#   (LS, SE, OPT, ANGRY, SAD, HAPPY, CALM); the stems would be in the BRM
#   article's Method section.
#
# PII: none. No text columns other than the categorical ID (asserted below);
#   no names, emails, dates or locations. Age coarsened as above.

import hashlib
import os
import sys
import urllib.request

import numpy as np
import pandas as pd
import pyreadr

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
TABLE = "corbelli_2026_ema_positivity"
FILE = "ema_positivity.rds"
SHA256 = "660c26513424bbe84040a6292ce607fa2e6b263d9bfd034277c28d1764ba9f34"
ITEMS = ["LS", "SE", "OPT", "HAPPY", "CALM", "ANGRY", "SAD"]
SCALE = [1, 2, 3, 4, 5]


def _raw():
    """CORBELLI_RAW_DIR, else fetch into raw_cache with a sha256 check."""
    d = os.environ.get("CORBELLI_RAW_DIR")
    if not d:
        d = os.path.join(REPO_ROOT, "automated_finding", "runs", "raw_cache",
                         "corbelli_2026")
    os.makedirs(d, exist_ok=True)
    dest = os.path.join(d, FILE)
    if not os.path.exists(dest):
        url = f"https://zenodo.org/api/records/21970195/files/{FILE}/content"
        req = urllib.request.Request(
            url, headers={"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"})
        with urllib.request.urlopen(req, timeout=300) as r:
            blob = r.read()
        with open(dest, "wb") as fh:
            fh.write(blob)
    with open(dest, "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == SHA256, f"{FILE} changed"
    return dest


def convert():
    df = list(pyreadr.read_r(_raw()).values())[0]
    assert df.shape == (11176, 14), df.shape
    assert list(df.columns) == ["ID", "EMA", "DAY", "H4", "BEEP", "age",
                                "gender"] + ["ANGRY", "SAD", "HAPPY", "CALM",
                                             "LS", "SE", "OPT"], list(df.columns)
    df["ID"] = df["ID"].astype(str)
    assert df["ID"].nunique() == 166
    assert ((df["DAY"] - 1) * 3 + df["BEEP"] == df["EMA"]).all()
    assert not df.duplicated(["ID", "EMA"]).any()
    assert df[ITEMS].notna().all().all()
    assert df.groupby("ID")[["age", "gender"]].nunique().max().max() == 1
    assert set(df["gender"].unique()) == {0.0, 1.0}

    df["id"] = df["ID"].astype(int)
    df["wave"] = df["EMA"].astype(int)
    df["cov_age"] = np.floor(df["age"]).astype("Int64")
    df["cov_gender"] = df["gender"].astype("Int64")
    ren = {c: c.lower() for c in ITEMS}
    df = df.rename(columns=ren)
    items = list(ren.values())
    covs = ["cov_age", "cov_gender"]

    long = df.melt(id_vars=["id", "wave"] + covs, value_vars=items,
                   var_name="item", value_name="resp")
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "wave"] + covs]
    long = long.sort_values(["id", "wave", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item", "wave"]).any()
    assert set(long["resp"]) == set(SCALE)
    assert long["id"].nunique() >= 100

    checks = run_qc(long, permitted_values={i: SCALE for i in items})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {TABLE} {c.name}: {c.detail[:180]}")

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} waves={long['wave'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
