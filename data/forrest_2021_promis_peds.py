#!/usr/bin/env python3
# Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/QOO7QX
# DOI: 10.7910/DVN/QOO7QX
# License: CC0 1.0 (stated on the Harvard Dataverse landing page)
# GitHub issue: #233
#
# "PROMIS Pediatric Measure Evaluation" (Forrest, deposited 2020, published on
# Dataverse 2021). Cross-sectional calibration samples drawn from school,
# clinic, and internet-panel settings, used to develop and IRT-calibrate ten
# PROMIS pediatric item banks. Each bank was fielded in two editions -- a
# child self-report and a parent-proxy report -- shipped here as separate
# files, since the two editions have different item wording (the proxy items
# carry a `_PX`/`_Proxy` suffix in the source) and were calibrated separately.
# That gives 10 constructs x 2 reporters = 20 tables.
#
# `authorname_year` is taken from the deposit itself (Forrest, 2021) rather
# than from a per-construct paper: the deposit spans six publications from
# 2014-2020 with three different first authors, and splitting the naming
# across them would obscure that these are all one data collection.
#
# Notes on the conversion:
#  * `id` is `childid` for the child files and `parentid` for the proxy files.
#    In the proxy files each parent appears exactly once and rates exactly one
#    child, so `parentid` identifies the rated child as well; `childid` is not
#    usable there because it is missing for ~3% of rows. The global-health
#    proxy file is the exception: it carries no `parentid` at all, and its
#    `childid` is complete and unique, so that file keys on `childid`.
#  * The `*_theta`/`*_thetase` columns (IRT scores + standard errors) and
#    `pgh7`/`pgh7px` (sum of the PGH-7 items) are composites, not responses,
#    and are dropped.
#  * The `child_inc_*`/`parent_inc_*` columns are constant 1 (every shipped
#    row was in the psychometric analysis sample) and are dropped.
#  * A handful of items carry a non-ordinal first category ("Did not have
#    recess", "Do not go to school", "Do not work a job") that sits below the
#    ordinal anchors rather than on them. Those specific item-responses are
#    dropped -- see NONORDINAL below, with codes read off the deposit's
#    codebook PDFs. "None" as the bottom of a duration scale (PAC_M_029/030/
#    067, PAC_S_003: "None" / "Less than 15 minutes" / ...) *is* a real
#    anchor and is kept.
#  * Item names are kept exactly as in the source so they join to the
#    codebook PDFs, which carry full item text for every bank.

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

API = "https://dataverse.harvard.edu/api/access/datafile/"
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# (dataverse file id, output name) per construct/reporter.
FILES = [
    (4271452, "forrest_2021_family_belonging_child"),
    (4271446, "forrest_2021_family_belonging_proxy"),
    (4271453, "forrest_2021_family_involve_child"),
    (4271434, "forrest_2021_family_involve_proxy"),
    (4271439, "forrest_2021_global_health_child"),
    (4271461, "forrest_2021_global_health_proxy"),
    (4271464, "forrest_2021_life_satisfaction_child"),
    (4271456, "forrest_2021_life_satisfaction_proxy"),
    (4271454, "forrest_2021_meaning_purpose_child"),
    (4271463, "forrest_2021_meaning_purpose_proxy"),
    (4271447, "forrest_2021_phys_stress_child"),
    (4271429, "forrest_2021_phys_stress_proxy"),
    (4271459, "forrest_2021_phys_activity_child"),
    (4271466, "forrest_2021_phys_activity_proxy"),
    (4271430, "forrest_2021_positive_affect_child"),
    (4271440, "forrest_2021_positive_affect_proxy"),
    (4271458, "forrest_2021_psych_stress_child"),
    (4271450, "forrest_2021_psych_stress_proxy"),
    (4271437, "forrest_2021_strength_child"),
    (4271435, "forrest_2021_strength_proxy"),
]

# Child-report and parent-proxy covariate blocks (source name -> IRW name).
COV_CHILD = {
    "socio02c": "cov_age",
    "socio03c": "cov_gender",
    "socio04c": "cov_ethnicity",
    "socio05c": "cov_race",
    "mode_F": "cov_setting",
}
COV_PROXY = {
    "socio02p": "cov_age",
    "socio03p": "cov_gender",
    "socio07ap": "cov_grade",
    "socio04p": "cov_ethnicity",
    "socio05p": "cov_race",
    "socio22": "cov_chronic_condition",
    "socio24": "cov_respondent_relationship",
    "socio07": "cov_parent_education",
    "mode_F": "cov_setting",
}

# Numeric codes -> labels, from the deposit's codebook PDFs. Age and grade are
# already in years/grade-number and are left numeric.
COV_LABELS = {
    "cov_gender": {1: "Boy", 2: "Girl"},
    "cov_ethnicity": {0: "Not Hispanic/Latino", 1: "Hispanic/Latino"},
    "cov_race": {1: "White", 2: "Black or African American", 4: "Asian",
                 8: "American Indian or Alaska Native",
                 16: "Native Hawaiian or Pacific Islander", 32: "Other"},
    "cov_setting": {1: "School", 2: "Clinic", 3: "Internet Panel"},
    "cov_chronic_condition": {0: "No", 1: "Yes"},
    "cov_respondent_relationship": {1: "Mother", 2: "Father", 3: "Stepmother",
                                    4: "Stepfather", 5: "Grandmother",
                                    6: "Grandfather", 7: "Other"},
    "cov_parent_education": {1: "Some High School", 2: "High School/GED",
                             3: "Some College", 4: "College Degree or Higher"},
}

# Item -> response codes that are a non-ordinal "not applicable" category
# rather than a point on the item's scale.
NONORDINAL = {
    "PedGlobal9": {1},           # 1 = Do not go to school
    "PedGlobal10": {1},          # 1 = Do not go to school
    "PedGlobal12": {1},          # 1 = Do not work a job
    "PedGlobal9_Proxy": {1},
    "PedGlobal10_Proxy": {1},
    "PedGlobal12_Proxy": {1},
    "PAC_M_016": {1},            # 1 = Did not have recess
    "PAC_M_019": {1},            # 1 = Did not take gym/PE class
    "PAC_M_016_PX": {1},
    "PAC_M_019_PX": {1},
}

# Columns that are never items: identifiers, analysis-inclusion flags, and
# the derived theta / sum-score columns.
DROP_EXACT = {"childid", "parentid", "pgh7", "pgh7px"}
DROP_PREFIX = ("child_inc_", "parent_inc_")
DROP_SUFFIX = ("_theta", "_thetase")


def fetch(file_id: int) -> pd.DataFrame:
    r = requests.get(API + str(file_id), headers=HEADERS, timeout=120)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.content.decode("utf-8")), sep="\t",
                       low_memory=False)


def convert():
    os.makedirs(OUT_DIR, exist_ok=True)
    for file_id, out_name in FILES:
        proxy = out_name.endswith("_proxy")
        df = fetch(file_id)

        cov_map = COV_PROXY if proxy else COV_CHILD
        # Proxy files are keyed on the responding parent; the global-health
        # proxy file is the one exception -- it ships no parentid, but its
        # childid is complete and unique, so it keys on the rated child.
        id_col = "parentid" if proxy and "parentid" in df.columns else "childid"
        assert id_col in df.columns, f"{out_name}: no {id_col}"

        item_cols = [c for c in df.columns
                     if c not in DROP_EXACT and c not in cov_map
                     and not c.startswith(DROP_PREFIX)
                     and not c.endswith(DROP_SUFFIX)]
        assert item_cols, f"{out_name}: no item columns"

        keep = [id_col] + [c for c in cov_map if c in df.columns] + item_cols
        df = df[keep].rename(columns={id_col: "id", **cov_map})

        # Exact duplicate rows are redundant records of the same response set.
        df = df.drop_duplicates()
        # Any id still repeated carries conflicting responses and cannot be
        # adjudicated, so both records are dropped.
        dup = df["id"].duplicated(keep=False)
        if dup.any():
            print(f"  {out_name}: dropping {int(dup.sum())} row(s) with "
                  f"conflicting duplicate id")
            df = df[~dup]
        df = df[df["id"].notna()]
        assert df["id"].is_unique, f"{out_name}: id not unique"

        cov_cols = [c for c in df.columns if c.startswith("cov_")]
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                       var_name="item", value_name="resp")

        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        for item, codes in NONORDINAL.items():
            if item in item_cols:
                long = long[~(long["item"].eq(item) & long["resp"].isin(codes))]

        for cov, labels in COV_LABELS.items():
            if cov in long.columns:
                extra = set(long[cov].dropna().unique()) - set(labels)
                assert not extra, f"{out_name}: unlabelled {cov} codes {extra}"
                long[cov] = long[cov].map(labels)

        long = long[["id", "item", "resp"] + cov_cols].reset_index(drop=True)
        long.to_csv(os.path.join(OUT_DIR, out_name + ".csv"), index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
