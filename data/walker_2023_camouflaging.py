#!/usr/bin/env python3
# Source: https://data.ncl.ac.uk/articles/dataset/Anxiety_suicidality_autistic_traits_and_camouflaging_data/23895822
# DOI: 10.25405/data.ncl.23895822.v1
#   Walker V, Gullon-Scott F (2023). Anxiety, suicidality, autistic traits and camouflaging
#   data. Newcastle University data repository. Related article (README): "Exploring
#   suicidality, autistic traits and camouflaging within women with anxiety".
# License: CC BY 4.0 (figshare record + README)
# Data: "Anxiety, suicidality, autistic traits and camouflaging data.xlsx", one sheet per
#   instrument, rows keyed by "No." (148 UK women with an anxiety diagnosis, Qualtrics,
#   March-July 2022; README: no missing data). README.txt is the codebook.
#
# Tables (item = the instrument's item number as in the sheet header, prefixed by scale):
#   walker_2023_spin    Social Phobia Inventory, 17 items, text recoded 0-4
#                       (Not at all 0, A little bit 1, Somewhat 2, Very much 3, Extremely 4)
#   walker_2023_catq    Camouflaging Autistic Traits Questionnaire, 25 items, text recoded
#                       1-7 (Strongly disagree 1 .. Strongly agree 7, Neither agree or
#                       disagree 4); reverse-keyed items raw
#   walker_2023_bapq    Broad Autism Phenotype Questionnaire, 35 items as deposited (the BAPQ
#                       has 36; the sheet carries columns 1-35 only), text recoded 1-6
#                       (Very rarely 1, Rarely 2, Occasionally 3, Somewhat often 4 [source
#                       spells "Somewhat ofen"], Often 5, Very often 6); reverse-keyed raw
#   walker_2023_inq15   Interpersonal Needs Questionnaire-15, 15 items, 1-7 as deposited
#   walker_2023_acssfad Acquired Capability for Suicide Scale - Fearlessness About Death,
#                       7 items, 0-4 as deposited
# Not shipped: HADS. Its sheet holds per-item response wording (each HADS item has its own
#   four options and keying) mixed with a bare numeric 4 in every item, so the coding of
#   the 4 cannot be tied to an option without guessing.
# A text response outside the mapped set raises (no silent NA).
# Covariates: cov_age_band, cov_gender, cov_cisgender ("Same as sex assigned at birth?"),
#   cov_sexuality, cov_ethnicity (as deposited).
# Item text: not shipped -- the deposit has item numbers only.
import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = "https://ndownloader.figshare.com/files/41894244"

SPIN = {"Not at all": 0, "A little bit": 1, "Somewhat": 2, "Very much": 3, "Extremely": 4}
CATQ = {"Strongly disagree": 1, "Disagree": 2, "Somewhat disagree": 3,
        "Neither agree or disagree": 4, "Somewhat agree": 5, "Agree": 6, "Strongly agree": 7}
BAPQ = {"Very rarely": 1, "Rarely": 2, "Occasionally": 3, "Somewhat ofen": 4,
        "Somewhat often": 4, "Often": 5, "Very often": 6}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    x = pd.read_excel(io.BytesIO(r.content), sheet_name=None)
    demo = x["Demographics"].rename(columns={
        "No.": "id", "Age": "cov_age_band", "Gender": "cov_gender",
        "Same as sex assigned at birth?": "cov_cisgender", "Sexuality": "cov_sexuality",
        "Ethnicity": "cov_ethnicity"})
    assert len(demo) == 148 and demo["id"].is_unique
    covs = ["cov_age_band", "cov_gender", "cov_cisgender", "cov_sexuality", "cov_ethnicity"]
    specs = {"spin": ("SPIN", 17, SPIN, 0, 4), "catq": ("CATQ", 25, CATQ, 1, 7),
             "bapq": ("BAPQ", 35, BAPQ, 1, 6), "inq15": ("INQ15", 15, None, 1, 7),
             "acssfad": ("ACSSFAD", 7, None, 0, 4)}
    for name, (sheet, n, mapping, lo, hi) in specs.items():
        s = x[sheet].rename(columns={"No.": "id"})
        items = [c for c in s.columns if c != "id"]
        assert len(items) == n, (name, len(items))
        t = s.melt(id_vars="id", var_name="item", value_name="resp").dropna(subset=["resp"])
        if mapping is not None:
            bad = set(t["resp"]) - set(mapping)
            assert not bad, (name, bad)
            t["resp"] = t["resp"].map(mapping)
        t["resp"] = t["resp"].astype(int)
        assert t["resp"].between(lo, hi).all()
        t["item"] = name + "_" + t["item"].astype(int).astype(str).str.zfill(2)
        t = t.merge(demo[["id"] + covs], on="id", how="left", validate="many_to_one")
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        t.to_csv(OUT / f"walker_2023_{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
