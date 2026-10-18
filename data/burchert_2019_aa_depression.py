#!/usr/bin/env python3
# Source: https://zenodo.org/records/3384860
# DOI: 10.5281/zenodo.3384860
# Data: Dataset_14-day_AA_depression_symptoms_mood_and_PHQ-9.csv
# License: CC BY 4.0 (verified on the Zenodo record)
# Reference: Burchert, S., Kerber, A., Zimmermann, J., & Knaevelsrud, C.
#   (2019). 14-day smartphone ambulatory assessment of depression symptoms and
#   mood dynamics in a general population sample.
#
# **The lead row's "16,150 participants" is the ROW count.** There are 185
# respondents, each contributing 11-686 ambulatory assessments over 14 days,
# so the file is one person-occasion per row. Two instruments with different
# structures share it:
#
#   phq1..phq9  PHQ-9, 0-3  -- a BASELINE, repeated verbatim on every one of a
#               respondent's rows. Verified: each respondent has exactly ONE
#               distinct value per phq item across all their rows. So it
#               de-duplicates to one row per person (185 x 9); melting it as
#               deposited would have shipped the same nine answers up to 686
#               times each and inflated the table to ~143,000 rows.
#   q1..q47     17 momentary mood items, 0-4 -- the genuinely repeated
#               measures, carried long with `wave` as the occasion index.
#
# `wave` is the within-person occasion order taken from `time`, 1..n, which is
# the numeric order the standard asks for. `phq.day` is a fractional day
# offset (it runs negative, -116..212, so it is an offset from an anchor and
# not a usable occasion index) and is dropped.
#
# RIGHTS. The PHQ/GAD screener family is verdict `ship` in
# itemtext/instrument_rights_register.csv, so the PHQ-9 ships.
# `happiness.score` is DROPPED, for two independent reasons: it is a single
# column (a one-item table is never shipped), and the register's Subjective
# Happiness Scale row BLOCKS on the bare matcher `happiness`, which this
# column's name matches. It is not in fact the 4-item SHS -- it is a single
# 0-4 momentary rating, and it duplicates no q item (checked, max agreement
# with any q column well under 0.9) -- but there is no reason to take the risk
# for a column that cannot ship anyway. Recorded here so the next pass does
# not re-derive it.
#
# Item text: NOT shipped. The file is a bare CSV with no label level of any
# kind (not an SPSS/Stata file, no codebook in the deposit), and the item
# codes are positional (`q1`..`q47`, with q15 and q17-q45 absent). The PHQ-9
# wording is canonical and could be supplied, but the 17 mood items would need
# the published paper's appendix to know what was asked. Where the text is:
# the paper's own instrument description, not this deposit.

import os

import pandas as pd


# --- raw input -------------------------------------------------------------
# Self-contained by design: the script fetches the deposit itself and caches
# it next to this file, so it re-runs in a fresh checkout (which is what
# metadata/covariate_labels/harvest.py does). Set BURCHERT_RAW to point at an
# already-downloaded copy instead.
_URL = ("https://zenodo.org/api/records/3384860/files/Dataset_14-day_AA_depression_symptoms_mood_and_PHQ-9.csv/content")
_NAME = "zenodo_3384860__aa_depression.csv"


def _raw():
    override = os.environ.get("BURCHERT_RAW")
    if override:
        return override if os.path.isfile(override) else os.path.join(override, _NAME)
    cache = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "..", "automated_finding", "runs", "raw_cache")
    os.makedirs(cache, exist_ok=True)
    dest = os.path.join(cache, _NAME)
    if not os.path.exists(dest):
        import urllib.request
        req = urllib.request.Request(
            _URL, headers={"User-Agent":
                           "IRW-Finder/1.0 (ben.domingue@gmail.com)"})
        with urllib.request.urlopen(req, timeout=300) as r, \
                open(dest, "wb") as fh:
            fh.write(r.read())
    return dest

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

PHQ = [f"phq{i}" for i in range(1, 10)]
MOOD = [f"q{i}" for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                          16, 46, 47]]
PHQ_SCALE = {0.0, 1.0, 2.0, 3.0}
MOOD_SCALE = {0.0, 1.0, 2.0, 3.0, 4.0}


def convert():
    df = pd.read_csv(_raw())
    print(f"raw: {df.shape}")

    assert (df["user_id"] == df["id"]).all(), "user_id and id disagree"
    n_people = df["user_id"].nunique()
    print(f"{len(df)} rows over {n_people} respondents "
          f"(median {int(df.groupby('user_id').size().median())} occasions each)")

    # The PHQ-9 is a baseline: prove it is constant within respondent before
    # collapsing it, rather than assuming from the file's shape.
    per_person = df.groupby("user_id")[PHQ].nunique().max()
    assert (per_person <= 1).all(), \
        f"PHQ varies within respondent: {per_person[per_person > 1].to_dict()}"
    print("PHQ-9 is constant within respondent -> collapsed to one row each")

    covs = (df.groupby("user_id")
              .agg(cov_age=("age", "first"), cov_sex=("sex", "first"))
              .reset_index().rename(columns={"user_id": "id"}))

    accounted = set(["user_id", "id", "age", "sex", "time", "period.name",
                     "start.time"]) | set(PHQ) | set(MOOD)
    skipped = {}
    for c in df.columns:
        if c in accounted:
            continue
        if c == "happiness.score":
            skipped[c] = ("single column, and matches the register's blocked "
                          "SHS row on the bare `happiness` matcher")
        elif c == "phq.day":
            skipped[c] = "fractional day offset, runs negative; not an occasion index"
        elif c.startswith("Unnamed"):
            skipped[c] = "row index from the CSV writer"
        else:
            skipped[c] = "not an item or covariate"
    for c, why in sorted(skipped.items()):
        print(f"  skip {c:18} {why}")
    assert accounted | set(skipped) == set(df.columns), "books do not balance"

    written = set()

    # --- PHQ-9, one row per respondent ---
    base = df.drop_duplicates("user_id")[["user_id"] + PHQ].rename(
        columns={"user_id": "id"})
    long = base.melt(id_vars="id", var_name="item", value_name="resp"
                     ).dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(float)
    bad = set(long["resp"].unique()) - PHQ_SCALE
    assert not bad, f"PHQ: {sorted(bad)} outside 0-3"
    long = long.merge(covs, on="id", how="left")[
        ["id", "item", "resp", "cov_age", "cov_sex"]]
    assert long["item"].nunique() > 1 and long["id"].nunique() >= 100
    name = "burchert_2019_phq9"
    written.add(name)
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")

    # --- momentary mood, long with an occasion index ---
    d = df[["user_id", "time"] + MOOD].copy()
    d["time"] = pd.to_datetime(d["time"], errors="coerce")
    d = d.sort_values(["user_id", "time"])
    d["wave"] = d.groupby("user_id").cumcount() + 1
    long = d.melt(id_vars=["user_id", "wave"], value_vars=MOOD,
                  var_name="item", value_name="resp"
                  ).dropna(subset=["resp"]).rename(columns={"user_id": "id"})
    long["resp"] = long["resp"].astype(float)
    bad = set(long["resp"].unique()) - MOOD_SCALE
    assert not bad, f"mood: {sorted(bad)} outside 0-4"
    long = long.merge(covs, on="id", how="left")[
        ["id", "item", "resp", "wave", "cov_age", "cov_sex"]]
    assert long["item"].nunique() > 1 and long["id"].nunique() >= 100
    name = "burchert_2019_momentary_mood"
    assert name not in written, f"duplicate output name {name}"
    long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
    print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} waves={long['wave'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
