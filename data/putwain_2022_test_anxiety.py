#!/usr/bin/env python3

# Source: https://data.mendeley.com/datasets/6bhr52dc5v/2
# DOI: 10.17632/6bhr52dc5v.2
#   Putwain, D. (2022). Test Anxiety, Wellbeing, Buoyancy, Adaptability, and
#   Mental Health Risk [Dataset]. Mendeley Data.
# Data: the deposit's single .sav -- 1,198 English students aged 16-19,
#   measured twice: the unprefixed columns are time 1 and the `T2`-prefixed
#   ones are the same items at time 2.
# License: CC BY 4.0 (verified on the Mendeley record and DataCite, 2026-10-19).
# Item text: NOT shipped here, but it is fully in hand -- every item's
#   administered English stem is its SPSS variable label ("Before an exam, I am
#   worried I will fail.") and every block carries value labels for its
#   anchors. None of the four instruments has a rights-register row, so this
#   deposit is a strong candidate for a later text pass; it is left out only
#   because this slice is response tables.
#
# FOUR tables, two waves each (wave 1 = the unprefixed columns, wave 2 = the
#   T2 ones; the item name carries no wave, so one item links across both):
#   putwain_2022_test_anxiety  16 items, 1-5  (MTAS)
#   putwain_2022_buoyancy       4 items, 1-5
#   putwain_2022_wellbeing      6 items, 1-5
#   putwain_2022_adaptability   9 items, 1-5
#
# THE FIFTH BLOCK IS DEFERRED, and the deposit's own value labels are what
#   condemn it. The 20 `S*` / `T2S*` items ("I argue with others.") carry value
#   labels 0=Never, 1=Sometimes, 2=Often, 3=Almost Always -- a FOUR-category
#   scale. At time 1 the observed values are 1-4, i.e. the same four categories
#   stored one higher than the labels. At time 2 they are 0-4, five distinct
#   values, and **184 of 1,093 respondents use both 0 and 4 within the same
#   20 items**, so time 2 is not one coding shifted either: it mixes them
#   within respondents. An item whose value means a different category for
#   different people cannot ship, so the block is recorded in the batch's
#   leads file instead of guessed at.
#
# NOT SHIPPED besides that: the three `T2*MISSING` flags, which are the
#   deposit's own bookkeeping for wave-2 non-response.
#
# id: the row index, kept so the two waves link within a respondent.
# Covariates: cov_school, cov_gender, cov_age, cov_ethnicity -- the deposit's
#   own codes, time-invariant; gender, age and ethnicity are missing for 24,
#   21 and 29 respondents respectively.
import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "group2_t1" / "6bhr52dc5v" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATASET = "6bhr52dc5v"
FNAME = "Test Anxiety, Wellbeing, Buoyancy, Adaptability, and Mental Health Risk.sav"
COVS = {"School": "cov_school", "Gender": "cov_gender", "Age": "cov_age",
        "Ethnicity": "cov_ethnicity"}
SCALE = set(range(1, 6))
TABLES = {"putwain_2022_test_anxiety": ("MTAS", 16),
          "putwain_2022_buoyancy": ("B", 4),
          "putwain_2022_wellbeing": ("W", 6),
          "putwain_2022_adaptability": ("A", 9)}
DEFERRED_PREFIX, DEFERRED_N = "S", 20


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get("https://data.mendeley.com/public-api/datasets/"
                         f"{DATASET}", headers=UA, timeout=120).json()
        url = [f["content_details"]["download_url"] for f in j["files"]
               if f["filename"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    labels = meta.column_names_to_labels
    assert len(df) == 1198, len(df)

    # Assert the deferred block's defect rather than describing it from memory.
    s_t1 = [f"{DEFERRED_PREFIX}{i}" for i in range(1, DEFERRED_N + 1)]
    s_t2 = [f"T2{DEFERRED_PREFIX}{i}" for i in range(1, DEFERRED_N + 1)]
    assert set(meta.variable_value_labels.get(s_t1[0], {})) == {0, 1, 2, 3}, \
        "the S block's value labels are no longer the four 0-3 categories"
    assert set(pd.to_numeric(df[s_t1].stack()).dropna().unique()) <= {1, 2, 3, 4}
    sub = df[s_t2].dropna(how="all")
    both = ((sub == 0).any(axis=1) & (sub == 4).any(axis=1)).sum()
    assert both > 0, "the T2 mixed-coding defect is gone; re-check the block"
    print(f"deferred: the {DEFERRED_N}-item {DEFERRED_PREFIX}* block -- labels "
          f"say 0-3, wave 1 holds 1-4, wave 2 holds 0-4 and {int(both)} of "
          f"{len(sub)} respondents use both 0 and 4 in it")

    df = df.rename(columns=COVS)
    df["id"] = range(1, len(df) + 1)
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov], errors="coerce")
        assert (v.dropna() % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (prefix, n) in TABLES.items():
        frames = []
        for wave, pre in ((1, ""), (2, "T2")):
            cols = [f"{pre}{prefix}{i}" for i in range(1, n + 1)]
            missing = [c for c in cols if c not in df.columns]
            assert not missing, (name, wave, missing)
            for c in cols:        # the stem is the label, in both waves
                assert len((labels.get(c) or "").strip()) > 8, (c, labels.get(c))
            part = (df[["id", *cov_cols, *cols]]
                    .melt(id_vars=["id", *cov_cols], value_vars=cols,
                          var_name="item", value_name="resp")
                    .dropna(subset=["resp"]))
            if pre:
                part["item"] = part["item"].str.removeprefix(pre)
            part["wave"] = wave
            frames.append(part)
        t = pd.concat(frames, ignore_index=True)
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the labelled 1-5 scale: {bad}"
        t = t[["id", "item", "resp", "wave", *cov_cols]]
        assert not t.duplicated(["id", "item", "wave"]).any(), name
        assert t["item"].nunique() == n and set(t["wave"]) == {1, 2}
        assert t["id"].nunique() >= 100, (name, t["id"].nunique())
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:130]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} waves={t['wave'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
