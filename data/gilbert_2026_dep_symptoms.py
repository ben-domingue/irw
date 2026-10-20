#!/usr/bin/env python3
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/G68C5Y
# DOI: 10.7910/DVN/G68C5Y
# Data: DepressionDat.csv (semicolon-delimited; fetched with ?format=original)
# License: CC BY-NC-SA 4.0, as stated on the deposit record (checked
#   2026-10-19). NC proceeds under datastandard.md "Before you start" (ruled
#   2026-10-01); Derived_License carries the NC restriction through.
#
# Gilbert, J. B., Kim, E. J., Himmelsbach, Z., Ulitzsch, E., & Zhang, L.
#   (2026). Idiographic item response theory: Modeling person-specific
#   differential item functioning in intensive longitudinal data.
#   Multivariate Behavioral Research.
#
# PROVENANCE CAVEAT -- READ BEFORE UPLOADING. The deposit describes this file
# as "repeated-measures depression-symptom data (9 dichotomous DSM-5 items in a
# psychotherapy RCT)", i.e. it is NOT the depositors' own data collection: the
# analysis script (02 an_idio_dep.qmd) refers to it only as "per McNeish, limit
# to C group only" and names no trial, paper or source deposit. The deposit's
# CC BY-NC-SA covers what the depositors published; it does not by itself
# establish the originating trial's redistribution terms, which is the case
# datastandard.md's "scraped or relabelled third-party data" clause points at.
# Josh Gilbert can resolve this in one message -- until he does, this table is
# held rather than staged.
#
# Table: gilbert_2026_dep_symptoms -- 256 patients x up to 28 sessions x 9
#   dichotomous DSM-5 major-depression criteria.
#   item  = the symptom column name (mood, concentration, self_worth,
#           suicidal_ideation, tiredness, sleep, pleasure, psychomotor,
#           appetite), as the deposit spells it.
#   resp  = 0/1, symptom absent/present.
#   wave  = sessionN, the session index (0 = intake, max 27).
#   treat = Group.x recoded, following the deposit's own analysis script:
#           "based on N, group 2 is control" -> group 2 = 0, group 1 = 1. That
#           reading is the depositors', not documentation from the trial; no
#           arm labels ship with the file.
#   The nine *_lag columns are the same responses shifted one session (a
#   derived copy used by the paper's model) and are dropped.
# Covariates: none in the file.
# Item text: not shipped. The item codes ARE the DSM-5 criterion names, but the
#   administered wording (whatever instrument the trial used to score each
#   criterion 0/1 per session) is in the unnamed source trial, not in this
#   deposit, and no label level exists at all -- the file is a plain CSV.

import sys
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
CSV = "https://dataverse.harvard.edu/api/access/datafile/14228345?format=original"
NAME = "gilbert_2026_dep_symptoms"
ITEMS = ["mood", "concentration", "self_worth", "suicidal_ideation",
         "tiredness", "sleep", "pleasure", "psychomotor", "appetite"]


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(CSV, headers=UA, timeout=180)
    r.raise_for_status()
    d = pd.read_csv(BytesIO(r.content), sep=";")

    assert d.shape == (5517, 21), d.shape
    assert d["PatID.x"].nunique() == 256
    assert set(d["Group.x"].unique()) == {1, 2}
    assert not d.duplicated(["PatID.x", "sessionN"]).any()
    # The _lag columns are a one-session shift of the items, not new responses:
    # check that on every person each lag equals the previous session's value.
    # It holds exactly in the file's STORED order, which is what the deposit
    # computed the lags in -- and that is not session order: the last three
    # rows are (PatID 45, session 9), (142, session 1) and (155, session 3),
    # appended after the rest of their own patient's sessions. So each lag is
    # the previous ROW's response, which for those three and for the session
    # following each of them is not the previous session's. Nothing here ships
    # the lags, so it is noted rather than repaired -- but it does bear on the
    # published model, which used them.
    assert list(d.index[-3:]) == [5514, 5515, 5516]
    tail = set(map(tuple, d.loc[5514:, ["PatID.x", "sessionN"]].astype(int).values))
    assert tail == {(45, 9), (142, 1), (155, 3)}, tail
    for it in ITEMS:
        prev = d.groupby("PatID.x")[it].shift(1)
        both = prev.notna() & d[f"{it}_lag"].notna()
        assert (prev[both] == d.loc[both, f"{it}_lag"]).all(), it
    accounted = {"PatID.x", "Group.x", "sessionN", *ITEMS,
                 *[f"{i}_lag" for i in ITEMS]}
    assert set(d.columns) == accounted, set(d.columns) ^ accounted

    long = d.melt(id_vars=["PatID.x", "Group.x", "sessionN"], value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    dropped = long["resp"].isna().sum()
    long = long.dropna(subset=["resp"])

    t = pd.DataFrame({
        "id": long["PatID.x"].astype(int),
        "item": long["item"],
        "resp": long["resp"].astype(int),
        "wave": long["sessionN"].astype(int),
        "treat": (long["Group.x"] == 1).astype(int),
    })
    t = t.sort_values(["id", "wave", "item"]).reset_index(drop=True)

    assert not t.duplicated(["id", "item", "wave"]).any()
    assert t["id"].nunique() == 256
    assert t["item"].nunique() == 9
    assert set(t["resp"].unique()) == {0, 1}
    assert (t.groupby("id")["treat"].nunique() == 1).all()
    assert dropped == 55, dropped

    pv = {i: {0, 1} for i in ITEMS}
    cl = {i: "depression_symptoms" for i in ITEMS}
    fails = [(c.name, c.detail) for c in
             run_qc(t, permitted_values=pv, item_constructs=cl) if c.status == "fail"]
    assert not fails, fails
    report = irw_validate.validate_frame(
        t, label=NAME, profile="upload",
        context={"permitted_values": pv, "item_constructs": cl})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]
    for f in report.findings:
        print(f"    [{f.severity}] {f.check}: {f.message}")

    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} waves={t['wave'].nunique()} "
          f"treat1={t['treat'].eq(1).sum()} dropped_na={dropped}")


if __name__ == "__main__":
    convert()
