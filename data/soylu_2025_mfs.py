#!/usr/bin/env python3
# Source: https://zenodo.org/records/17761951
# DOI: 10.3390/brainsci16010074
#   Soylu, Y., Fortes, L. S., Arslan, E., Jahrami, H. et al. (2026). "The
#   Cross-Cultural Adaptation, Validation and Psychometric Properties of the
#   Mental Fatigue Scale in Turkish Athletes." Brain Sciences 16(1), 74.
#   (PMC12839050)
# Data: Zenodo 17761951, MF_ZENODO.xlsx, two sheets: "Adults" (204 rows x
#       24 columns) and "Adolescents" (287 x 24). Same 15 MF_ items and the
#       same covariates on both sheets (the time-of-day questions are headed
#       in Turkish on one sheet, English on the other).
# License: CC BY 4.0 (Zenodo record metadata).
#
# Item text: not shipped. A spreadsheet: no variable labels (headers are the
#   positional MF_1..MF_15) and no value labels. The Turkish stems are not in
#   the deposit; the MFS wording is in Johansson & Ronnback's MFS and the
#   paper's adaptation.
#
# Table: soylu_2025_mfs, 15 items (MF_1 .. MF_15, the source column names),
#   Mental Fatigue Scale (Johansson et al.), Turkish. Paper: each item rated
#   0-3 (0 normal function .. 3 maximum symptoms) and "half-point ratings
#   (0.5, 1.5, and 2.5) were permitted", so the permitted set is
#   {0, 0.5, ..., 3} and resp is kept as a float. The halves are answers,
#   not imputations. MF_15 (diurnal variation) is descriptive and not summed
#   into the total, but it is an administered item on the same form, so it
#   ships (observed 0-2, inside the documented set).
#   Both sheets carry the same instrument and response format, so they ship
#   as one table with cov_study.
#
# Cleaning (duplicate respondents):
#   - Adults: 9 pairs of rows agree on age, height, weight, sport, national
#     status, both time-of-day answers and all 15 items, and differ only in
#     athletic experience (by 3-10 years; a later row 10 years higher in
#     most pairs). These are copies, not people. The later row is dropped
#     (asserted) -> 195 adults.
#   - Adolescents: 1 row is an exact copy of the row before it -> dropped.
#   - 3 eighteen-year-olds appear on both sheets with the same height,
#     weight, sport and items -> the adolescent-sheet copy is dropped
#     -> 283 adolescents.
#   The paper's 204 + 287 = 491 counts these copies.
#   Gender is reported in the paper but is not in the file.
#
# Dropped: nothing else; BMI is kept as a covariate (it equals
#   weight / height^2, asserted).
# id: row index over adults then adolescents (the file has no respondent id).
# Covariates: cov_study (adult / adolescent), cov_age, cov_height_cm,
#   cov_weight_kg, cov_bmi, cov_experience_years, cov_sport (as entered,
#   whitespace stripped; spellings vary), cov_national_athlete (1 yes,
#   0 no), cov_best_time, cov_worst_time ("When do you feel at your
#   best/worst?": Morning/Afternoon/Evening/Night).

import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/17761951/files/MF_ZENODO.xlsx/content"
TABLE = "soylu_2025_mfs"

ITEMS = [f"MF_{i}" for i in range(1, 16)]
PERMITTED = {x / 2 for x in range(0, 7)}
COVS_ADULT = {"Age": "cov_age", "Height": "cov_height_cm",
              "Weight": "cov_weight_kg", "BM": "cov_bmi",
              "Athlete Experience (year)": "cov_experience_years",
              "Branch": "cov_sport",
              "National Athlete": "cov_national_athlete",
              "Kendinizi ne zaman en iyi hissediyorsunuz?": "cov_best_time",
              "Kendinizi ne zaman en kötü hissediyorsunuz?": "cov_worst_time"}
COVS_TEEN = {**{k: v for k, v in COVS_ADULT.items()
                if k not in ("BM",) and not k.startswith("Kendinizi")},
             "BMI": "cov_bmi",
             "When do you feel at your best?": "cov_best_time",
             "When do you feel at your worst?": "cov_worst_time"}
MATCH = ["cov_age", "cov_height_cm", "cov_weight_kg", "cov_sport",
         "cov_national_athlete", "cov_best_time", "cov_worst_time"] + ITEMS


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    x = pd.ExcelFile(io.BytesIO(r.content))
    assert x.sheet_names == ["Adults", "Adolescents"], x.sheet_names
    return pd.read_excel(x, "Adults"), pd.read_excel(x, "Adolescents")


def prep(df, covs, study):
    assert set(df.columns) == set(covs) | set(ITEMS), \
        set(df.columns) ^ (set(covs) | set(ITEMS))
    df = df.rename(columns=covs)
    bmi = df["cov_weight_kg"] / (df["cov_height_cm"] / 100) ** 2
    assert np.allclose(df["cov_bmi"], bmi)
    df["cov_weight_kg"] = df["cov_weight_kg"].astype(float)
    df["cov_sport"] = df["cov_sport"].str.strip()
    assert set(df["cov_national_athlete"]) == {"Yes", "No"}
    df["cov_national_athlete"] = (df["cov_national_athlete"] == "Yes").astype(int)
    df.insert(0, "cov_study", study)
    return df


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    a, t = load()
    assert a.shape == (204, 24) and t.shape == (287, 24), (a.shape, t.shape)
    a = prep(a, COVS_ADULT, "adult")
    t = prep(t, COVS_TEEN, "adolescent")

    # Within-sheet copies. Adult copies differ only in experience.
    da = a.duplicated(MATCH)
    assert da.sum() == 9
    assert (a[a.duplicated(MATCH, keep=False)]
            .groupby(MATCH)["cov_experience_years"].nunique() == 2).all()
    a = a[~da]
    dt = t.duplicated(MATCH)
    assert dt.sum() == 1
    t = t[~dt]
    # Cross-sheet copies: drop the adolescent-sheet row.
    key = MATCH
    cross = t.merge(a[key], on=key, how="left", indicator=True)["_merge"]
    cross = (cross == "both").to_numpy()
    assert cross.sum() == 3 and (t.loc[cross, "cov_age"] == 18).all()
    t = t[~cross]
    assert len(a) == 195 and len(t) == 283

    d = pd.concat([a, t], ignore_index=True)
    d.insert(0, "id", d.index + 1)
    cov_cols = ["cov_study"] + [c for c in COVS_ADULT.values()]
    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(float)
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - PERMITTED
        assert not bad, (it, bad)
    pv = {i: PERMITTED for i in ITEMS}

    long = long[["id", "item", "resp"] + cov_cols]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() == 478
    assert long["item"].nunique() == 15

    checks = run_qc(long, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    out = OUT_DIR / f"{TABLE}.csv"
    long.to_csv(out, index=False)
    rep = irw_validate.validate_file(str(out), profile="upload",
                                     context={"permitted_values": pv})
    assert rep.conforms and not rep.errors, \
        [(f.check, f.message) for f in rep.errors]
    for f in rep.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")
    print(f"{TABLE}.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
