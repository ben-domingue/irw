#!/usr/bin/env python3

# Source: https://data.mendeley.com/datasets/j5zjb46tr7/1
# DOI: 10.17632/j5zjb46tr7.1
#   Díaz Guerra, D. D., Ramos-Galarza, C., Hernández Lugo, M. de la C., &
#   Broche-Pérez, Y. (2024). Validity and Reliability of the Executive
#   Function Scale (UEF-1) in Cuban University Students [Dataset]. Mendeley
#   Data.
# Data: "Data EF Cuba.sav" -- 1,092 Cuban university students answering the
#   31-item UEF-1 executive-function self-report, complete throughout.
# License: CC BY 4.0 (verified on the Mendeley record and DataCite, 2026-10-19).
# Item text: NOT shipped, and it cannot be from this deposit. All 41 variable
#   labels are EMPTY -- checked, 0 of 41 -- so there is no stem anywhere in the
#   file. Value labels are populated on 33 columns, i.e. the response options
#   without the questions, and irw#1770 forbids shipping option text alone.
#
# ONE table: 1,092 respondents x 31 items at 1-5 (33,852 responses).
#
# NOT SHIPPED: F1-F7, the deposit's own factor scores. They are composites of
#   the 31 items, not responses.
#
# id: the row index. The deposit carries no respondent id column.
# Covariates: cov_age, cov_sex, cov_province -- the deposit's own codes, which
#   it does not label.
import os
import re
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
    REPO_ROOT / "automated_finding" / "runs" / "group2_t1" / "j5zjb46tr7" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
DATASET, FNAME = "j5zjb46tr7", "Data EF Cuba.sav"
COVS = {"Edad": "cov_age", "Sexo": "cov_sex", "Provincia": "cov_province"}
FACTORS = [f"F{i}" for i in range(1, 8)]
SCALE = set(range(1, 6))
TABLE = "diazguerra_2024_uef1"


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
    items = sorted((c for c in df.columns if re.fullmatch(r"UEF\d+", c)),
                   key=lambda c: int(re.search(r"\d+", c).group()))
    assert len(items) == 31, len(items)
    assert len(df) == 1092, len(df)
    assert not df[items].isna().any().any()
    unaccounted = sorted(set(df.columns) - set(items) - set(COVS) - set(FACTORS))
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    # The reason there is no item text: the file has no stems at all.
    non_empty = [c for c in df.columns if (labels.get(c) or "").strip()]
    assert not non_empty, f"variable labels appeared: {non_empty[:5]}"
    print(f"not shipped: {FACTORS} (the deposit's factor scores); "
          f"0 of {len(df.columns)} variable labels carry a stem")

    df = df.rename(columns=COVS)
    df["id"] = range(1, len(df) + 1)
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov], errors="coerce")
        assert (v.dropna() % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")

    t = (df[["id", *cov_cols, *items]]
         .melt(id_vars=["id", *cov_cols], value_vars=items,
               var_name="item", value_name="resp"))
    t["resp"] = pd.to_numeric(t["resp"]).astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the 1-5 scale: {bad}"
    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() == 1092 and t["item"].nunique() == 31
    assert len(t) == 1092 * 31

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:150]}")
    report = irw_validate.validate_frame(t, label=TABLE, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{TABLE}.csv", index=False)
    print(f"{TABLE}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
