#!/usr/bin/env python3
# Source: https://zenodo.org/records/23890112
# DOI: 10.5281/zenodo.23890112 (dataset; the record names no published paper)
# Deposit: Shiota, M., & Vornlocher, C. (2026). Seeking Support to Dampen
#   Distress: Affective, Relational, and Behavioral Outcomes of Support-Seeking
#   as an Emotion Regulation Strategy [Data set]. Zenodo.
# Data: "CopingCOVID_Study2_completedataset_8.26.21 FINAL.sav" (314 rows x
#   1,398 columns, SPSS with variable and value labels), read with pyreadstat.
#   sha256 8c0be9a7c66166186bd76fdf74003325dd6b1033b2e2f665c2b50d8eef7a16c0
#   The rest of the deposit is Mplus input/output and SPSS output (.spv).
# Codebook: none as a file. The SPSS variable labels carry each item's full
#   wording and the value labels carry the anchors; that is what is used here.
# License: CC BY 4.0 (resolved from the Zenodo record's metadata, cc-by-4.0)
#
# Found by the repos monthly sweep of 2026-11-02 (recoverable_format).
#
# Design (from the record description and the file): a COVID-era diary study.
#   Adults reported daily for about three weeks (daily surveys D1..D22); on
#   days 1, 8, 15 and 22 the survey also carried a weekly battery. Two sites,
#   identified only by the ID prefix (AZ: 139, CA: 175). No dates or
#   timestamps anywhere in the file.
#
# id: the deposit's ID, verbatim (e.g. AZ101). 42 IDs carry an analyst suffix
#   "_DROP" or "_DROPn" (e.g. AZ102_DROP8) marking participants who left the
#   study; kept as given, since it is the source's id.
#   ONE RECORD DROPPED: CA283 duplicates AZ283. The two rows agree on all 266
#   weekly/baseline battery responses they both hold, and on age, gender,
#   income and race; they differ only in the relationship and three political
#   codes, which are shifted by exactly 3 (CA283's relationship code 4 is the
#   only use of that code in the file and has no value label), and CA283
#   alone has a day-18 diary. The next most similar pair of respondents
#   agrees on 79% of shared battery cells. Read as one person entered twice;
#   AZ283 (labelled codes) is kept. 313 respondents remain.
#
# FIVE output tables, one per instrument; the item codes are the source
#   column stems, lower-cased (except the loneliness codes, see below):
#   shiota_2026_panas        PANAS, 20 adjectives, 1 = not at all ..
#       5 = extremely. Weekly, wave 1-4 = survey days 1/8/15/22. Codes are
#       panas1-panas20 in the standard PANAS order (Watson, Clark & Tellegen
#       1988), which is the order of the PANAS list below: panas1 interested,
#       2 distressed, 3 excited, 4 upset, 5 strong, 6 guilty, 7 scared,
#       8 hostile, 9 enthusiastic, 10 proud, 11 irritable, 12 alert,
#       13 ashamed, 14 inspired, 15 nervous, 16 determined, 17 attentive,
#       18 jittery, 19 active, 20 afraid. NOT panas_<adjective>: each PANAS
#       item IS its one adjective, so that code would publish the wording,
#       which the rights register blocks (renamed 2026-11-02 before upload).
#   shiota_2026_dass21       DASS-21, dass1-dass21 in DASS-21 order, coded
#       1 = not at all, 2 = rarely, 3 = sometimes, 4 = most of the time (NOT
#       the usual 0-3: shipped as recorded). Weekly, wave 1-4 = weeks 1-4.
#   shiota_2026_loneliness   UCLA Loneliness Scale (20 items, version 3
#       wording, framed "In the last week, how often did you feel..."),
#       source lone1-lone20 RENAMED ucla1-ucla20 (same order), because the
#       rights register's `^lone` matcher also hits the De Jong Gierveld
#       scale, which this is not; `ucla` hits only the UCLA-L row.
#       1 = never .. 4 = often. Weekly, wave 1-4. The nine
#       positively worded items (1, 5, 6, 9, 10, 15, 16, 19, 20) are NOT
#       reversed.
#   shiota_2026_ecr_s        ECR-S-shaped 12-item attachment measure (anxiety
#       and avoidance toward "relationship partners"), rel_<stem> codes,
#       1 = disagree strongly .. 7 = agree strongly. Baseline only, no wave.
#       Item rel_worry_abandoned ("I do not often worry about being
#       abandoned") and the avoidance items worded toward closeness are NOT
#       reversed.
#   shiota_2026_tipi         Ten-Item Personality Inventory (TIPI) word pairs
#       ("Extraverted, enthusiastic", ...), codes tipi1-tipi10 in the
#       published TIPI item order (TIPI_ORDER below; source columns are
#       B5_<first word>, in a different order), 1 = disagree strongly ..
#       7 = agree strongly. Baseline only. Reverse items (2, 4, 6, 8, 10) NOT
#       reversed. Not b5_<word>: that code carries half of each item's
#       wording, and TIPI has no rights-register row (renamed 2026-11-02).
#
# Five isolated out-of-range cells are DROPPED (data-entry slips: each occurs
#   once, in week 3, against thousands of in-range responses on the same
#   scale): PANAS_inspired_day15 = 6, PANAS_attentive_day15 = 6,
#   dass1_w3 = 5, lone16_w3 = 6, lone19_w3 = 5.
#
# NOT SHIPPED (and why):
#   * The daily coping battery (17 strategies x 2 items, e.g. EmoSupport1_D1,
#     emosup1_D3, Active1..., 22 days) -- the paper's focal measure, but the
#     file is not clean enough to ship without the authors' help: the
#     weekly-day surveys (D1/8/15/22) use different wording from the other
#     18 days for most items; day 2 has two copies of plan2 and corona2
#     (Plan2_D2 / Plan2_D2.0); detached2 is missing on day 15 and corona2 on
#     day 7; the value labels switch between "I didn't do this at all .. a
#     lot" and "Never .. Often"; and several items carry out-of-range codes
#     (active1 5-6, active2 9, plan2 10, exercise2 6, connect2 5). A follow-up
#     candidate, not a rejection.
#   * Daily single items (Daily_Affect, household, closeness, SSB, sweets,
#     sleep, exercise, nicotine, alcohol): single items, and several have
#     mislabelled columns (sleep_D9.0 is labelled as exercise minutes).
#   * COV_Wk1-4 (24 COVID-19 behaviour frequencies) and COV2_Wk1-4 (13 yes/no
#     prosocial/antisocial acts): behaviour checklists, left for scope.
#   * Attention checks (attchk_*), employment status.
#   * Free text and household roster: race_Other_TEXT (free-typed ethnicity),
#     Household_Age_1-10 and Household_Relationship_1-10 (ages and relations
#     of other household members) -- dropped in every form.
#
# Plausibility check (2026-11-02, after other deposits in this batch looked
#   generated): mean (min) inter-item r, week 1 -- PANAS positive .53 (.39),
#   negative .46 (.24); DASS-21 .44 (.16); UCLA after reversing its nine
#   positive items .47 (.08). Week 4 is the same. DASS total r(week 1, week 2)
#   = .78. TIPI extraverted vs reserved r = -.59. Apart from the CA283
#   duplicate above, no two respondents share more than 79% of battery cells.
#   Read as real data.
#
# Covariates (person level, from the baseline survey):
#   cov_site                ID prefix, AZ or CA (the deposit does not name
#                           the sites)
#   cov_gender              source code 1/2/3; NOT labelled in the deposit
#                           (128 / 185 / 1), so not relabelled
#   cov_age                 years
#   cov_race_white ... cov_race_other   checkbox flags, 1 = ticked, blank =
#                           not ticked, as in the source
#   cov_income              household income last year: <30K, 30-60K,
#                           61-100K, >100K
#   cov_relationship_status value label (Married, In a relationship, living
#                           together, ..., Never married and single)
#   cov_political_ideology, cov_political_economic, cov_political_social
#                           value label (Strongly conservative .. Strongly
#                           liberal; the source codes are 1, 5-10)
#
# Item text: shiota_2026_dass21 SHIPPED 2026-11-02 (staged, not yet uploaded)
#   by automated_finding/itemtext_verification/make_itemtext_shiota_2026.R:
#   stems from the .sav variable labels, anchors from its value labels (1 Not
#   at all .. 4 Most of the time), data_labels + study_materials; rights =
#   the DASS register `ship` row (public-domain FAQ). The other four tables
#   ship none: PANAS, UCLA-L and ECR are `block` rows; standalone TIPI has no
#   register row of its own.
#
# PII: no names, emails, dates of birth or locations. The six text columns
#   (ID, race_Other_TEXT, Household_Age_4-7) are listed and asserted below;
#   all but ID are dropped.

import hashlib
import os
import re
import sys
import urllib.parse
import urllib.request

import pandas as pd
import pyreadstat

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
FILE = "CopingCOVID_Study2_completedataset_8.26.21 FINAL.sav"
SHA256 = "8c0be9a7c66166186bd76fdf74003325dd6b1033b2e2f665c2b50d8eef7a16c0"

PANAS = ["interested", "distressed", "excited", "upset", "strong", "guilty",
         "scared", "hostile", "enthusiastic", "proud", "irritable", "alert",
         "ashamed", "inspired", "nervous", "determined", "attentive",
         "jittery", "active", "afraid"]
PANAS_DAYS = [1, 8, 15, 22]
REL = ["time_of_need", "reassurance", "pulling_back", "get_close",
       "reassurance2", "scares_people_away", "avoid_too_close",
       "worry_abandoned", "discuss_problems", "frustrated",
       "nervous_too_close", "worry_care_as_much"]
B5 = ["extraverted", "reserved", "sympathetic", "critical", "dependable",
      "disorganized", "calm", "anxious", "open", "conventional"]
# TIPI item numbers as published (Gosling, Rentfrow & Swann 2003): the codes
# are tipi1-tipi10 in that order, not the source's column order above.
TIPI_ORDER = ["extraverted", "critical", "dependable", "anxious", "open",
              "reserved", "sympathetic", "disorganized", "calm",
              "conventional"]
assert sorted(TIPI_ORDER) == sorted(B5)
RACE = ["White", "Black", "Hispanic", "EastAsian", "SouthAsian",
        "NativeAmerican", "MiddleEastern", "Other"]
SLIPS = {"PANAS_inspired_day15": 6, "PANAS_attentive_day15": 6,
         "dass1_w3": 5, "lone16_w3": 6, "lone19_w3": 5}
TEXT_COLS = {"ID", "race_Other_TEXT", "Household_Age_4", "Household_Age_5",
             "Household_Age_6", "Household_Age_7"}


def _raw():
    """SHIOTA_RAW (path to the .sav), else fetch into raw_cache, sha256-checked."""
    dest = os.environ.get("SHIOTA_RAW")
    if not dest:
        d = os.path.join(REPO_ROOT, "automated_finding", "runs", "raw_cache",
                         "shiota_2026")
        os.makedirs(d, exist_ok=True)
        dest = os.path.join(d, "shiota_2026.sav")
        if not os.path.exists(dest):
            url = ("https://zenodo.org/api/records/23890112/files/"
                   f"{urllib.parse.quote(FILE)}/content")
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"})
            with urllib.request.urlopen(req, timeout=300) as r:
                blob = r.read()
            with open(dest, "wb") as fh:
                fh.write(blob)
    with open(dest, "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == SHA256, f"{FILE} changed"
    return dest


def _label(meta, col, s):
    labs = meta.variable_value_labels[col]
    out = s.map(labs)
    assert out[s.notna()].notna().all(), (col, set(s.dropna()) - set(labs))
    return out


def tables(df):
    """table -> (list of (wave or None, {source col: item code}), scale)."""
    out = {}
    out["shiota_2026_panas"] = (
        [(w + 1, {f"PANAS_{a}_day{d}": f"panas{i}"
          for i, a in enumerate(PANAS, start=1)})
         for w, d in enumerate(PANAS_DAYS)], [1, 2, 3, 4, 5])
    out["shiota_2026_dass21"] = (
        [(w, {f"dass{i}_w{w}": f"dass{i}" for i in range(1, 22)})
         for w in range(1, 5)], [1, 2, 3, 4])
    out["shiota_2026_loneliness"] = (
        [(w, {f"lone{i}_w{w}": f"ucla{i}" for i in range(1, 21)})
         for w in range(1, 5)], [1, 2, 3, 4])
    out["shiota_2026_ecr_s"] = (
        [(None, {f"REL_{s}": f"rel_{s}" for s in REL})], list(range(1, 8)))
    out["shiota_2026_tipi"] = (
        [(None, {f"B5_{s}": f"tipi{TIPI_ORDER.index(s) + 1}" for s in B5})], list(range(1, 8)))
    return out


def convert():
    df, meta = pyreadstat.read_sav(_raw())
    assert df.shape == (314, 1398), df.shape
    text = {c for c in df.columns if pd.api.types.is_string_dtype(df[c])}
    print(f"  text columns examined: {len(text)}")
    assert text == TEXT_COLS, text
    assert df["ID"].is_unique

    # the duplicate record (see header)
    a = df.loc[df["ID"] == "AZ283"].iloc[0]
    b = df.loc[df["ID"] == "CA283"].iloc[0]
    batt = [c for c in df.columns
            if re.match(r"(PANAS_|dass\d|lone\d|REL_|B5_)", c)]
    both = a[batt].notna() & b[batt].notna()
    assert both.sum() == 266 and (a[batt][both] == b[batt][both]).all()
    df = df.loc[df["ID"] != "CA283"].reset_index(drop=True)

    for col, v in SLIPS.items():
        assert (df[col] == v).sum() == 1, col
        df.loc[df[col] == v, col] = pd.NA

    df["id"] = df["ID"]
    df["cov_site"] = df["ID"].str[:2]
    assert set(df["cov_site"]) == {"AZ", "CA"}
    df["cov_gender"] = df["gender"].astype("Int64")
    df["cov_age"] = df["age"].astype("Int64")
    race_cov = []
    for r in RACE:
        c = "cov_race_" + re.sub(r"(?<!^)(?=[A-Z])", "_", r).lower()
        assert set(df[f"race_{r}"].dropna()) <= {1.0}
        df[c] = df[f"race_{r}"].astype("Int64")
        race_cov.append(c)
    df["cov_income"] = _label(meta, "Income", df["Income"])
    df["cov_relationship_status"] = _label(meta, "relationship_status",
                                           df["relationship_status"])
    pol = []
    for c in ["political_ideology", "political_economic", "political_social"]:
        df["cov_" + c] = _label(meta, c, df[c])
        pol.append("cov_" + c)
    covs = (["cov_site", "cov_gender", "cov_age"] + race_cov
            + ["cov_income", "cov_relationship_status"] + pol)

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, (waves, scale) in tables(df).items():
        parts = []
        for wave, ren in waves:
            assert all(c in df.columns for c in ren), table
            w = df[["id"] + covs + list(ren)].rename(columns=ren)
            long = w.melt(id_vars=["id"] + covs, value_vars=list(ren.values()),
                          var_name="item", value_name="resp")
            if wave is not None:
                long["wave"] = wave
            parts.append(long)
        long = pd.concat(parts, ignore_index=True)
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        has_wave = "wave" in long.columns
        lead = ["id", "item", "resp"] + (["wave"] if has_wave else [])
        long = long[lead + covs]
        long = long.sort_values(["id"] + (["wave"] if has_wave else [])
                                + ["item"]).reset_index(drop=True)
        assert not long.duplicated(
            ["id", "item"] + (["wave"] if has_wave else [])).any()
        assert long["resp"].isin(scale).all(), table
        assert set(long["resp"]) == set(scale), table
        assert long["id"].nunique() >= 100

        items = sorted(long["item"].unique())
        checks = run_qc(long, permitted_values={i: scale for i in items})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")

        long.to_csv(os.path.join(OUT_DIR, table + ".csv"), index=False)
        print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"waves={long['wave'].nunique() if has_wave else '-'} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
