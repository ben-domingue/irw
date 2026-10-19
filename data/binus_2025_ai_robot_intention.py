#!/usr/bin/env python3

# Source: https://zenodo.org/records/17688586
# DOI: 10.5281/zenodo.17688586
#   Binus University (2025). Behavioral Intention to Use AI-Based Robots
#   Questionnaire [Dataset]. Zenodo.
# Data: "FINAL DATA.csv" -- 320 respondents, 1-5 agreement, bare construct codes.
# License: CC BY 4.0 (verified on the Zenodo record).
# Item text: NOT shipped. One header row of bare codes, no label level in a .csv.
#   The stems are in the paper behind the deposit title.
# NAMING. The record's only creator is the INSTITUTION, "Binus University" -- no
#   individual is named anywhere on it. The table prefix is therefore the
#   institution, following usc_2026_gasa, which took the same route earlier in this
#   #3077 run. This is not the anonymous-creator case that parks a lead: an
#   institutional depositor is a nameable author, "Anonymous, Anonymous" is not.
#
# A SIX-POINT SCALE. All six categories are used across every block, so 6 is a
#   response and not a sentinel; checked over the whole file before shipping.
#
# SIX tables, all 1-6:
#   binus_2025_trust                  4 items (TR1-4)
#   binus_2025_subjective_norm        4 items (SN1-4)
#   binus_2025_perceived_usefulness   6 items (PU1-6)
#   binus_2025_perceived_ease         6 items (PEOU1-6)
#   binus_2025_attitude               4 items (ATT1-4)
#   binus_2025_intention              9 items (BI1-9)
# id: the file carries no respondent id; the 0-based row index is used.
# Covariates: none -- the deposit ships no demographics.
# Rights: none of the six is in the instrument rights register; checked by
# construct against its block list by hand.
import os
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
    "IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "b5_raw" / "17688586"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD, FNAME = 17688586, "FINAL DATA.csv"
SCALE = set(range(1, 7))

BLOCKS = {
    "binus_2025_trust": [f"TR{i}" for i in range(1, 5)],
    "binus_2025_subjective_norm": [f"SN{i}" for i in range(1, 5)],
    "binus_2025_perceived_usefulness": [f"PU{i}" for i in range(1, 7)],
    "binus_2025_perceived_ease": [f"PEOU{i}" for i in range(1, 7)],
    "binus_2025_attitude": [f"ATT{i}" for i in range(1, 5)],
    "binus_2025_intention": [f"BI{i}" for i in range(1, 10)],
}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                         headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_csv(fetch())
    df.insert(0, "id", range(len(df)))
    items = {c for cols in BLOCKS.values() for c in cols}
    for c in items:
        assert c in df.columns, f"expected item column {c} is absent"
    unaccounted = [c for c in df.columns if c not in ({"id"} | items)]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    for name, cols in BLOCKS.items():
        t = (df[["id", *cols]]
             .melt(id_vars="id", value_vars=cols, var_name="item",
                   value_name="resp")
             .dropna(subset=["resp"]))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), f"{name}: fractional resp"
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the observed 1-6 scale: {bad}"
        t = t[["id", "item", "resp"]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert name not in written
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:170]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        written.append(name)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
