#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0143612
# DOI: 10.1371/journal.pone.0143612
# Yu et al. (2015), "The Role of Family Environment in Depressive Symptoms
# among University Students: A Large Sample Survey in China", PLOS ONE.
# CC BY 4.0.
# Download raw file: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0143612.s001
#
# E1-E21 are the 21 items of the Beck Depression Inventory (4-point, 1-4; the
# paper's Instruments section; E19 weight loss, E21 loss of interest in sex
# and E9 suicidal thoughts are the rarest endorsements, as BDI norms predict).
# The table was first published as yu_2015_family_environment, a name taken
# from the paper's title; the Family Environment Scale is in the deposit only
# as 10 subscale totals. Renamed yu_2015_bdi 2026-10-05 (irw#2840); the
# responses are unchanged.
#
# The raw "Number" column is NOT a unique person id -- rows sharing the same
# Number have different Gender/Age (confirmed by inspection), so it's some
# other code, not a participant identifier. Falls back to row index per
# datastandard.md's "Missing person ID" guidance. Cohesion/Expression/
# Conflict/Independence/Achievement/Intellectual/Recreational/Moral/
# Organization/Control are derived subscale totals, excluded from the item
# list -- only the raw E1-E21 items are kept.

from __future__ import annotations

import io
import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0143612.s001"

ITEM_COLS = [f"E{i}" for i in range(1, 22)]
COV_RENAME = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "Ethnic": "cov_ethnicity",
    "Religionbelief": "cov_religion_belief",
    "Familyeconomic": "cov_family_economic_status",
    "Parentrelationship": "cov_parent_relationship",
    "Paternaleducation": "cov_paternal_education",
    "Maternaleducation": "cov_maternal_education",
    "Saticfactionwithmajor": "cov_satisfaction_with_major",
}
COV_COLS = list(COV_RENAME.values())


def convert():
    r = requests.get(URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns=COV_RENAME)
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)

    long = df.melt(id_vars=["id"] + COV_COLS, value_vars=ITEM_COLS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    ##the .sav stores whole numbers as doubles; write them as integers
    long["resp"] = long["resp"].astype(int)
    for c in COV_COLS:
        long[c] = long[c].astype("Int64")
    long = long[["id", "item", "resp"] + COV_COLS]

    path = os.path.join(OUT_DIR, "yu_2015_bdi.csv")
    long.to_csv(path, index=False)
    print(f"yu_2015_bdi: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
