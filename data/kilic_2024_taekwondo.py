#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC10984172
# DOI: 10.7717/peerj.17174
#
# Kilic (2024), "Attitude towards healthy nutrition and mental toughness:
# a study of taekwondo athletes." PeerJ. CC BY 4.0. N=276.
# Supplementary file peerj-12-17174-s002.xls has two clean raw-item scales
# (1-5 Likert each): a 21-item nutrition-attitude questionnaire and an
# 11-item mental toughness questionnaire, split per datastandard.md's
# "one file per scale" rule.

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10984172/supplementaryFiles"
MEMBER = "peerj-12-17174-s002.xls"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

NUTRITION_COLS = [f"Nutrition  question {i}" if i in (4, 5, 6) else f"Nutrition question {i}"
                   for i in range(1, 22)]
MT_COLS = ["MT \nquestion 1"] + [f"MT question {i}" for i in range(2, 12)]


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with zf.open(MEMBER) as f:
        return pd.read_excel(f, sheet_name="data")


def build_long(raw: pd.DataFrame, cols: list[str], prefix: str) -> pd.DataFrame:
    cov = pd.DataFrame({
        "id": raw["number"],
        "cov_gender": raw["female=1"].fillna(raw["\n\n male= 2"]).map({1.0: "female", 2.0: "male"}),
        "cov_age": raw["age"],
    })
    long = raw[cols].copy()
    long.columns = [f"{prefix}{i + 1}" for i in range(len(cols))]
    long["id"] = raw["number"]
    long = long.melt(id_vars="id", var_name="item", value_name="resp")
    long = long.merge(cov, on="id")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    return long[["id", "item", "resp", "cov_gender", "cov_age"]]


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    raw = fetch_raw()
    nutrition = build_long(raw, NUTRITION_COLS, "nq")
    mt = build_long(raw, MT_COLS, "mtq")
    write_scale(nutrition, "kilic_2024_nutrition_attitude.csv")
    write_scale(mt, "kilic_2024_mental_toughness.csv")


if __name__ == "__main__":
    convert()
