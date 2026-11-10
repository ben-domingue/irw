#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0203826
# DOI: 10.1371/journal.pone.0203826
# Paper: Takamatsu R (2018). Turning off the empathy switch: Lower empathic
#   concern for the victim leads to utilitarian choices of action. PLOS ONE
#   13(9): e0203826.
# Data: Mendeley Data, two datasets by Reina Takamatsu:
#   Study 1: 10.17632/jczjwnbdf3.1, Study1.sav, 275 rows x 14 columns
#   Study 2: 10.17632/yvfd3rztmc.1, Study2.sav, 170 rows x 22 columns
#   Each record's description is the codebook (measures and response scales).
# License: CC BY 4.0 (both Mendeley Data records).
#
# Found by the PLOS monthly run of 2026-11-09 (leads/plos_leads_2026-11-09.csv,
# step-2b recoverable_format: resp_scale_mixed, because the .sav files hold
# the dilemma choices beside 5-35 sum scores).
#
# ONE output table: takamatsu_2018_sacrificial_dilemmas -- utilitarian choice
#   of action in sacrificial moral dilemmas ("would you push the stranger on to
#   the tracks in order to save the five workmen?"), "4-point scale from 0
#   (definitely no) to 3 (definitely yes)" in both studies (paper, both
#   Methods sections; both Mendeley descriptions).
#   Study 1 (MTurk, n = 275): footbridge, raftboat.
#   Study 2 (MTurk "Masters", n = 170): footbridge, raftboat, baby (crying
#   baby), vaccine, safari (modified safari), sacrifice (Sophie's choice).
#   Item codes: the dilemma names, lower-cased (Study 1 "footbridge_choice"
#   -> footbridge).
# TWO SAMPLES MERGED, cov_study = 1 / 2: footbridge and raftboat are the same
#   scenarios with the same documented response scale in both studies, so per
#   the same-instrument-across-samples rule they are one table. Study 2 ids are
#   offset past Study 1's (Study 2 id = 1000 + row).
# RECODE, Study 2 only: Study2.sav stores the choices as 1-4 (all four codes
#   used; its moral_judgment sum of the six runs 6-24), while the paper and the
#   Mendeley description both document 0-3. That is a uniform +1 offset in the
#   file, so Study 2 resp = stored value - 1, putting both studies on the
#   documented 0-3 coding. Asserted: Study 2 moral_judgment == sum of the six
#   stored values.
#
# Covariates: cov_study, cov_age, cov_gender (male / female; Study 1 deposits
#   text, Study 2 0 = male, 1 = female per its value labels), cov_ethnicity
#   (as deposited; the two studies used different category lists),
#   cov_political_orientation (Study 2 only, as deposited).
# DROPPED: every sum score (Study 1 choice_total, valence_total, LSRP_1,
#   sympathy_/distress_ footbridge/boat; Study 2 EC, LSRP_1, moral_judgment,
#   e_saved, e_victim, deon, moral_relativity, emo_react, ego_concern,
#   confidence) -- the item-level empathy, justification, LSRP and IRI
#   responses were not deposited; Study 1 gender_code (duplicates gender);
#   Study 1 condition (0/1/2, documented in neither the paper nor the
#   deposit); Study 2 o_benefit, s_benefit (entirely empty).
#
# Imputation: none; no missing choice cells (asserted).
#
# Item text: HELD. Label levels checked: both Mendeley records (dilemma names
#   only), .sav variable labels ("moral judgment in footbridge" etc.), S1 File
#   and the article (only the footbridge question quoted). Instruments: the
#   Greene et al. sacrificial dilemmas (Footbridge, Raftboat, Crying Baby,
#   Vaccine, Modified Safari, Sophie's Choice), cited to Greene et al. 2004
#   (Neuron). No scenario text is deposited. Register GREENE-DILEMMAS (hold,
#   new 2026-11-09).
#
# PII: none -- age, gender, ethnicity and political orientation only.

import os
import socket
import sys
import tempfile

import pandas as pd
import pyreadstat
import requests
import urllib3.util.connection as _uc

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
TABLE = "takamatsu_2018_sacrificial_dilemmas"
URLS = {
    1: ("https://data.mendeley.com/public-files/datasets/jczjwnbdf3/files/"
        "e38d6aa3-cb12-404c-bcff-849714df21bd/file_downloaded"),
    2: ("https://data.mendeley.com/public-files/datasets/yvfd3rztmc/files/"
        "358f1dc1-d5d9-498f-80ec-91827ee3ca58/file_downloaded"),
}
RAW = {1: os.environ.get("TAKAMATSU_S1_RAW", ""),
       2: os.environ.get("TAKAMATSU_S2_RAW", "")}
S1_ITEMS = {"footbridge_choice": "footbridge", "raftboat_choice": "raftboat"}
S2_ITEMS = {"Footbridge": "footbridge", "Raftboat": "raftboat",
            "Baby": "baby", "Vaccine": "vaccine", "Safari": "safari",
            "Sacrifice": "sacrifice"}
S1_DROPPED = ["choice_total", "valence_total", "LSRP_1", "sympathy_footbridge",
              "distress_footbridge", "sympathy_boat", "distress_boat",
              "gender_code", "condition"]
S2_DROPPED = ["EC", "LSRP_1", "moral_judgment", "e_saved", "e_victim", "deon",
              "moral_relativity", "emo_react", "ego_concern", "confidence",
              "o_benefit", "s_benefit"]
COV_COLS = ["cov_study", "cov_age", "cov_gender", "cov_ethnicity",
            "cov_political_orientation"]


def fetch(study):
    if RAW[study]:
        return RAW[study]
    _uc.allowed_gai_family = lambda: socket.AF_INET  # IPv6 stalls here
    r = requests.get(URLS[study], headers={"User-Agent": "IRW-Finder/1.0"},
                     timeout=120)
    r.raise_for_status()
    path = os.path.join(tempfile.mkdtemp(), f"Study{study}.sav")
    with open(path, "wb") as fh:
        fh.write(r.content)
    return path


def melt(df, items):
    long = df.melt(id_vars=["id"] + COV_COLS, value_vars=list(items),
                   var_name="item", value_name="resp")
    long["item"] = long["item"].map(items)
    return long


def convert():
    s1, _ = pyreadstat.read_sav(fetch(1))
    s2, m2 = pyreadstat.read_sav(fetch(2))
    assert s1.shape == (275, 14) and s2.shape == (170, 22), (s1.shape, s2.shape)
    for df, items, dropped, base in ((s1, S1_ITEMS, S1_DROPPED,
                                      ["age", "gender", "ethnicity"]),
                                     (s2, S2_ITEMS, S2_DROPPED,
                                      ["age", "gender", "ethnicity", "pol_ori"])):
        acc = set(items) | set(dropped) | set(base)
        assert acc == set(df.columns), set(df.columns) ^ acc
        assert df[list(items)].notna().all().all()
    print(f"PII screen: {s1.shape[1] + s2.shape[1]} columns examined; "
          f"string columns are gender/ethnicity/political orientation only")

    assert s1[list(S1_ITEMS)].isin([0, 1, 2, 3]).all().all()
    assert s2[list(S2_ITEMS)].isin([1, 2, 3, 4]).all().all()
    assert (s2[list(S2_ITEMS)].sum(axis=1) == s2["moral_judgment"]).all()
    assert s2["o_benefit"].isna().all() and s2["s_benefit"].isna().all()
    assert m2.variable_value_labels["gender"] == {0.0: "male", 1.0: "female"}

    s1 = s1.copy()
    s1["id"] = range(1, len(s1) + 1)
    s1["cov_study"] = 1
    s1["cov_age"] = s1["age"]
    s1["cov_gender"] = s1["gender"].str.lower().replace("", pd.NA)
    s1["cov_ethnicity"] = s1["ethnicity"].replace("", pd.NA)
    s1["cov_political_orientation"] = pd.NA

    s2 = s2.copy()
    s2["id"] = 1000 + pd.Series(range(1, len(s2) + 1), index=s2.index)
    assert s2["id"].min() > s1["id"].max()
    s2["cov_study"] = 2
    s2["cov_age"] = s2["age"]
    s2["cov_gender"] = s2["gender"].map({0.0: "male", 1.0: "female"})
    s2["cov_ethnicity"] = s2["ethnicity"]
    s2["cov_political_orientation"] = s2["pol_ori"]
    for c in S2_ITEMS:
        s2[c] = s2[c] - 1  # documented 0-3; the file stores 1-4

    long = pd.concat([melt(s1, S1_ITEMS), melt(s2, S2_ITEMS)],
                     ignore_index=True)
    long["resp"] = long["resp"].astype(int)
    long["cov_age"] = long["cov_age"].astype("Int64")
    long = long[["id", "item", "resp"] + COV_COLS]
    assert not long.duplicated(["id", "item"]).any()
    assert len(long) == 275 * 2 + 170 * 6
    assert long["id"].nunique() == 445

    checks = run_qc(long, permitted_values=[0, 1, 2, 3])
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {c.name}: {c.detail[:160]}")
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, TABLE + ".csv"), index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-"
          f"{long['resp'].max()}")


if __name__ == "__main__":
    convert()
