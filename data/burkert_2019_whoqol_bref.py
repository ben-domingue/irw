#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC6510219
# DOI: 10.7717/peerj.6773
#
# Burkert & Freidl (2019), "Pronounced social inequality in health-related
# factors and quality of life in women and men from Austria who are
# overweight or obese." PeerJ. CC BY 4.0. N=15,771.
# Data are drawn from the Austrian Health Interview Survey (ATHIS)
# 2014/2015. Supplementary file peerj-07-6773-s001.sav is the full ATHIS
# microdata extract (567 columns) -- most of that is unrelated survey
# content (health behaviors, housing, income, etc.), not one coherent
# instrument. The paper's quality-of-life outcome is the WHOQOL-BREF
# (World Health Organization Quality of Life, short form), whose 26 raw
# items are present as columns LQ1-LQ26 (1-5 Likert, German item labels
# in the .sav variable-label metadata, e.g. LQ1="Lebensqualitaet",
# LQ2="Gesundheitszufriedenheit"). The paper itself only reports the four
# computed WHOQOL domain scores (physical health, psychological health,
# social relationships, environment) -- those are aggregates and are
# excluded here per datastandard.md; this script ships the raw items
# instead. No missing values in LQ1-LQ26 (26 * 15,771 non-null cells,
# exactly item_count * n). No PII: the only birth-related column,
# BIRTHPLACE ("Geburtsland" = country of birth), is a 3-level categorical
# code (10/21/22), not a date of birth.

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6510219/supplementaryFiles"
MEMBER = "peerj-07-6773-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

LQ_ITEMS = [f"LQ{i}" for i in range(1, 27)]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with zf.open(MEMBER) as f:
        df = pd.read_spss(io.BytesIO(f.read()), convert_categoricals=False)

    df = df.rename(columns={"lfnr": "id"})
    df["id"] = df["id"].astype(int)
    assert df["id"].nunique() == len(df)

    keep = ["id"] + LQ_ITEMS
    df = df[keep]

    long = df.melt(id_vars=["id"], value_vars=LQ_ITEMS,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    out_path = OUT_DIR / "burkert_2019_whoqol_bref.csv"
    long.to_csv(out_path, index=False)
    print(f"burkert_2019_whoqol_bref: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
