#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/9w9t8skvjp/1
# DOI: 10.17632/9w9t8skvjp.1 (data)
#   Gao W, Zhang Y (2026). Shenyang twelve pocket parks soundscape perception questionnaire data
#   [Data set]. Mendeley Data, V1. Manuscript: Wang, Gao, Yang, Zhang & Zhang, "Soundscape and
#   environmental appraisals in roadside pocket parks".
# License: CC BY 4.0 (Mendeley Data)
# Data: questionnaire.csv (= the workbook's questionnaire sheet), 220 adult visitors to 12
#   traffic-adjacent pocket parks in Shenyang (April-June 2025). The workbook's variable_dictionary
#   sheet gives every code: sound-source dominance 1 not at all .. 5 dominates completely; the eight
#   ISO 12913-2 perceived affective quality attributes 1 strongly disagree .. 5 strongly agree
#   (Mandarin administration).
# Tables (item = the deposit's column name):
#   gao_2026_pocket_park_paq           -- pleasant, vibrant, eventful, chaotic, annoying, monotonous,
#                                         uneventful, calm
#   gao_2026_pocket_park_sound_sources -- traffic_noise, human_sound, natural_sound, misc_noise (the
#                                         deposit's other_noise, renamed: the covariate lint reads other_* as a covariate)
# id: respondent_id. Covariates: cov_park (sample_id, 1-12), cov_park_size (park_type).
# Not shipped: single questions with their own scales (satisfaction, noisiness, coherence,
#   aq_satisfaction), visit context. Not carried: gender (the dictionary gives no codes for it).
# Item text: not shipped -- the attribute names are ISO/TS 12913-2's; the Mandarin wording is not deposited.
import io
import json
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = ("https://data.mendeley.com/public-files/datasets/9w9t8skvjp/files/"
       "62b6ccf1-75f8-43be-b261-1dd959a2c52f/file_downloaded")
TABLES = {"gao_2026_pocket_park_paq": ["pleasant", "vibrant", "eventful", "chaotic", "annoying", "monotonous",
                                       "uneventful", "calm"],
          "gao_2026_pocket_park_sound_sources": ["traffic_noise", "human_sound", "natural_sound", "misc_noise"]}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    c = r.content
    if c[:8] == b'{"url":"':
        c = requests.get(json.loads(c)["url"], timeout=120).content
    d = pd.read_csv(io.BytesIO(c))
    assert len(d) == 220 and d["respondent_id"].is_unique
    d = d.rename(columns={"other_noise": "misc_noise"})  # the covariate lint reads "other_*" as a covariate
    d["id"] = d["respondent_id"]
    d["cov_park"] = d["sample_id"]
    d["cov_park_size"] = d["park_type"]
    covs = ["cov_park", "cov_park_size"]
    for name, items in TABLES.items():
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        assert t["resp"].isin([1, 2, 3, 4, 5]).all()
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(1, 6)) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
