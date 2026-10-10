#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/25QUO9
# DOI: 10.65961/ajelt-2025-1-003
#   Leis, A., & Mundotia, M. (2025). The intrinsic motivation of students studying English
#   in India. Asian Journal of English Language Teaching.
# Data: Harvard Dataverse 10.7910/DVN/25QUO9 (Leis, Adrian; 2024-07-30). "The Intrinsic
#       Motivation of Students Studying English in India Dataset.xlsx" (file 10409651).
#       Sheet "Students Raw Data": 379 high-school students (+ four trailing summary rows:
#       Average, SD and blanks, which have no Timestamp) x Timestamp, Gender, Age, Class,
#       self-rated English, the 20 SDT motivation items with the full English stem as
#       header, and one open-ended answer. Sheet "Teachers Raw Data": 36 teachers'
#       predictions (below the N floor; not used).
# License: CC0 1.0 (Dataverse record).
#
# Item text: shipped (English administration: the paper's Methods give the items in English,
#   distributed on printed forms and Google Forms in English-medium classes). Stems are the
#   xlsx column headers; anchors 1 strongly disagree .. 5 strongly agree from the paper's
#   Methods (2-4 unlabelled). Built by
#   automated_finding/itemtext_verification/make_itemtext_leis_2025.py. Label levels
#   checked: headers carry the stems; no value labels exist (xlsx).
#
# Instrument (paper): 20 items after Agawa & Takeuchi (2016), measuring intrinsic motivation
#   (6), identified regulation (6), external regulation (3) and amotivation (5); the paper
#   gives the counts but not which item is which, so one table holds all 20.
# Item codes: q01..q20 = the 20 stem columns in sheet order (the header text is the item;
#   the mapping is printed by the script and repeated in the item text table).
# Table: leis_2025_english_motivation   q01-q20, 1-5, as administered (amotivation items
#   are worded negatively and kept as worded).
# Skipped: the open-ended "What kinds of things are fun in English class?" (free text);
#   Timestamp; the four summary/blank rows; the teachers' sheet (N = 36).
# Covariates: cov_gender (as stored text), cov_age, cov_class (IX-XII),
#   cov_english_self (self-rated English: not good / average / good / excellent).
# id: row index of the 379 respondent rows.

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
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "25quo9"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://dataverse.harvard.edu/api/access/datafile/10409651?format=original"
NAME = "leis_2025_english_motivation"
COVS = {"Gender": "cov_gender", "Age": "cov_age", "Class": "cov_class",
        "How good is your English?": "cov_english_self"}


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def item_columns(d: pd.DataFrame) -> list:
    """The 20 stem columns, in sheet order (shared logic with the item text builder)."""
    cols = list(d.columns[5:25])
    assert len(cols) == 20 and all(len(c.strip()) > 25 for c in cols)
    return cols


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="Students Raw Data")
    assert d.shape == (383, 26)
    summary = d["Timestamp"].isna()
    assert summary.sum() == 4 and set(d.loc[summary, "Gender"].dropna()) == {"Average", "SD"}
    d = d[~summary].reset_index(drop=True)
    assert len(d) == 379
    print("  [skip] 4 trailing rows without Timestamp (Average, SD, blanks)")
    stems = item_columns(d)
    code = {c: f"q{i:02d}" for i, c in enumerate(stems, 1)}
    for c, k in code.items():
        print(f"    {k} = {c.strip()}")
    other = set(d.columns) - set(stems) - set(COVS)
    assert other == {"Timestamp", d.columns[-1]}, other
    print(f"  [skip] Timestamp; {d.columns[-1]!r}: free text")
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns={**COVS, **code})
    covs = list(COVS.values())
    its = list(code.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    assert t["resp"].isin(range(1, 6)).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert set(t["item"]) == set(its) and not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100 and len(t) == int(d[its].notna().sum().sum())
    pv = {i: set(range(1, 6)) for i in its}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.warnings:
        print(f"    [validate warn] {f.check}: {f.message[:160]}")
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
