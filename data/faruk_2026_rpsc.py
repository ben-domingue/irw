#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.32939375.v2
# DOI: none found (figshare deposit only; no related identifiers, and
#   Crossref / Europe PMC searches for a Racial Prejudice Scale for Children
#   paper found nothing as of 2026-10-02).
#   Faruk, M. O. (2026). "Racial Prejudice Scale Development Dataset_MOF &
#   MKM." figshare. Developed by Md Omar Faruk under the supervision of
#   M. Kamruzzaman Mozumder (Department of Clinical Psychology, University of
#   Dhaka), per the deposit description.
# Data: figshare file 66441653, Final data set_RPSC_2020.sav (298 rows x 36
#       columns; Bangladeshi children and adolescents aged 11-18).
# License: CC BY 4.0 (figshare API).
#
# Item text: not shipped. Both label levels checked: variable labels are
#   positional ("Racial Prejudice Scale_1" .. "_23"); value labels give the
#   four response anchors. The deposit's RPSC_English.pdf and RPSC_Bangla
#   .pdf print the questionnaire, but only 17 numbered items against the 23
#   in the data (presumably the final post-EFA form), so which statement is
#   RPSk for k > 17 -- and whether items 1-17 keep their numbers -- is not
#   documented.
#
# Table:
#   faruk_2026_rpsc  RPS1-RPS23, Racial Prejudice Scale for Children.
#       1 = Not at all agree, 2 = Slightly agree, 3 = Somewhat agree,
#       4 = Completely agree (the .sav value labels on every item, and the
#       deposit questionnaire's 4-point response row). Tot_sum is their sum
#       (asserted). All statements in the printed form are worded towards
#       acceptance of other races.
#
# Dropped:
#   - Tot_sum (composite).
#   - ID: a 1..298 participant number; replaced by the row index.
#   - Assant (parental assent): constant "Yes".
# id: row index.
# Covariates: cov_analysis_sample (1 exploratory, 2 confirmatory half, per
#   the value labels), cov_age, cov_sex (1 male, 2 female), cov_religion
#   (1 Islam .. 5 other), cov_language (1 Bangla, 2 Chakma, 3 Marma,
#   4 Rakhine, 5 Tripura, 6 other), cov_hours_with_friends, cov_grade,
#   cov_ses (1 lower, 2 middle, 3 lower middle, 4 higher -- the deposit's
#   own codes), cov_family_type (1 single, 2 extended),
#   cov_feeling_thermometer (0-100 single item, kept as a covariate).

import os
import sys
import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://ndownloader.figshare.com/files/66441653"
TABLE = "faruk_2026_rpsc"

ITEMS = [f"RPS{i}" for i in range(1, 24)]
COVS = {"Analysis_Type": "cov_analysis_sample", "Age": "cov_age",
        "Sex": "cov_sex", "Religion": "cov_religion",
        "Language": "cov_language", "HS_F": "cov_hours_with_friends",
        "Grade": "cov_grade", "Socio_ES": "cov_ses",
        "Nat_F": "cov_family_type", "FT": "cov_feeling_thermometer"}
DROPPED = {"Tot_sum", "ID", "Assant"}
LABELS = {1.0: "Not at all agree", 2.0: "Slightly agree",
          3.0: "Somewhat agree", 4.0: "Completely agree"}


def load():
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as f:
        f.write(r.content)
        path = f.name
    try:
        df, meta = pyreadstat.read_sav(path)
    finally:
        os.unlink(path)
    return df, meta


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    d, meta = load()
    assert d.shape == (298, 36), d.shape

    # Balance the books.
    known = set(ITEMS) | set(COVS) | DROPPED
    assert set(d.columns) == known, set(d.columns) ^ known
    for c in ITEMS:
        assert meta.variable_value_labels[c] == LABELS, c
    assert (d[ITEMS].sum(axis=1) == d["Tot_sum"]).all()
    assert set(d["Assant"]) == {"1"}
    assert d["ID"].is_unique
    assert not d.duplicated().any()
    assert not d.drop(columns="ID").duplicated().any()

    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())
    for c in cov_cols:
        d[c] = pd.to_numeric(d[c])

    long = d.melt(id_vars=["id"] + cov_cols, value_vars=ITEMS,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    allowed = {1, 2, 3, 4}
    for it, g in long.groupby("item"):
        bad = set(g["resp"]) - allowed
        assert not bad, (it, bad)
    long = long[["id", "item", "resp"] + cov_cols]
    for c in cov_cols:
        if c != "cov_hours_with_friends":
            long[c] = long[c].astype("Int64")
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    assert long["id"].nunique() == 298 and long["item"].nunique() == 23
    pv = {i: allowed for i in ITEMS}
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
