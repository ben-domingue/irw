#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0346696
# DOI: 10.1371/journal.pone.0346696
# Supporting Information: https://doi.org/10.1371/journal.pone.0346696.s001 (S1 File, XLSX)
#
# Survey of Chinese university students'/staff's Generative-AI (GAI)
# assisted learning, 7 constructs x 5 items each (35 items total), all on
# a 7-point Likert scale (1=Strongly Disagree .. 7=Strongly Agree). Item-
# to-construct mapping comes directly from the article's Table 2
# ("Measurement Items and Sources", extracted from the PLOS full-text XML
# since the HTML-rendered table is an image):
#   Task-Technology Fit (TTF):        Q5-Q9
#   Role Adaptation (RA):             Q10-Q14
#   Self Efficacy (SE):               Q15-Q19
#   Institutional Support (IS):       Q20-Q24
#   Exploration Behavior (Explore):   Q25-Q29
#   Exploitation Behavior (Exploit):  Q30-Q34
#   Learning Effect (LE):             Q35-Q39
# One file per construct (one scale per file, per datastandard.md) -- items
# are renamed to their construct-prefixed codes (e.g. TTF1..TTF5) as given
# in Table 2 so they match the source instrument rather than raw Q-numbers.
#
# Q1/Q2/Q4 (identity, GAI-usage duration, academic field) are kept as
# categorical covariates; Q3_Choice1-5 (multi-select "which GAI tools do
# you use" checkboxes) are kept as binary covariates. All 35 item columns
# are clean integers in 1-7 across all 207 respondents; no sentinel or
# out-of-range values found.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0346696.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {
    "Q1": "cov_identity",
    "Q2": "cov_gai_duration",
    "Q4": "cov_academic_field",
    "Q3_Choice1": "cov_tool_chatgpt",
    "Q3_Choice2": "cov_tool_wenxin_yiyan",
    "Q3_Choice3": "cov_tool_deepseek",
    "Q3_Choice4": "cov_tool_doubao",
    "Q3_Choice5": "cov_tool_other",
}

# (output name, item prefix, list of source Q-columns in item order)
SCALES = [
    ("zeng_2026_gai_ttf", "TTF", [f"Q{i}" for i in range(5, 10)]),
    ("zeng_2026_gai_role_adapt", "RA", [f"Q{i}" for i in range(10, 15)]),
    ("zeng_2026_gai_self_efficacy", "SE", [f"Q{i}" for i in range(15, 20)]),
    ("zeng_2026_gai_inst_support", "IS", [f"Q{i}" for i in range(20, 25)]),
    ("zeng_2026_gai_exploration", "EXPLORE", [f"Q{i}" for i in range(25, 30)]),
    ("zeng_2026_gai_exploitation", "EXPLOIT", [f"Q{i}" for i in range(30, 35)]),
    ("zeng_2026_gai_learning_effect", "LE", [f"Q{i}" for i in range(35, 40)]),
]


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"Code": "id", **COV_RENAME})
    assert df["id"].nunique() == len(df)
    return df


def convert():
    df = fetch_data()
    cov_cols = list(COV_RENAME.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for out_name, prefix, q_cols in SCALES:
        item_names = [f"{prefix}{i+1}" for i in range(len(q_cols))]
        rename_map = dict(zip(q_cols, item_names))
        sub = df.rename(columns=rename_map)

        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_names,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= 1) & (long["resp"] <= 7)]
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + cov_cols]

        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()} rows={len(long)}")


if __name__ == "__main__":
    convert()
