#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC8679900
# DOI: 10.7717/peerj.12528
#
# Reuter PR, Forster BL, Kruger BJ (2021), "A longitudinal study of the
# impact of COVID-19 restrictions on students' health behavior, mental
# health and emotional well-being." PeerJ. CC BY 4.0.
#
# Supplementary file peerj-09-12528-s001.xlsx has four sheets. This script
# ships only "Emotions" (39-item mood/emotion checklist, binary 0/1 -- not
# endorsed/endorsed; anonymous survey with no person ID column in the
# source, row index used as id per datastandard.md).
#
# QC fix (2026-08-12, ben-domingue catch): the "Mental health" sheet
# (6 campus/social-connection items) was previously also shipped as
# reuter_2021_campuslife.csv, but on review it mixes 4 binary Yes/No items
# with 2 three-point Less/About the same/More items under one file with no
# confirmed underlying instrument name -- the same "heterogeneous
# single-purpose survey items rather than a psychometric scale" problem
# already used to exclude the "Longitudinal data" sheets below. Removed.
# The "Longitudinal data I"/"Longitudinal data II" sheets (health-behavior
# counts in mixed units -- hours, days, times -- plus a few suicide-ideation
# items) remain excluded for the same reason.

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8679900/supplementaryFiles"
MEMBER = "peerj-09-12528-s001.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch_zip() -> zipfile.ZipFile:
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    return zipfile.ZipFile(io.BytesIO(r.content))


def make_emotions(zf: zipfile.ZipFile):
    df = pd.read_excel(io.BytesIO(zf.read(MEMBER)), sheet_name="Emotions")
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    items = [c for c in df.columns if c != "id"]

    long = df.melt(id_vars=["id"], value_vars=items, var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"]]

    out_path = OUT_DIR / "reuter_2021_emotions.csv"
    long.to_csv(out_path, index=False)
    print(f"reuter_2021_emotions: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    zf = fetch_zip()
    make_emotions(zf)


if __name__ == "__main__":
    convert()
