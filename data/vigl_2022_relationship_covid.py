#!/usr/bin/env python3
# Source: https://osf.io/f8m7a/
# DOI: 10.1371/journal.pone.0264511
# Paper: Vigl J, Strauss H, Talamini F, Zentner M (2022). Relationship
#   satisfaction in the early stages of the COVID-19 pandemic: A cross-national
#   examination of situational, dispositional, and relationship factors.
#   PLOS ONE 17(3): e0264511.
# Data: OSF node f8m7a, one file love_corona_data.csv (';'-separated, decimal
#   commas), 3,243 rows x 129 columns. No codebook in the deposit; the paper's
#   Method section documents the scales.
# License: CC BY 4.0, set on node f8m7a by Julia Vigl on 2026-11-12 after an
#   IRW ask (verified via the OSF API). She also granted inclusion and
#   reformatting by email the same day. The parent node v79je carries no
#   licence, but the data file sits on f8m7a. Logged in
#   processing_notes/outreach/outreach_log.csv.
#
# Found by the PLOS monthly run of 2026-11-09 (licence-blocked then, see
# automated_finding/license_blocked_candidates.csv).
#
# Sample (paper, Participants): 3,243 adults in a romantic relationship, April
# to June 2020, online LimeSurvey in English, Italian and German; 67 countries,
# mostly Italy, the US, the UK and Germany/Switzerland/Austria. The file is
# the paper's final analysis sample (3,243 rows), after its exclusions.
#
# FIVE output tables:
#   vigl_2022_ras_before    Relationship Assessment Scale (Hendrick 1988), 7
#                           items RAS1-RAS7, plus the one added sexual
#                           satisfaction item `sexsat`, rated RETROSPECTIVELY
#                           for before the pandemic. 1-5.
#   vigl_2022_ras_now       The same 8 items rated for now (at the survey). 1-5.
#     "Participants were asked to provide two separate ratings: one
#     retrospective rating of their relationship satisfaction before the
#     outbreak of the pandemic, and one rating of their current relationship
#     satisfaction. The answers were given on a 5-point scale, with higher
#     scores indicating higher relationship satisfaction." Alpha is reported
#     on the eight-item measure, so `sexsat` belongs with the RAS here.
#     TWO tables, not one with `wave`: both ratings were given at the same
#     sitting, so `wave` would present a retrospective recall as a second
#     measurement occasion (precedent: data/mazzini_2026_arousal_regulation.py).
#     Both tables carry the same `id`, so a user who wants the pair can join.
#     Item codes drop the _bef/_now suffix so the two tables share item names.
#     Direction: RAS4 and RAS7 are reverse-keyed in the published RAS, but the
#     deposit stores them ALREADY reverse-scored -- its own composites RAS_0 /
#     RAS_1 equal the plain mean of the eight stored items in every row
#     (asserted), and RAS4 rises with RAS1. Shipped as stored.
#   vigl_2022_bfi2xs        BFI-2-XS (Soto & John 2017; German version
#                           Rammstedt et al.), 15 items BFI2XS_{E,A,C,N,O}{1-3},
#                           1-5. Also stored already reverse-scored: BFI_E..
#                           BFI_O equal the plain mean of their three items
#                           (asserted). Shipped as stored.
#   vigl_2022_pandemic_worries  6 pandemic-related worries (spread, health of
#                           others, own health, work, money, friends), "on a
#                           10-point scale ... (1 = not worried at all,
#                           10 = very worried; alpha = .70 to .74)".
#   vigl_2022_shared_time_change  The four items the paper combines into its
#                           "decrease in shared time" index (alpha .79-.83):
#                           contactchange (physical contact, -3 = less than
#                           half of the time, 0 = same as before, 3 = twice as
#                           much) and activitieschange_{talks,activities,sex}
#                           (-4 much less than before .. 0 same .. 4 much more).
#                           Shipped in the source direction (more = higher);
#                           the paper reverses them for its index, IRW does
#                           not. Two scales in one table, as the paper's own
#                           composite has them; per-item range differs.
#   Item codes are the source headers except two, renamed because
#   irw_lint_covariates.py reads the header as a covariate: worries_work ->
#   worries_livelihood (worry about one's work situation),
#   activitieschange_sex -> activitieschange_intimacy (frequency of sex with
#   the partner).
#
# NOT SHIPPED:
#   ECR (8 items ECRRD_Anx1-4, ECRRD_Av1-4): HELD. Stored 0-7, eight values,
#     every item with 68-274 zeros; the ECR short form is a 7-point scale and
#     the paper gives no response range for it. The composites ECR_Anx/ECR_Av
#     equal the plain mean INCLUDING the zeros, so the depositors treat 0 as a
#     scale point, but whether 0-7 is the administered scale or a recode is
#     unconfirmed (datastandard.md: silence is not confirmation). Ask the
#     depositor; ship on her answer.
#   activitieschange_arg (arguing) and activitieschange_self (time for
#     oneself): single items the paper keeps separate; below the 3-item floor.
#   sexsat on its own: shipped inside the RAS tables (see above).
#   Division-of-labour block (cooking/homemaking/admin/maintenance/childcare
#     _bef/_now and their *_cod twins) and satisfactiondomestic/kids: not
#     described in the paper ("Other measures were administered ... which are
#     not relevant"), raw vs _cod coding unexplained, blank for many rows.
#   homefeel_privacy, restrictionscountry, workchange*, time-out hours,
#     homesize: single items or counts, not a scale.
#   All composites: RAS_bef, RAS_now, RAS_0, RAS_1, BFI_*, ECR_*, ch_cont_rev.
#
# `id`: the ROW INDEX (1..3243), not PersonID. PersonID is a self-generated
#   respondent code (letters plus digits, 7-11 characters) of the kind built
#   from initials and birthday parts, so it is not carried in any form. It is
#   also not unique: one code appears on two rows submitted 8 minutes apart
#   with different gender and different answers -- two people, most likely a
#   couple who generated the same code -- and the paper counts both (its N is
#   3,243 = the row count), so both are kept as distinct ids.
#
# Covariates (codes confirmed by matching the paper's reported percentages):
#   cov_gender         1 = woman (73.4%, paper "73.4% women"), 2 = man.
#                      Non-binary respondents were excluded by the authors.
#   cov_age            years, 18-79 (paper: M 31, SD 11.21, range 18-79).
#   cov_cohabiting     1 = lives with partner (56.3%), 0 = not.
#   cov_partner_distance  0 = cohabiting (56.3%), 1 = apart, same region
#                      (28.7%), 2 = different regions (15.0%).
#   cov_children       1 = has children (20%), 0 = none.
#   cov_relationship_type  2 = open (3.7%), 3 = committed (73%), 4 = married
#                      (23.4%).
#   cov_rel_duration   relationship duration in years (paper M 6.30), decimal
#                      comma parsed.
#   cov_country_group  1 = Germany/Switzerland/Austria (n=775), 2 = Italy
#                      (1,094), 3 = US (776), 4 = UK (302), 5 = other (296);
#                      counts equal the paper's.
#   cov_language       survey language: de, en, it.
#   NOT carried: `city` (size of living area, 3 codes; the paper names three
#   categories but not their coding), sexorientation, education, job,
#   partnergender, typeof_relation -- codes undocumented. submitdate/
#   datestamp: per-person timestamps, not carried.
#
# Imputation: none stated ("imput" absent from the article). Every shipped item
#   column is complete and integer within its documented range (asserted).
#
# Item text: not shipped -- no wording in the deposit. The ECR items are quoted
#   in the paper (held table); RAS and BFI-2-XS wording lives in the published
#   instruments; the worries items are in the paper's S1 File, Table S3d.
#
# PII: string columns PersonID (dropped, see `id`), lang (carried as
#   cov_language), submitdate/datestamp (dropped), and survey fields stored as
#   strings because of blanks/decimal commas (numeric codes only, none
#   carried as free text). No names, emails, IPs, coordinates or postal codes.

import os
import socket
import sys
import tempfile

import numpy as np
import pandas as pd
import requests
import urllib3.util.connection as _uc

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
URL = "https://osf.io/download/rv92p/"
RAW = os.environ.get("VIGL_RAW", "")
N_ROWS = 3243

COVS = {
    "gender": "cov_gender",
    "age": "cov_age",
    "cohabiting": "cov_cohabiting",
    "distancepartner": "cov_partner_distance",
    "Children": "cov_children",
    "relationtype": "cov_relationship_type",
    "rel_dur": "cov_rel_duration",
    "target_country": "cov_country_group",
    "lang": "cov_language",
}

RAS_ITEMS = [f"RAS{i}" for i in range(1, 8)] + ["sexsat"]


def ras_cols(when):
    sfx = {"bef": "_bef", "now": "_now"}[when]
    cols = {f"RAS{i}{sfx}": f"RAS{i}" for i in range(1, 8)}
    cols["sexsat_before" if when == "bef" else "sexsat_now"] = "sexsat"
    return cols


TABLES = {
    "vigl_2022_ras_before": (ras_cols("bef"), range(1, 6)),
    "vigl_2022_ras_now": (ras_cols("now"), range(1, 6)),
    "vigl_2022_bfi2xs": (
        {f"BFI2XS_{d}{i}": f"BFI2XS_{d}{i}" for i in (1, 2, 3) for d in "EACNO"},
        range(1, 6)),
    "vigl_2022_pandemic_worries": (
        {"worries_spread": "worries_spread",
         "worries_healthothers": "worries_healthothers",
         "worries_healthself": "worries_healthself",
         "worries_work": "worries_livelihood",  # renamed: lint reads 'work' as a covariate
         "worries_money": "worries_money",
         "worries_friends": "worries_friends"},
        range(1, 11)),
    "vigl_2022_shared_time_change": (
        {"contactchange": "contactchange",
         "activitieschange_talks": "activitieschange_talks",
         "activitieschange_activities": "activitieschange_activities",
         # renamed: lint reads 'sex' as a covariate (gender)
         "activitieschange_sex": "activitieschange_intimacy"},
        None),  # per-item ranges, checked below
}
ITEM_RANGES = {"contactchange": range(-3, 4)}  # the rest -4..4


def num(s):
    """Decimal-comma string column -> float ('' and ' ' -> NaN)."""
    s = s.astype(str).str.strip().str.replace(",", ".", regex=False)
    s = s.where(~s.isin(["", "."]))
    return pd.to_numeric(s, errors="raise")


def fetch():
    if RAW:
        return RAW
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(URL, headers={"User-Agent": "IRW-Finder/1.0"},
                     timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), "love_corona_data.csv")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def check_composites(df):
    for when, comp in (("bef", "RAS_0"), ("now", "RAS_1")):
        cols = list(ras_cols(when))
        assert np.allclose(df[cols].mean(axis=1), num(df[comp])), comp
    for d in "EACNO":
        cols = [f"BFI2XS_{d}{i}" for i in (1, 2, 3)]
        assert np.allclose(df[cols].mean(axis=1), num(df[f"BFI_{d}"])), d


def convert():
    df = pd.read_csv(fetch(), sep=";")
    assert df.shape == (N_ROWS, 129), df.shape
    strings = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: {len(df.columns)} columns examined, {len(strings)} "
          f"string column(s)")
    assert len(df.columns) > 0 and len(strings) > 0
    # PersonID is replaced by the row index; it is not unique (see header).
    assert df["PersonID"].nunique() == N_ROWS - 1
    check_composites(df)

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    cov = df[["id"] + list(COVS)].rename(columns=COVS)
    cov["cov_rel_duration"] = num(cov["cov_rel_duration"])
    assert cov.drop(columns="cov_rel_duration").notna().all().all()
    assert set(cov["cov_gender"]) == {1, 2}
    assert round((cov["cov_gender"] == 1).mean(), 3) == 0.734  # paper: 73.4% women
    assert set(cov["cov_language"]) == {"de", "en", "it"}
    assert (cov["cov_country_group"].value_counts().sort_index().tolist()
            == [775, 1094, 776, 302, 296])
    assert ((cov["cov_cohabiting"] == 1)
            == (cov["cov_partner_distance"] == 0)).all()
    cov_cols = [c for c in cov.columns if c != "id"]

    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for name, (mapping, rng) in TABLES.items():
        assert len(name) <= 40, name
        sub = df[["id"] + list(mapping)].rename(columns=mapping)
        items = list(mapping.values())
        assert sub[items].notna().all().all(), name
        for it in items:
            ok = rng if rng is not None else ITEM_RANGES.get(it, range(-4, 5))
            assert sub[it].isin(ok).all(), (name, it)
        long = sub.melt(id_vars=["id"], var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(int)
        long = long.merge(cov, on="id", how="left", validate="many_to_one")
        long = long[["id", "item", "resp"] + cov_cols]
        assert long["id"].nunique() == N_ROWS
        assert len(long) == N_ROWS * len(items)
        assert not long.duplicated(["id", "item"]).any()
        pv = list(rng) if rng is not None else list(range(-4, 5))
        checks = run_qc(long, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {name} {c.name}: {c.detail[:160]}")
        long.to_csv(os.path.join(OUT_DIR, name + ".csv"), index=False)
        total += len(long)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-"
              f"{long['resp'].max()}")
    print(f"{len(TABLES)} tables, {total} responses")


if __name__ == "__main__":
    convert()
