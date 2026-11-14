#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/r3v4xznjkp/1
# DOI: 10.17632/r3v4xznjkp.1 (data)
#   Atsiz O (2021). The impact of cultural destination attributes on overall tourist satisfaction and
#   tourist loyalty [Data set]. Mendeley Data, V1.
# License: CC BY 4.0 (Mendeley Data)
# Data: anket tez.sav, 411 international travellers about to leave Istanbul. Value labels on every
#   item: 1 strongly disagree .. 5 strongly agree. Variable labels are the Turkish wording.
# MEAN-IMPUTED CELLS ARE DROPPED: in every item column the fractional values (e.g. religousplaces
#   3.5073529..., sat1 4.2322738...) are a single value per column equal to that column's mean over
#   its integer cells -- the depositors' mean substitution for missing answers. The script checks
#   this and drops those cells rather than ship them. One `guides` cell is 11 (outside the 1-5
#   labels) and is dropped as a data-entry error.
# Tables (item = the .sav variable name):
#   atsiz_2021_destination_attributes -- 21 cultural destination attributes (religious places,
#     souvenirs, theme parks, festivals, food, shopping, guides, handcrafts, architecture, traditional
#     scenery, art, accessibility, outdoor activities, atmosphere, information centres,
#     accommodation, museums, galleries, cultural villages, historic buildings, monuments).
#   atsiz_2021_tourist_satisfaction -- sat1-sat4.
#   atsiz_2021_tourist_loyalty      -- revisit, wom, ewom.
# Covariates: cov_age (yas), cov_gender (cinsiyet value labels).
# Not carried: nationality (free text), trip characteristics, spending.
# Item text: not shipped -- the Turkish wording is in the variable labels, but the questionnaire was
#   administered to international travellers and the administered-language versions are not deposited.
import io
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = ("https://data.mendeley.com/public-files/datasets/r3v4xznjkp/files/"
       "19d85e77-4303-491d-83a5-19f01bba98f4/file_downloaded")
ATTR = ["religousplaces", "souveniers", "themeparks", "festivals", "food", "shoppingplaces", "guides", "handcrafts",
        "architecture", "traditionalscenery", "art", "accesiblity", "indoorfac", "atmosphere", "infocenters",
        "accomodation", "museums", "galleries", "culturevillages", "historicbuilding", "monuments"]
TABLES = {"atsiz_2021_destination_attributes": ATTR,
          "atsiz_2021_tourist_satisfaction": ["sat1", "sat2", "sat3", "sat4"],
          "atsiz_2021_tourist_loyalty": ["revisit", "wom", "ewom"]}


def main():
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    c = r.content
    if c[:8] == b'{"url":"':
        c = requests.get(json.loads(c)["url"], timeout=120).content
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(c)
        f.flush()
        d, meta = pyreadstat.read_sav(f.name)
    assert len(d) == 411
    vl = meta.variable_value_labels
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["yas"]
    d["cov_gender"] = d["cinsiyet"].map(vl["cinsiyet"])
    covs = ["cov_age", "cov_gender"]
    dropped = 0
    for col in sum(TABLES.values(), []):
        x = d[col]
        frac = x[(x % 1) != 0].dropna()
        if len(frac):
            assert frac.nunique() == 1, col
            assert np.isclose(frac.iloc[0], x[(x % 1) == 0].mean()), col  # the column mean -> imputed
            dropped += len(frac)
            d.loc[frac.index, col] = np.nan
    print("mean-imputed cells dropped:", dropped)
    out_of_range = d["guides"].notna() & ~d["guides"].between(1, 5)
    assert out_of_range.sum() == 1 and (d.loc[out_of_range, "guides"] == 11).all()
    d.loc[out_of_range, "guides"] = np.nan
    for name, items in TABLES.items():
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t = t.dropna(subset=["resp"])
        assert t["resp"].isin([1, 2, 3, 4, 5]).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(1, 6)) if c.status == "fail"]
        assert not fails, (name, fails)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())


if __name__ == "__main__":
    main()
