#!/usr/bin/env python3

# Source: https://figshare.com/articles/dataset/_/28303889
# DOI: 10.6084/m9.figshare.28303889
#   Jaber, K. (2025). Postpartum Depression [Dataset]. figshare.
# Data: "Data Figshare.xlsx" -- 267 postpartum women, a 10-item depression
#   screen scored 0-3, administered in Arabic, plus eleven obstetric and
#   demographic columns.
# License: CC BY 4.0 (verified on the figshare record).
# Item text: NOT shipped. The header row carries the full Arabic stem of each
#   of the ten items -- extraction is solved and needs no further source. It
#   is held because the stems identify the instrument as the Edinburgh
#   Postnatal Depression Scale (Cox, Holden & Sagovsky 1987): the wording,
#   order and 0-3 scoring match item for item ("I have been able to laugh and
#   see the funny side of things", "I have looked forward with enjoyment to
#   things", ... "The thought of harming myself has occurred to me"). The EPDS
#   has no row in itemtext/instrument_rights_register.csv, and under the
#   2026-10-15 silence rule a third-party instrument with no ruling does not
#   ship, whatever the deposit's own licence says. A ruling on the EPDS
#   releases this table's item text and the Arabic wording with it.
#
# ITEM CODES are derived from the header's own leading number, reversibly:
#   the column beginning "1. لقد كنت قادرة على الضحك..." becomes EPDS_1, and
#   the mapping is checked to be a permutation of 1-10 before anything is
#   written. The Arabic stem cannot serve as a code (full sentence, with
#   punctuation), which is the case datastandard.md's opaque-label guidance
#   covers.
#
# ONE table, 267 respondents:
#   jaber_2025_epds   10 items, 0-3
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: NONE are shipped. All eleven (age, family income, education,
#   working status, gravidity, parity, gestational age, anaesthesia, infant
#   feeding, intrapartum complications, mode of delivery) are option-coded
#   small integers and the deposit ships no codebook, so "Age" = 2 cannot be
#   given a meaning. They are dropped with this reason rather than shipped as
#   unlabelled integers.
# Dropped: "EPDS Score" (the sum) and "EPDS Category" (its 13-point split).
import os
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get(
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "figshare_batch" / "28303889" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
ARTICLE, FNAME = 28303889, "Data Figshare.xlsx"
NAME = "jaber_2025_epds"
SCALE = set(range(0, 4))

DEMOG = ["Age", "Family Income", "Education", "Working status", "Gravidity",
         "Parity", "Gestational age", "Anesthesia", "Infant Feeding",
         "Intrapartum Complications", "Mode of Delivery"]
DERIVED = ["EPDS Score", "EPDS Category"]


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://api.figshare.com/v2/articles/{ARTICLE}",
                         headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_excel(fetch(), sheet_name="Data")

    codes = {}
    for c in df.columns:
        if c in DEMOG or c in DERIVED:
            continue
        m = re.match(r"^\s*(\d{1,2})\s*\.", str(c))
        assert m, f"item column with no leading number: {c!r}"
        codes[c] = f"EPDS_{int(m.group(1))}"
    assert sorted(int(v.split('_')[1]) for v in codes.values()) == list(range(1, 11)), \
        sorted(codes.values())

    unaccounted = [c for c in df.columns
                   if c not in set(list(codes) + DEMOG + DERIVED)]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"dropped, option-coded with no codebook in the deposit: {DEMOG}")
    print(f"dropped, derived: {DERIVED}")

    df = df.rename(columns=codes)
    df.insert(0, "id", range(len(df)))
    cols = [f"EPDS_{i}" for i in range(1, 11)]

    t = (df[["id", *cols]]
         .melt(id_vars="id", value_vars=cols, var_name="item",
               value_name="resp")
         .dropna(subset=["resp"]))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    bad = sorted(set(t["resp"]) - SCALE)
    assert not bad, f"resp outside the documented 0-3 scale: {bad}"
    t = t[["id", "item", "resp"]]
    assert not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2

    checks = run_qc(t, permitted_values=SCALE)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:170]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": SCALE})
    assert report.conforms and not report.errors, \
        [(f.check, f.message) for f in report.errors]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
