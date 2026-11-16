#!/usr/bin/env python3
# Source: https://doi.org/10.5061/dryad.gtht76hv4 (Dryad; mirrored at https://zenodo.org/records/10927571)
# DOI: 10.5061/dryad.gtht76hv4
# Paper: Trumbull et al. (2024), "Using a standardized sound set to help characterize
#   misophonia: The international affective digitized sounds", PLOS ONE,
#   https://doi.org/10.1371/journal.pone.0301105
# License: CC0 1.0 (Zenodo record + DataCite rightsList)
# Data: IADS_Data_Clean.sav (Qualtrics export, 377 MTurk adults: 132 misophonia
#   [MQincluded=1], 245 controls [HCgroupincluded=1]) -- matches the paper's N.
#
# Tables (one per instrument; items keep the source variable name):
#   trumbull_2024_mq       Misophonia Questionnaire (Wu et al. 2014): mq1_1..mq1_7
#                          (sound sensitivity) + mq2_1..mq2_10 (emotions/behaviours), 0-4.
#                          The two "Other (specify)" rows mq1_8/mq2_11 and the single
#                          severity rating mq3 (0-15) are dropped.
#   trumbull_2024_panas    PANAS, 20 items, 1-5
#   trumbull_2024_pai_bor  PAI Borderline Features scale, 24 items, 1-4 as administered
#                          (False..Very true); reverse-keyed items left raw
#   trumbull_2024_snap_ocpd SNAP obsessive-compulsive PD scale, 25 items, True=1/False=0
#                          (source codes 1=True, 2=False)
#   trumbull_2024_iip47    Inventory of Interpersonal Problems short form, 47 items, 1-5
#   trumbull_2024_aim      Affect Intensity Measure short (AIM_NI_1-6, AIM_NR_1-6), 1-6
#   trumbull_2024_iads_valence / _arousal / _similarity / _avoidance
#                          Ratings of 167 IADS-2 sounds (items S1..S167 as numbered in
#                          the Qualtrics export; each participant heard one of three
#                          blocks, ~126 raters per sound), 1-9. Valence = SAM 1 most
#                          negative .. 9 most positive; arousal = SAM 1 calm .. 9 excited;
#                          similarity to everyday trigger sounds and avoidance 1 not at all
#                          .. 9 exactly.
# Not shipped: Q1985-Q1991 (an unnamed trigger-checklist / thoughts block; the README
#   does not name the instrument), QID288-QID360 (unnamed social-support items),
#   timing columns, pre-computed score/average columns, practice sound Q3382-Q3390.
# id = row index (the file has no participant id column). Free-text "specify" columns
#   are not carried. No names, emails, IPs or dates of birth in the file.
# Covariates: cov_group (misophonia/control), cov_gender, cov_age, cov_hispanic,
#   cov_race, cov_education, cov_income (SPSS value labels applied).
#
# Item text: not shipped -- SPSS variable labels carry full stems for mq/panas/pai/
#   snap/iip/aim and value labels carry options; not attempted this batch (no register
#   row for PAI/SNAP/IIP; time). Sound items have no labels naming the IADS stimulus.
import io
import sys
from pathlib import Path
import re
import tempfile

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402


def gate(t):
    fails = [c for c in run_qc(t) if c.status == "fail"]
    assert not fails, fails

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://zenodo.org/api/records/10927571/files/IADS_Data_Clean.sav/content"


def load():
    r = requests.get(URL, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content); f.flush()
        df, meta = pyreadstat.read_sav(f.name)
    return df, meta


def main():
    df, meta = load()
    vl = meta.variable_value_labels
    df = df.reset_index(drop=True)
    df["id"] = np.arange(1, len(df) + 1)
    df["cov_group"] = np.where(df["MQincluded"] == 1, "misophonia", "control")
    df["cov_gender"] = df["dem1"].map(vl["dem1"])
    df["cov_age"] = pd.to_numeric(df["dem2"].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    # One respondent typed a 4-digit year (1978) into the free-text age field; it is
    # nulled rather than converted (survey date not in the file).
    df.loc[df["cov_age"] > 120, "cov_age"] = np.nan
    df["cov_hispanic"] = df["dem3"].map(vl["dem3"])
    df["cov_race"] = df["dem4"].map(vl["dem4"])
    df["cov_education"] = df["dem5"].map(vl["dem5"])
    df["cov_income"] = df["dem6"].map(vl["dem6"])
    covs = ["cov_group", "cov_gender", "cov_age", "cov_hispanic", "cov_race",
            "cov_education", "cov_income"]

    scales = {
        "mq": [f"mq1_{i}" for i in range(1, 8)] + [f"mq2_{i}" for i in range(1, 11)],
        "panas": [f"panas{i}" for i in range(1, 21)],
        "pai_bor": [f"pai{i}" for i in range(1, 25)],
        "snap_ocpd": [f"snap{i}" for i in range(1, 26)],
        "iip47": [f"iip{i}" for i in range(1, 48)],
        "aim": [f"AIM_NI_{i}" for i in range(1, 7)] + [f"AIM_NR_{i}" for i in range(1, 7)],
    }
    snd = [c for c in df.columns if re.match(r"S\d+_", c)]
    probes = {"valence": "_SAM_V_", "arousal": "_SAM_A_", "similarity": "_sim_", "avoidance": "_avd"}
    for name, suf in probes.items():
        cols = [c for c in snd if c.endswith(suf)]
        assert len(cols) == 167, (name, len(cols))
        scales["iads_" + name] = cols

    for name, cols in scales.items():
        long = df[["id"] + covs + cols].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        if name == "snap_ocpd":
            long["resp"] = long["resp"].map({1.0: 1, 2.0: 0})
        if name.startswith("iads_"):
            long["item"] = long["item"].str.extract(r"^(S\d+)_")[0]
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        out = OUT / f"trumbull_2024_{name}.csv"
        gate(long)
        long.to_csv(out, index=False)
        print(out.name, len(long), long["id"].nunique(), long["item"].nunique(),
              sorted(long["resp"].unique()))


if __name__ == "__main__":
    main()
