#!/usr/bin/env python3

# Source: https://zenodo.org/records/16072050
# DOI: 10.5281/zenodo.16072050
#   Zeng, Y., & Zhang, Y. (2025). online learning readiness and attitude
#   towards flipped learning on adoption of flipped learning [Dataset].
#   Zenodo.
# Data: the deposit's single .sav -- 353 Chinese university students (a
#   teacher-education sample), 44 items in six blocks, all on the same 1-5
#   agreement scale, with no missing cell in the file.
# License: CC BY-SA 4.0 (verified on the Zenodo record, 2026-10-19).
# Item text: NOT shipped, extraction solved -- every item's full administered
#   Chinese stem is in its SPSS variable label, numbered in questionnaire
#   order ("29.用翻转课堂的方式学习课程更轻松"). The first four blocks are
#   Online Learning Readiness Scale dimensions (Hung et al. 2010), which owe a
#   rights ruling; ATFL/AFL are the study's own.
#
# 10.5281/zenodo.16072049 IS THE SAME RECORD. Both DOIs were separate leads in
#   the ledger, and both resolve to zenodo.org/records/16072050 with the same
#   single file -- a concept/version DOI pair, not two deposits. The other lead
#   is closed as duplicate_version.
#
# SIX tables, 353 respondents, 1-5 throughout. Block names come from the
#   stems plus the study's own title:
#   TR    7  technology readiness (liking the newest technology, trusting it)
#   OCSE  5  online communication self-efficacy (expressing oneself, posting)
#   SDL   8  self-directed learning
#   MFL   8  motivation for learning
#   ATFL 11  attitude towards flipped learning
#   AFL   5  adoption of flipped learning
#
# NOT SHIPPED: `totalvalue` (the deposit's own 44-item sum), `totalseconds`
#   (whole-questionnaire duration, not a per-item rt), `index`, and `Major`,
#   which is free text in Chinese with 48 distinct spellings of a handful of
#   teacher-education programmes -- a covariate nobody could use as given.
#
# id: the row index. `index` is a 1-353 row counter, not a respondent id.
# Covariates: cov_gender, cov_grade, cov_flipped_experience,
#   cov_selfstudy_hours -- the deposit's own codes; it documents no value
#   labels, so nothing is relabelled.
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
    REPO_ROOT / "automated_finding" / "runs" / "tail_batch" / "zenodo16072050" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
RECORD = 16072050
FNAME = ("online learning readiness and attitude towards flipped learning on "
         "adoption of flipped learning dataset.sav")
SCALE = set(range(1, 6))
COVS = {"Gender": "cov_gender", "Grade": "cov_grade",
        "Experience": "cov_flipped_experience",
        "Timespent": "cov_selfstudy_hours"}
NOT_SHIPPED = ["index", "totalseconds", "totalvalue", "Major"]
BLOCKS = {
    "zeng_2025_technology_readiness": ("TR", 7),
    "zeng_2025_online_comm_self_efficacy": ("OCSE", 5),
    "zeng_2025_self_directed_learning": ("SDL", 8),
    "zeng_2025_motivation_for_learning": ("MFL", 8),
    "zeng_2025_attitude_flipped": ("ATFL", 11),
    "zeng_2025_adoption_flipped": ("AFL", 5),
}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        j = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                         headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == FNAME][0]
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df, meta = pyreadstat.read_sav(str(fetch()), apply_value_formats=False)
    labels = meta.column_names_to_labels
    assert len(df) == 353, len(df)
    assert not df.isna().any().any(), "the file is complete; a blank is new"

    plan = {}
    for name, (prefix, n) in BLOCKS.items():
        cols = [f"{prefix}{i}" for i in range(1, n + 1)]
        missing = [c for c in cols if c not in df.columns]
        assert not missing, (prefix, missing)
        for c in cols:                      # every item carries its stem
            assert len((labels.get(c) or "").strip()) > 6, (c, labels.get(c))
        plan[name] = cols
    items = [c for cols in plan.values() for c in cols]
    assert len(items) == len(set(items)) == 44, len(items)
    unaccounted = sorted(set(df.columns) - set(items) - set(COVS) - set(NOT_SHIPPED))
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"
    print(f"not shipped: {NOT_SHIPPED}")

    # The deposit's own total is the arithmetic check on the item set.
    assert (df[items].sum(axis=1) == df["totalvalue"]).all(), \
        "totalvalue is not the sum of the 44 shipped items"
    print("totalvalue equals the sum of the 44 items for all 353 respondents")

    df = df.rename(columns=COVS)
    df["id"] = range(1, len(df) + 1)
    cov_cols = list(COVS.values())
    for cov in cov_cols:
        v = pd.to_numeric(df[cov])
        assert (v % 1 == 0).all(), cov
        df[cov] = v.astype("Int64")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, cols in plan.items():
        t = (df[["id", *cov_cols, *cols]]
             .melt(id_vars=["id", *cov_cols], value_vars=cols,
                   var_name="item", value_name="resp"))
        t["resp"] = pd.to_numeric(t["resp"])
        assert (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        bad = sorted(set(t["resp"]) - SCALE)
        assert not bad, f"{name}: resp outside the administered 1-5 scale: {bad}"
        t = t[["id", "item", "resp", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() == 353 and t["item"].nunique() == len(cols)
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:130]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        total += len(t)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert total == 353 * 44, total


if __name__ == "__main__":
    main()
