#!/usr/bin/env python3
# Source: https://zenodo.org/records/15575267
# DOI: none found. The deposit has no related identifiers; Crossref and
#   Europe PMC searches (title; author Bacon AM with silencing / feminine)
#   found only Bacon & White 2023 (Psychol Health Med,
#   10.1080/13548506.2022.2159459), a different study, as of 2026-10-02.
#   Bacon, A. (2025). Women's depression, Self-silencing and endorsement of
#   traditional feminine norms: a 21st century update [Data set]. Zenodo.
#   https://doi.org/10.5281/zenodo.15575267
# Data: norms SS 2025.sav (518 rows x 104 columns; women in two age groups,
#       18-25 and 60+).
# License: CC BY 4.0 (Zenodo API).
#
# Item text: not shipped. Both label levels checked: variable labels are
#   positional ("STSS item 1", "PHQ item 1", "CFNI item 1") and no column
#   has value labels. The wording is in the published STSS (Jack & Dill
#   1992), PHQ-9 and CFNI-45 (Parent & Moradi 2010).
#
# Tables (item codes are the source column names). With no paper and no
# value labels, the permitted sets come from the published instruments'
# documented formats, not from the observed values:
#   bacon_2025_stss   STS1-STS31  Silencing the Self Scale, 31 items, 5-point
#       (1 strongly disagree .. 5 strongly agree; Jack & Dill 1992).
#   bacon_2025_phq9   PHQ1-PHQ9   PHQ-9, 0 not at all .. 3 nearly every day.
#   bacon_2025_cfni45 CFNI1-CFNI45  Conformity to Feminine Norms
#       Inventory-45, 4-point 0-3 (Parent & Moradi 2010).
#   Scoring checks (asserted):
#   - the nine CFNI subscale columns (thin, domest, appear, modest, relate,
#     child, sexfid, romance, sweet) each equal the plain sum of five items
#     in every row (child only where CFNI43 is present), so CFNI items are
#     stored as scored;
#   - STSStot equals the plain sum of STS1-31 and dep the plain sum of
#     PHQ1-9 in every row EXCEPT the first eight (id 1-8), where both totals
#     disagree with the items (dep runs to 30, impossible for nine 0-3
#     items). The CFNI subscales agree in those same eight rows, so the
#     item responses are kept and only the two totals are treated as
#     mis-entered. STSS items are therefore stored as scored: the plain sum
#     reproduces the published total.
#   - CFNI43 (a "involvement with children" item) is missing for 82 women,
#     kept as missing.
#
# Dropped: totals and subscales (thin .. sweet, dep, ESP, CASS, STS, DS,
#   STSStot); ageGP (asserted = age band: 0 for 18-25, 1 for 60+, kept
#   only as cov_age_group).
# id: row index. The source "id" is a 1-518 participant number (unique, not
#   in file order) and is not shipped.
# Covariates: cov_age (years), cov_age_group (0 18-25, 1 60+), cov_ses
#   (1-9 self-rated socioeconomic status, as entered).

import os
import sys
import tempfile
from pathlib import Path

import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/15575267/files/"
       "norms%20SS%202025.sav/content")

STSS = [f"STS{i}" for i in range(1, 32)]
PHQ = [f"PHQ{i}" for i in range(1, 10)]
CFNI = [f"CFNI{i}" for i in range(1, 46)]
TABLES = {"bacon_2025_stss": STSS, "bacon_2025_phq9": PHQ,
          "bacon_2025_cfni45": CFNI}
PERMITTED = {"bacon_2025_stss": set(range(1, 6)),
             "bacon_2025_phq9": set(range(0, 4)),
             "bacon_2025_cfni45": set(range(0, 4))}
CFNI_SUBS = {"thin": [1, 17, 31, 37, 41], "domest": [2, 5, 12, 26, 34],
             "appear": [3, 6, 14, 20, 27], "modest": [4, 10, 19, 24, 29],
             "relate": [7, 15, 21, 23, 44], "child": [8, 16, 36, 40, 43],
             "sexfid": [9, 18, 22, 32, 42], "romance": [11, 25, 30, 33, 38],
             "sweet": [13, 28, 35, 39, 45]}
TOTALS = set(CFNI_SUBS) | {"dep", "ESP", "CASS", "STS", "DS", "STSStot"}
COVS = {"age": "cov_age", "ageGP": "cov_age_group", "SES": "cov_ses"}


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
    assert d.shape == (518, 104), d.shape

    known = set(STSS) | set(PHQ) | set(CFNI) | TOTALS | set(COVS) | {"id"}
    assert set(d.columns) == known, set(d.columns) ^ known
    assert sorted(d["id"]) == list(range(1, 519))
    assert not meta.variable_value_labels.get("STS1")
    assert meta.column_names_to_labels["STS1"] == "STSS item 1"

    for s, nums in CFNI_SUBS.items():
        cols = [f"CFNI{i}" for i in nums]
        raw = d[cols].sum(axis=1, min_count=5)
        ok = raw.notna()
        assert (raw[ok] == d.loc[ok, s]).all(), s
    assert d["CFNI43"].isna().sum() == 82
    bad_tot = ((d[PHQ].sum(axis=1) != d["dep"])
               | (d[STSS].sum(axis=1) != d["STSStot"]))
    assert sorted(d.loc[bad_tot, "id"]) == list(range(1, 9)), d.loc[bad_tot, "id"]
    assert ((d["age"] <= 25) == (d["ageGP"] == 0)).all()
    assert ((d["age"] >= 60) == (d["ageGP"] == 1)).all()
    assert not d.drop(columns="id").duplicated().any()
    assert not d[STSS + PHQ + CFNI].T.duplicated().any()

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    cov_cols = list(COVS.values())

    names = []
    for table, its in TABLES.items():
        long = d.melt(id_vars=["id"] + cov_cols, value_vars=its,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        assert (long["resp"] % 1 == 0).all()
        long["resp"] = long["resp"].astype(int)
        allowed = PERMITTED[table]
        for it, g in long.groupby("item"):
            bad = set(g["resp"]) - allowed
            assert not bad, (table, it, bad)
        pv = {i: allowed for i in its}
        long = long[["id", "item", "resp"] + cov_cols]
        for c in cov_cols:
            long[c] = long[c].astype("Int64")
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        assert not long.duplicated(["id", "item"]).any()
        assert long["id"].nunique() >= 100
        assert long["item"].nunique() == len(its) > 1
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        out = OUT_DIR / f"{table}.csv"
        long.to_csv(out, index=False)
        names.append(table)
        rep = irw_validate.validate_file(str(out), profile="upload",
                                         context={"permitted_values": pv})
        assert rep.conforms and not rep.errors, \
            [(f.check, f.message) for f in rep.errors]
        for f in rep.findings:
            print(f"    [{f.severity}] {f.check}: {f.message}")
        print(f"{table}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")
    assert len(names) == len(set(names))


if __name__ == "__main__":
    convert()
