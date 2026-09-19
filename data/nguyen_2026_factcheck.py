#!/usr/bin/env python3
# Source: https://researchdata.ntu.edu.sg/dataset.xhtml?persistentId=doi:10.21979/N9/P5WUGI
# DOI: 10.21979/N9/P5WUGI
# Paper: Nguyen, T. M. C., & Lee, C. S. (2026). Fact-Checking Against
#   Misinformation by Generative Artificial Intelligence Conversational Agents:
#   the Role of Digital Literacy. Technology in Society.
#
# Licence: CC BY-NC 4.0. NC is outside the default open-licence rule; taken on
# ben-domingue's approval (2026-09-15, per the datastandard.md NC exception),
# so Derived_License must carry CC BY-NC 4.0.
#
# One survey of 668 higher-education GenAI users, one row per respondent, no
# missing values and no demographics in the deposit. Each block of items is
# one scale; the deposit's own scale-score columns identify them (block mean
# vs score, r >= 0.97 for each), and the SPSS variable labels carry the
# wording:
#   C_1..C_10   -> DL   Digital Literacy in GenAI Usage  (7-point agreement)
#   G_1..G_12   -> UH   User Heuristics                  (7-point agreement)
#   H_1..H_12   -> SP   Systematic Processing            (7-point agreement)
#   I_1..I_11   -> IE   Information Self-efficacy        (7-point agreement)
#   J3_1..J3_5  -> ITFC Intention to Fact-check          (7-point agreement)
#   B1ad_1..4   -> frequency of use of four kinds of GenAI tool
#                  (1 Never .. 5 Always, more than 10 times a week)
# The 7-point labels run 1 Strongly disagree .. 7 Strongly agree with no
# don't-know code. The score columns (DL, UH, IE, SP, ITFC) are composites
# and are not shipped.
#
# The deposit has no respondent identifier, so `id` is the row index.

import io
import os
import sys

import pandas as pd
import pyreadstat
import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "automated_finding"))
from irw_triage_updated import run_qc          # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

FILE_URL = "https://researchdata.ntu.edu.sg/api/access/datafile/507231?format=original"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SCALES = [
    ("C_",    10, 7, "nguyen_2026_factcheck_digital_literacy"),
    ("G_",    12, 7, "nguyen_2026_factcheck_user_heuristics"),
    ("H_",    12, 7, "nguyen_2026_factcheck_systematic_proc"),
    ("I_",    11, 7, "nguyen_2026_factcheck_info_self_efficacy"),
    ("J3_",    5, 7, "nguyen_2026_factcheck_intention"),
    ("B1ad_",  4, 5, "nguyen_2026_factcheck_genai_use"),
]


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=300)
    r.raise_for_status()
    path = os.path.join(OUT_DIR, "_nguyen_2026_factcheck.sav")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(path, "wb") as f:
        f.write(r.content)
    try:
        df, _ = pyreadstat.read_sav(path)
    finally:
        os.remove(path)
    return df


def convert():
    raw = fetch()
    assert len(raw) == 668, len(raw)
    raw.insert(0, "id", range(1, len(raw) + 1))

    for prefix, n_items, top, name in SCALES:
        items = [f"{prefix}{i}" for i in range(1, n_items + 1)]
        long = raw[["id"] + items].melt(id_vars="id", var_name="item",
                                        value_name="resp")
        long = long.dropna(subset=["resp"])
        bad = ~long["resp"].isin(range(1, top + 1))
        assert not bad.any(), long[bad].head()
        long["resp"] = long["resp"].astype(int)
        long = long.sort_values(["id", "item"], key=lambda s: s if s.name == "id"
                                else s.str.split("_").str[1].astype(int))
        long = long[["id", "item", "resp"]].reset_index(drop=True)
        checks = run_qc(long)
        bad = [c for c in checks if c.status == "fail"]
        assert not bad, (name, [(c.name, c.detail) for c in bad])
        long.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
