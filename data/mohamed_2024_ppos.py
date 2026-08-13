#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11636530
# DOI: 10.7717/peerj.18676
#
# Mohamed et al. (2024), "Evaluation of the effect of a communication
# skills course on medical students' attitude towards patient-centered
# care: a prospective study." PeerJ. CC BY 4.0.
# Supplementary file peerj-12-18676-s001.xlsx contains the 18-item Patient-
# Practitioner Orientation Scale (PPOS), administered to the same cohort at
# two timepoints (Methods: "collected data at two points: the start of
# year two and the start of year four from the same cohort") -- treated as
# a wave column per datastandard.md rather than two files, since the same
# students and items recur. Confirmed n=143 unique students (all "year 4"
# respondents are a subset of the 143 "year 2" respondents). PPOS uses a
# 6-point Likert scale ("6 = strongly agree" to "1 = strongly disagree"
# per Methods); the raw file also contains a handful of 0 values on every
# item, out of the documented 1-6 range, which are dropped as a sentinel
# per datastandard.md's "Filter sentinel/missing-value codes". The Sharing/
# Caring/Overall/Transformed_* columns are pre-computed subscale composites
# and are excluded as aggregates. "Canddaite" values (e.g. "F1") are
# study-assigned pseudonymous codes, not names -- no PII.

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11636530/supplementaryFiles"
MEMBER = "peerj-12-18676-s001.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

PPOS_ITEMS = [f"PPOS{i:02d}_b" for i in range(1, 19)]


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    df = pd.read_excel(io.BytesIO(zf.read(MEMBER)))
    df = df.rename(columns={"Canddaite": "id", "Year": "wave"})

    long = df.melt(id_vars=["id", "wave"], value_vars=PPOS_ITEMS,
                    var_name="item", value_name="resp")
    long["item"] = long["item"].str.replace("_b", "", regex=False)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long[(long["resp"] >= 1) & (long["resp"] <= 6)]  # drop 0 sentinel
    long = long.reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"]]

    out_path = OUT_DIR / "mohamed_2024_ppos.csv"
    long.to_csv(out_path, index=False)
    print(f"mohamed_2024_ppos: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
