#!/usr/bin/env python3

# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/HBQLA6
# DOI: 10.7910/DVN/HBQLA6
#   Enke, B., Gneezy, U., Hall, B., Martin, D., Nelidov, V., Offerman, T., &
#   Van de Ven, J. (2021). Replication data for: Cognitive Biases: Mistakes or
#   Missing Stakes? [Dataset]. Harvard Dataverse. Published as Review of
#   Economics and Statistics 105(4), 818-832 (2023).
# Data: "experimental_data.dta" -- 1,236 Kenyan university students, each
#   answering four cognitive-bias problems drawn from a pool of 18: six CRT
#   items, four Bayesian-reasoning (BRN) items, four anchoring items and four
#   Wason selection items.
# License: CC0 1.0 (verified on the Dataverse record, 2026-10-19).
# Item text: NOT shipped. The deposit carries the data, four .do files and a
#   readme.pdf -- no problem wording at any level, and the 18 codes
#   (CRT1..CRT6, BRN1..4, Anchoring1..4, Wason1..4) are positional. The
#   problems themselves are in the paper's appendix. Both the label level and
#   the deposit's file list were checked.
#
# FOUR tables, one per bias type, because CRT, Bayesian reasoning, anchoring
#   and the Wason selection task are four different measurement instruments
#   and the data standard gives each its own file. The cost is visible and
#   worth stating: each subject answers two problems of each of TWO types, so
#   every table is about 618 subjects x 2 items rather than one 18-item table.
#   The design is what makes it so -- nobody answered all 18.
#
#   enke_2023_crt         6 items, 620 subjects
#   enke_2023_brn         4 items, 618 subjects
#   enke_2023_anchoring   4 items, 615 subjects
#   enke_2023_wason       4 items, 619 subjects
#
# `resp` is the deposit's own `correct`, 0/1, complete for all 4,944 responses. The raw answers are NOT shipped -- they
#   are numeric for CRT/BRN/anchoring (`response`) and free text for Wason
#   (`wason_response`, e.g. "4 Card, Drinking Juice"), so a single `resp_raw`
#   column would mix a number scale with a string across items of one table.
#   The scoring is the source's, not ours: `correct` is in the deposit.
#
# The design is within-subject, and that is what `treat` carries. Every
#   subject answers two problems of one bias type with NO incentives, then two
#   of a second type under incentives -- `condition` is "no" on the first pair
#   and "low" or "high" on the second, and that varies WITHIN subject for all
#   1,236 of them. So `treat` = 1 where the row was incentivised, which is the
#   paper's manipulation, and the person-level assignment of which incentive
#   (low vs high) ships as cov_high_incentives. 636 subjects got low, 600 high.
# trial_number: 1-4, from the deposit's `j` (11, 12, 21, 22) -- the order the
#   four problems were answered in, first block then second.
# rt: `response_time`, already in seconds (4.2s to 3,228.8s).
#
# id: the deposit's own 1-1,236 subject number, which is a study-internal
#   index, not a platform account id. Kept so the four rows of one subject
#   link.
# Covariates: cov_age, cov_male, cov_education, cov_school_year, cov_gpa,
#   cov_stem, cov_income, cov_consumption, cov_raven, cov_iq,
#   cov_high_incentives. cov_raven is the post-experimental Raven matrices
#   score (0-8) and cov_iq its z-score, both the deposit's own; cov_income and
#   cov_consumption are in Kenyan shillings as given.
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
    "IRW_RAW_DIR",
    REPO_ROOT / "automated_finding" / "runs" / "dvn_batch" / "hbqla6" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FILE_ID, FNAME = 4810316, "experimental_data.dta"
COVS = {"age": "cov_age", "male": "cov_male", "education": "cov_education",
        "school_year": "cov_school_year", "gpa": "cov_gpa",
        "stem": "cov_stem", "income": "cov_income",
        "consumption": "cov_consumption", "raven": "cov_raven",
        "iq": "cov_iq", "high_incentives": "cov_high_incentives"}
TRIAL = {11: 1, 12: 2, 21: 3, 22: 4}
SCALE = {0, 1}
TABLES = {"enke_2023_crt": "CRT", "enke_2023_brn": "BRN",
          "enke_2023_anchoring": "Anchor", "enke_2023_wason": "Wason"}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        url = ("https://dataverse.harvard.edu/api/access/datafile/"
               f"{FILE_ID}?format=original")
        r = requests.get(url, headers=UA, timeout=600)
        r.raise_for_status()
        p.write_bytes(r.content)
    return p


def main():
    df = pd.read_stata(fetch(), convert_categoricals=False)
    assert len(df) == 4944, len(df)
    assert df["id"].nunique() == 1236
    assert (df.groupby("id").size() == 4).all(), "not four problems per subject"
    assert not df.duplicated(["id", "spec_task"]).any()
    assert set(df["spec_task"].unique()) == {
        f"{p}{i}" for p, n in (("CRT", 6), ("BRN", 4), ("Anchoring", 4),
                               ("Wason", 4)) for i in range(1, n + 1)}
    assert not df["correct"].isna().any() and set(df["correct"]) == {0.0, 1.0}
    assert not df["response_time"].isna().any()

    # The within-subject manipulation: no incentives in block 1, incentives in
    # block 2. Assert the shape rather than trusting the column.
    assert (df.groupby("id")["condition"].nunique() == 2).all()
    assert (df.groupby("id")["high_incentives"].nunique() == 1).all()
    assert set(df["condition"]) == {"no", "low", "high"}
    df["treat"] = (df["condition"] != "no").astype(int)
    assert (df.groupby("id")["treat"].sum() == 2).all(), \
        "every subject should have exactly two incentivised problems"

    df = df.rename(columns=COVS)
    cov_cols = list(COVS.values())
    df["trial_number"] = df["j"].map(TRIAL).astype(int)
    assert set(df["trial_number"]) == {1, 2, 3, 4}
    for cov in cov_cols:
        assert not df[cov].isna().any(), cov
        v = pd.to_numeric(df[cov])
        df[cov] = v.astype("Int64") if (v % 1 == 0).all() else v

    long = df.rename(columns={"spec_task": "item", "correct": "resp",
                              "response_time": "rt"})
    long["id"] = pd.to_numeric(long["id"]).astype(int)
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= SCALE
    assert set(long["task"]) == set(TABLES.values()), set(long["task"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, task in TABLES.items():
        t = long[long["task"] == task][
            ["id", "item", "resp", "treat", "rt", "trial_number", *cov_cols]]
        assert not t.duplicated(["id", "item"]).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        assert (t.groupby("id").size() == 2).all(), \
            f"{name}: a subject answered other than two problems of this type"
        checks = run_qc(t, permitted_values=SCALE)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:150]}")
        report = irw_validate.validate_frame(
            t, label=name, profile="upload",
            context={"permitted_values": SCALE})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        total += len(t)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")
    assert total == 4944, total


if __name__ == "__main__":
    main()
