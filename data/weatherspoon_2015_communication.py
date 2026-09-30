#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0119855
# DOI: 10.1371/journal.pone.0119855
#
# Weatherspoon DJ, Horowitz AM, Kleinman DV (2015) The Use of Recommended
# Communication Techniques by Maryland Family Physicians and Pediatricians.
# PLoS ONE.
#
# Companion survey to koo_2016_comm_technique_{use,opinion} (same research
# group, DOI 10.1371/journal.pone.0146545, oral-health-literacy
# communication techniques among Maryland nurse practitioners) -- this one
# surveys family physicians (S1 Dataset) and pediatricians (S2 Dataset)
# separately, same 17-item Q12_Na/Q12_Nb battery: a = frequency of use
# (1-5), b = perceived effectiveness (Yes = 1, No = 2, Don't know = 9).
# 9 is filtered out of both, matching koo_2016's convention for the same
# instrument family. Both files end in a block of fully-blank trailing rows (Excel
# padding) -- dropped via the ID-not-null filter. ID is not globally
# unique across the padding rows but is unique among real respondents.

import os

import pandas as pd
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URLS = {
    "family_physicians": "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0119855.s002",
    "pediatricians": "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0119855.s003",
}

A_ITEMS = [f"Q12_{i}a" for i in range(1, 18)]
B_ITEMS = [f"Q12_{i}b" for i in range(1, 18)]


def fetch_raw(url: str) -> pd.DataFrame:
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(pd.io.common.BytesIO(r.content))


def build_long(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    d = df[["ID"] + item_cols].dropna(subset=["ID"]).copy()
    d = d.rename(columns={"ID": "id"})
    assert d["id"].is_unique, "id column not unique after dropping blank rows"
    for c in item_cols:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    long = d.melt(id_vars=["id"], value_vars=item_cols, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long = long[long["resp"] != 9]  # "not applicable" sentinel
    long["id"] = long["id"].astype(int)
    return long[["id", "item", "resp"]].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, fname), index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


# Family-physician respondents whose effectiveness (b) answers include
# values the item never offered (3-5, in the deposit itself): 291 and 493
# have nothing else, and 522's three 2s sit among fourteen 3-5s, so none of
# their b answers can be read as Yes/No. Dropped from _effectiveness only
# (#2196).
DROP_EFFECTIVENESS_IDS = {"family_physicians": [291, 493, 522]}


def convert():
    for pop, url in URLS.items():
        print(f"Fetching {pop} dataset...")
        raw = fetch_raw(url)
        write_scale(build_long(raw, A_ITEMS), f"weatherspoon_2015_{pop}_freq.csv")
        eff = build_long(raw, B_ITEMS)
        eff = eff[~eff["id"].isin(DROP_EFFECTIVENESS_IDS.get(pop, []))]
        assert eff["resp"].isin([1, 2]).all(), f"{pop}: effectiveness outside Yes/No"
        write_scale(eff, f"weatherspoon_2015_{pop}_effectiveness.csv")


if __name__ == "__main__":
    convert()
