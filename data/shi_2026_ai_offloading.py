#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/QKL3Q6
# DOI (data): 10.7910/DVN/QKL3Q6
# Data: Shi, M. (2026). Within-person dynamics of generative AI cognitive
#   offloading, metacognitive calibration and independent problem-solving
#   performance. Harvard Dataverse. File "analysis_wide.tab" (original CSV),
#   1,166 undergraduates, six waves over one academic year.
#   No article is linked from the deposit (checked 2026-11-07).
# License: CC0 1.0, verified on the deposit (Dataverse API, latestVersion.license).
#
# Found by the repos sweep of 2026-11-07 (Step 2b recoverable_format).
#
# ONE output table:
#   shi_2026_ai_offloading  off1..off6 at each of the six waves: "the
#     frequency with which they delegated coursework-related cognitive
#     activities to generative AI" (deposit description). Integer 1-7 at every
#     wave; the anchors are not documented in the deposit. `wave` = 1..6 from
#     the column suffix (_1 .. _6).
# Covariates, time-invariant: age, gender, stem (0/1), year of study,
#   university (U1-U3, as given), counterbalance group, gpa_z and
#   ai_literacy_z (standardised, as deposited). Time-varying, per wave:
#   ai_days (days of AI use reported that wave) and nonuser (0/1).
# Dropped: the per-wave problem-solving and confidence aggregates (O, B, P, C,
#   AAI, Pp1-3, Bp1-3, Op1-3: percentages, biases and averages over the 24
#   items, never the item responses themselves), the dummy duplicates male,
#   U2 and U3, and the summaries n_waves and t_last.
# `id` is the row index: the deposit's "P" + 6-digit codes look like platform
#   participant ids, which the IRW replaces rather than ships.
#
# Item text: NOT SHIPPED. The six offloading stems are not in the deposit,
#   and no article is linked.

import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("SHI_RAW", "analysis_wide.csv")
STATIC = {"age": "cov_age", "gender": "cov_gender", "stem": "cov_stem", "year": "cov_year_of_study",
          "university": "cov_university", "counterbalance_group": "cov_counterbalance_group",
          "gpa_z": "cov_gpa_z", "ai_literacy_z": "cov_ai_literacy_z"}
WAVE_COVS = {"ai_days": "cov_ai_days", "nonuser": "cov_nonuser"}
AGG = ["O", "B", "P", "C", "AAI", "Pp1", "Pp2", "Pp3", "Bp1", "Bp2", "Bp3", "Op1", "Op2", "Op3"]
ITEMS = [f"off{i}" for i in range(1, 7)]


def convert():
    df = pd.read_csv(RAW)
    assert df.shape == (1166, 146), df.shape
    assert df["id"].is_unique
    df["rid"] = range(1, len(df) + 1)
    used = {"id", "rid", "male", "U2", "U3", "n_waves", "t_last"} | set(STATIC)
    parts = []
    for w in range(1, 7):
        cols = {f"{i}_{w}": i for i in ITEMS}
        wc = {f"{k}_{w}": v for k, v in WAVE_COVS.items()}
        used |= set(cols) | set(wc) | {f"{a}_{w}" for a in AGG}
        part = df[["rid"] + list(STATIC) + list(wc) + list(cols)].rename(columns={**STATIC, **wc, **cols})
        part["wave"] = w
        parts.append(part)
    assert used == set(df.columns), set(df.columns) - used
    wide = pd.concat(parts, ignore_index=True).rename(columns={"rid": "id"})
    covs = list(STATIC.values()) + list(WAVE_COVS.values())
    long = wide.melt(id_vars=["id", "wave"] + covs, var_name="item", value_name="resp")
    long = long[long["resp"].notna()].copy()
    assert (long["resp"] % 1 == 0).all()
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"]) <= set(range(1, 8)), set(long["resp"])
    long = long[["id", "item", "resp", "wave"] + covs].sort_values(["id", "wave", "item"])
    assert not long.duplicated(["id", "item", "wave"]).any()
    checks = run_qc(long, permitted_values={c: list(range(1, 8)) for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    name = "shi_2026_ai_offloading"
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"waves={long['wave'].nunique()}")


if __name__ == "__main__":
    convert()
