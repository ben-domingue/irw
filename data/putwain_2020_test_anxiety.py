#!/usr/bin/env python3

# Source: https://data.mendeley.com/datasets/9dcs5nvwtw/1
# DOI: 10.17632/9dcs5nvwtw.1
#   Putwain, D. (2020). Test Anxiety, Wellbeing, Generalised Anxiety and Panic
#   [Dataset]. Mendeley Data.
# Data: the deposit's single .sav -- 918 English students aged 13-19, three
#   instruments, complete throughout (no missing cell anywhere).
# License: CC BY 4.0 (verified on the Mendeley record and DataCite, 2026-10-19).
# Item text: NOT shipped here, but every item's administered English stem is
#   its SPSS variable label ("Before a test/ exam, I am worried I will fail.")
#   with value labels on every block, so a later pass is cheap. The RCADS has
#   no rights-register row; neither do the other two.
#
# THREE tables, 918 respondents each:
#   putwain_2020_test_anxiety  16 items, 1-5  (MTAS)
#   putwain_2020_wellbeing      7 items, 1-5
#   putwain_2020_rcads         15 items, 0-3  (RCADS short form)
#
# NOT MERGED with the 2022 deposit (10.17632/6bhr52dc5v), which shares all 16
#   MTAS codes: the samples are different (13-19 here, 16-19 there; 14 of 835
#   response vectors in common, i.e. coincidence) and so is the wording --
#   "Before a test/ exam, I am worried I will fail." here against "Before an
#   exam, I am worried I will fail." there. Two administrations, two tables.
#
# id: the row index. The deposit carries no respondent id column.
# Covariates: cov_school, cov_gender, cov_age, cov_year_group, cov_ethnicity,
#   cov_free_school_meals -- the deposit's own codes.
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
    REPO_ROOT / "automated_finding" / "runs" / "group2_t1" / "9dcs5nvwtw" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATASET = "9dcs5nvwtw"
FNAME = "Test Anxiety, Wellbeing, Generalised Anxiety and Panic.sav"
COVS = {"School": "cov_school", "Gender": "cov_gender", "Age": "cov_age",
        "Year_Group": "cov_year_group", "Ethnicity": "cov_ethnicity",
        "FSM": "cov_free_school_meals"}
TABLES = {"putwain_2020_test_anxiety": ("MTAS", 16, set(range(1, 6))),
          "putwain_2020_wellbeing": ("WELL", 7, set(range(1, 6))),
          "putwain_2020_rcads": ("RCADS", 15, set(range(0, 4)))}


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
    assert len(df) == 918, len(df)
    assert not df.isna().any().any(), "the file is complete; a blank is new"
    items = [f"{p}{i}" for p, n, _ in TABLES.values() for i in range(1, n + 1)]
    unaccounted = sorted(set(df.columns) - set(items) - set(COVS))
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVS)
    df["id"] = range(1, len(df) + 1)
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov])
        assert (v % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (prefix, n, scale) in TABLES.items():
        cols = [f"{prefix}{i}" for i in range(1, n + 1)]
        for c in cols:
            assert len((labels.get(c) or "").strip()) > 8, (c, labels.get(c))
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp"))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - scale)
        assert not bad, f"{name}: resp outside the labelled scale: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() == 918 and t["item"].nunique() == n
        checks = run_qc(t, permitted_values=scale)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:130]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": scale})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
