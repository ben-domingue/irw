#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Entrepreneurial_Mindset_Research_Self-Efficacy_and_Academic_Integrity_Among_Ghanaian_Tertiary_Students_Survey_Data_and_Analysis_Code/34779651
# DOI: 10.6084/m9.figshare.34779651.v1 (data; no paper DOI on the record)
#   Osei-Anim R (2026). Entrepreneurial Mindset, Research Self-Efficacy and
#   Academic Integrity Among Ghanaian Tertiary Students: Survey Data and
#   Analysis Code. figshare.
# Data: Ghana_dataset_cleaned_n247.csv (247 tertiary students x 82 columns),
#   survey 24 Apr-31 May 2025, mostly Kumasi institutions.
# License: CC BY 4.0 (figshare record).
# Codebook: none as such; the column headers are the English item stems and
#   the deposit's 02_reliability_and_scoring.py defines the blocks by column
#   position: cols 1-20 mindset, 21-67 research self-efficacy, 68-73 personal
#   integrity, 74-76 cheating pressure.
#
# Counts: 247 rows = the description's analytic sample of 247.
# Item codes: the headers are full stems, unusable as codes, so each block's
#   items are numbered in file order (em01-em20, rse01-rse47, ai01-ai06,
#   cp01-cp03). The tie is checked against STEMS below (each header must
#   start with the listed text), so the code-to-stem map is in this file.
# Tables (1-5, items as deposited):
#   oseianim_2026_entrepreneurial_mindset  20 items (vision 1-4, learning 5-8,
#                                          creativity 9-16, SRC 17-20)
#   oseianim_2026_research_self_efficacy   47 items (initiation 1-12,
#       information literacy 13-22, design 23-30, data analysis 31-38,
#       communication 39-47)
#   oseianim_2026_academic_integrity       6 items (personal integrity)
#   oseianim_2026_cheating_pressure        3 items (perceived pressure to cheat;
#       scored separately by the authors, "opposite theoretical valence")
# Not shipped: Timestamp (per-person submission time); free-text university
#   and programme names.
# id = row index. Covariates: programme status, gender, age band.
# Item text: not shipped -- the stems are the headers (English), but the
#   instruments are unidentified adaptations with no register row; left for an
#   itemtext pass. No anchors in the file.

import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = "https://ndownloader.figshare.com/files/70627080"
BLOCKS = {  # table: (code prefix, first col index, last col index exclusive)
    "oseianim_2026_entrepreneurial_mindset": ("em", 1, 21),
    "oseianim_2026_research_self_efficacy": ("rse", 21, 68),
    "oseianim_2026_academic_integrity": ("ai", 68, 74),
    "oseianim_2026_cheating_pressure": ("cp", 74, 77),
}
# first words of selected stems, asserted at block boundaries
STEMS = {1: "Vision is important", 20: "when students review their choices",
         21: "if confronted by a problem", 67: "i can list all my references",
         68: "it is important for me to follow", 73: "i try to follow my own",
         74: "if student does not cheat", 76: "i feel peer pressure to cheat"}
COVS = {"Programme status": "cov_programme_status", "Gender": "cov_gender",
        "Age": "cov_age_band"}


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content))
    assert d.shape == (247, 82), d.shape
    cols = list(d.columns)
    for i, s in STEMS.items():
        assert cols[i].startswith(s), (i, cols[i][:40])
    assert cols[0] == "Timestamp" and set(COVS) <= set(cols[77:])
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype(str).str.strip()
    allowed = set(range(1, 6))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    seen = set()
    for table, (pre, a, b) in BLOCKS.items():
        ren = {cols[j]: f"{pre}{k:02d}" for k, j in enumerate(range(a, b), 1)}
        seen |= set(ren)
        long = d[["id"] + list(ren) + covs].rename(columns=ren).melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"])
        long = long.dropna(subset=["resp"])
        assert not set(long["resp"]) - allowed, table
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        long = long.sort_values(["id", "item"]).reset_index(drop=True)
        checks = run_qc(long, permitted_values={c: allowed for c in ren.values()})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"[warn] {table} {c.name}: {c.detail[:120]}")
        long.to_csv(OUT_DIR / f"{table}.csv", index=False)
        print(f"[write] {table}: {len(long)} responses, "
              f"{long['id'].nunique()} ids x {long['item'].nunique()} items")
    assert seen == set(cols[1:77])


if __name__ == "__main__":
    main()
