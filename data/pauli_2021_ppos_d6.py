#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC8667738
# DOI: 10.7717/peerj.12604
#
# Pauli & Wilhelmy (2021), "A short scale for measuring attitudes towards
# the doctor-patient relationship: psychometric properties and measurement
# invariance of the German Patient-Practitioner-Orientation Scale
# (PPOS-D6)." PeerJ. CC BY 4.0. N=332.
# Supplementary file peerj-09-12604-s003.xlsx has two raw item batteries
# (0-5 agreement scale, -99 sentinel for missing): the 6-item PPOS-D6
# scale (v1.1-v1.6) and a 15-item coercion-in-medicine attitude scale
# (v6.1-v6.15), split per datastandard.md's "one file per scale" rule.
# v7/v8 are open free-text responses, excluded (not scale items).

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8667738/supplementaryFiles"
MEMBER = "peerj-09-12604-s003.xlsx"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

PPOS_COLS = [f"v1.{i}" for i in range(1, 7)]
COERCION_COLS = [f"v6.{i}" for i in range(1, 16)]

GENDER_MAP = {0: "female", 1: "male", 2: "other"}
DEGREE_MAP = {1: "human_medicine", 2: "dentistry", 3: "speech_therapy", 4: "doctoral_studies"}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with zf.open(MEMBER) as f:
        return pd.read_excel(f, sheet_name="PPOS-D6 raw dataset2")


def build_long(raw: pd.DataFrame, cols: list[str], prefix: str) -> pd.DataFrame:
    cov = pd.DataFrame({
        "id": raw["ID"],
        "cov_gender": raw["v4"].map(GENDER_MAP),
        "cov_degree_program": raw["v3"].map(DEGREE_MAP),
        "cov_birth_year": raw["v5"],
    })
    long = raw[cols].copy()
    long.columns = [f"{prefix}{i + 1}" for i in range(len(cols))]
    long["id"] = raw["ID"]
    long = long.melt(id_vars="id", var_name="item", value_name="resp")
    long = long[long["resp"] != -99]
    long = long.merge(cov, on="id")
    long["resp"] = long["resp"].astype(int)
    return long[["id", "item", "resp", "cov_gender", "cov_degree_program", "cov_birth_year"]]


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    raw = fetch_raw()
    ppos = build_long(raw, PPOS_COLS, "ppos")
    coercion = build_long(raw, COERCION_COLS, "coercion")
    write_scale(ppos, "pauli_2021_ppos_d6.csv")
    write_scale(coercion, "pauli_2021_coercion_attitudes.csv")


if __name__ == "__main__":
    convert()
