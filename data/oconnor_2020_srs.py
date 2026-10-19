#!/usr/bin/env python3

# Source: https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/W3QRSV
# DOI: 10.34894/W3QRSV
#   O'Connor, R. (2020). Spontaneous helping behavior of autistic and
#   non-autistic (pre-) adolescents: A matter of motivation? [Dataset].
#   DataverseNL.
# Data: "3. Raw data_autism helping.sav" -- 234 autistic and non-autistic
#   (pre-)adolescents; 192 of them have a complete Social Responsiveness
#   Scale administration (all 65 items), and the other 42 have none of it.
# License: CC0 1.0 (verified on the DataverseNL record, 2026-10-19).
# Item text: NOT shipped. The deposit carries no stem for any SRS item at
#   either the name or the label level, and the SRS is a commercially
#   published instrument (Western Psychological Services), so its wording is
#   not ours to distribute in any case.
#
# ONE table: 192 respondents x 65 items at 0-3, complete (12,480 responses).
#   Every one of the 65 columns carries an `r` suffix (srs1r ... srs65r) and
#   runs 0-3, which is the SRS's own scoring range; a 1-4 administration
#   recoded to 0-3 fits, and a reverse-key would not, since you do not
#   reverse all 65 items of a scale. Shipped as the deposit records them,
#   with nothing recoded either way -- but the suffix is the reason this note
#   exists rather than being left to the next reader.
#
# The 42 respondents with no SRS data are dropped by the melt, not by a rule:
#   all 65 of their cells are blank, so there is nothing to ship for them.
#
# NOT SHIPPED: `lucp1t2` ("looking at experimenter"), `lucp3t2` ("smiling")
#   and `lucp4rr` -- experimenter codings of the helping task on a 1-3 scale.
#   Three observational ratings of one behaviour are a different instrument
#   from the SRS, and the deposit documents neither their anchors nor what
#   `lucp4rr` measures.
#
# id: the deposit's own `sn` subject number (unique).
# Covariates: cov_diagnosis (autistic vs non-autistic), cov_sex, cov_iq (the
#   deposit's "IQ indication score"), cov_age_months (age at the task).
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
    REPO_ROOT / "automated_finding" / "runs" / "tail_batch" / "w3qrsv" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID, FNAME = 26822, "3. Raw data_autism helping.sav"
COVS = {"diagCOMB": "cov_diagnosis", "sex": "cov_sex", "IQfinal": "cov_iq",
        "aget2": "cov_age_months"}
NOT_SHIPPED = ["lucp1t2", "lucp3t2", "lucp4rr"]
SCALE = set(range(0, 4))
TABLE = "oconnor_2020_srs"


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = ("https://dataverse.nl/api/access/datafile/"
               f"{FILE_ID}?format=original")
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    items = sorted((c for c in df.columns if re.fullmatch(r"srs\d+r", c)),
                   key=lambda c: int(re.search(r"\d+", c).group()))
    assert len(items) == 65, len(items)
    assert {int(re.search(r"\d+", c).group()) for c in items} == set(range(1, 66))
    assert len(df) == 234, len(df)
    unaccounted = sorted(set(df.columns) - set(items) - set(COVS)
                         - set(NOT_SHIPPED) - {"sn"})
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"not shipped: {NOT_SHIPPED} (experimenter codings of the task)")

    # The SRS is all-or-nothing in this file: 42 respondents have none of it.
    blank = df[items].isna().all(axis=1)
    assert blank.sum() == 42, blank.sum()
    assert not df.loc[~blank, items].isna().any().any(), \
        "a partial SRS administration: the all-or-nothing note no longer holds"
    print(f"{int(blank.sum())} of 234 respondents have no SRS data at all; "
          f"{int((~blank).sum())} ship")

    df = df.rename(columns=COVS)
    df["id"] = pd.to_numeric(df["sn"]).astype(int)
    assert df["id"].is_unique
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov], errors="coerce")
        assert (v.dropna() % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")

    t = (df[["id", *cov_cols, *items]]
         .melt(id_vars=["id", *cov_cols], value_vars=items,
               var_name="item", value_name="resp")
         .dropna(subset=["resp"]))
    t["resp"] = pd.to_numeric(t["resp"]).astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the SRS's 0-3 range: {bad}"
    t = t[["id", "item", "resp", *cov_cols]]
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() == 192 and t["item"].nunique() == 65
    assert len(t) == 192 * 65

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:160]}")
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
