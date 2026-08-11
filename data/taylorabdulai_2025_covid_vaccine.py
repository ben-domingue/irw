#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0319798
# DOI: 10.1371/journal.pone.0319798
# SI: S1 File (10.1371/journal.pone.0319798.s001), XLSX
#
# No person-id column in the source file; row index used as id. Four
# distinct item batteries identified in the file (each a coherent set of
# Yes/No or Yes/No/Not-sure items sharing one construct and response
# format) are shipped as separate scale tables per datastandard.md's
# "multiple scales in one file" rule:
#   - info_source: which channels respondent gets COVID-19 info from
#   - stop_behaviors: preventive behaviors respondent has stopped doing
#   - conspiracy_beliefs: belief in specific vaccine conspiracy claims
#   - incentives: factors that would increase vaccine acceptance
# "Not sure" responses in conspiracy_beliefs are a non-response category
# (not an ordinal step between Yes/No) and are dropped, not recoded.

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0319798.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

YESNO_MAP = {"yes": 1, "no": 0}

INFO_SOURCE_COLS = [
    "Television_Info_Source", "Newspaper_Info_Source", "Healthworker_Info_Source",
    "Socialmedia_Info_Source", "Radiostations_Info_Source", "Ministryofhealth_Info_Source",
    "Institute_public_affairs_Info_Source", "Celebrities_Info_Source",
    "Socialmedia_influencers_Info_Source", "WHO_Info_Source",
    "COVID_19_Hotlines_Info_Source", "National_COVID_website_Info_Source",
]
STOP_BEHAVIOR_COLS = [
    "Stop_Mask", "Stop_Social_Distance", "stop_Handwashing", "Stop_sanitizers",
    "Stop_largeGathering", "Stop_shaking_Hands",
]
CONSPIRACY_COLS = [
    "Covid_Genetic", "Covid_Implanting_Mchip", "Infertility_Women", "Sterility_Men",
]
INCENTIVE_COLS = [
    "Covid_19_Financial_Incentive", "Covid_19_monetary_rewards", "Covid_19_free_of_charge",
    "Covid_19_adequate_info", "Covid_19_R_Travel", "Covid_19_employment_Condition",
    "Covid_19_positive_feedback",
]

COV_MAP = {
    "Age": "cov_age",
    "Sex": "cov_sex",
    "Religious_Deno": "cov_religion",
    "Edu_Background": "cov_education",
    "Occupation": "cov_occupation",
}

SCALES = {
    "taylorabdulai_2025_info_source": INFO_SOURCE_COLS,
    "taylorabdulai_2025_stop_behavior": STOP_BEHAVIOR_COLS,
    "taylorabdulai_2025_conspiracy": CONSPIRACY_COLS,
    "taylorabdulai_2025_incentives": INCENTIVE_COLS,
}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Sheet1")

    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COV_MAP)
    cov_cols = list(COV_MAP.values())

    os.makedirs(OUT_DIR, exist_ok=True)
    for out_name, item_cols in SCALES.items():
        sub = df[["id"] + cov_cols + item_cols].copy()
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(str).str.strip().str.lower().map(YESNO_MAP)
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"{out_name}.csv"
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
