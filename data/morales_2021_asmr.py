#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC8164417
# DOI: 10.7717/peerj.11474
#
# Morales, Ramirez-Benavides & Villena-Gonzalez (2021), "Autonomous
# Sensory Meridian Response self-reporters showed higher scores for
# cognitive reappraisal as an emotion regulation strategy." PeerJ.
# CC BY 4.0. N=179.
# Supplementary file peerj-09-11474-s002.csv has two raw item batteries:
# the 10-item Emotion Regulation Questionnaire (ERQ, 1-7 Likert) and the
# 15-item ASMR-15 checklist (1-5 Likert), split per datastandard.md's
# "one file per scale" rule. Remaining columns are free-text/multi-select
# ASMR-experience questions, excluded (not the two named scales).

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8164417/supplementaryFiles"
MEMBER = "peerj-09-11474-s002.csv"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

ERQ_COLS = [f"ERQ_{i}" for i in range(1, 11)]
ASMR_COLS = [f"ASMR15_{i}" for i in range(1, 16)]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with zf.open(MEMBER) as f:
        raw = pd.read_csv(f)
    raw = raw.rename(columns={"Unnamed: 0": "id"})
    raw["id"] = range(1, len(raw) + 1)
    return raw


def build_long(raw: pd.DataFrame, cols: list[str], prefix: str) -> pd.DataFrame:
    cov = raw[["id", "Age", "Gender", "Nationality"]].rename(
        columns={"Age": "cov_age", "Gender": "cov_gender", "Nationality": "cov_nationality"}
    )
    long = raw[cols].copy()
    long.columns = [f"{prefix}{i + 1}" for i in range(len(cols))]
    long["id"] = raw["id"]
    long = long.melt(id_vars="id", var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long = long.merge(cov, on="id")
    long["resp"] = long["resp"].astype(int)
    return long[["id", "item", "resp", "cov_age", "cov_gender", "cov_nationality"]]


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    raw = fetch_raw()
    erq = build_long(raw, ERQ_COLS, "erq")
    asmr = build_long(raw, ASMR_COLS, "asmr")
    write_scale(erq, "morales_2021_erq.csv")
    write_scale(asmr, "morales_2021_asmr15.csv")


if __name__ == "__main__":
    convert()
