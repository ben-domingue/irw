#!/usr/bin/env python3
# Source: https://europepmc.org/article/PMC/PMC11470773
# DOI: 10.7717/peerj.18195
#
# Mancone, Tosti, Corrado & Diotaiuti (2024), "Effects of video game
# immersion and task interference on cognitive performance: a study on
# immediate and delayed recall and recognition accuracy." PeerJ.
# CC BY 4.0. N=160.
# Supplementary file peerj-12-18195-s001.sav has the Rey Auditory Verbal
# Learning Test (RAVLT) results: subjects heard a 15-word list and
# attempted recall over 5 successive learning trials, with each trial's
# raw correct-recall count (SESS_1-5, max 15) and intrusion-error count
# (INTRU_1-5) recorded separately -- these are per-trial raw scores, not
# an aggregate, so each set ships as its own file (SESS = recall count
# per trial, INTRU = intrusion-error count per trial) per datastandard.md's
# "one file per scale" rule. TOTALE_Repetitions/TOTAL_INTRUSIONS/
# DELAYED_RECALLS/FALSE_RICOGNITIONSI are summary/aggregate outcomes
# (sums or single delayed-recall/recognition scores) and are excluded.
# `group` (1-4: three experimental multitasking/task-switching conditions
# plus a control) is a 4-level factor, not a binary treat/control split,
# so it's kept as cov_group rather than `treat`. No PII in the raw file
# (ID is a sequential study ID; Uni_course is a university course name).

import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SUPPL_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11470773/supplementaryFiles"
MEMBER = "peerj-12-18195-s001.sav"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SESS_ITEMS = [f"SESS_{i}" for i in range(1, 6)]
INTRU_ITEMS = [f"INTRU_{i}" for i in range(1, 6)]

COV_MAP = {
    "gender": "cov_gender",
    "group": "cov_group",
    "gaming_prevalence": "cov_gaming_prevalence",
    "expertise_years": "cov_expertise_years",
    "age": "cov_age",
}


def fetch_raw() -> pd.DataFrame:
    r = requests.get(SUPPL_URL, headers=UA, timeout=120)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    with zf.open(MEMBER) as f:
        return pd.read_spss(io.BytesIO(f.read()), convert_categoricals=False)


def build_long(raw: pd.DataFrame, items: list[str], cov_cols: list[str]) -> pd.DataFrame:
    keep = ["id"] + items + cov_cols
    long = raw[keep].melt(id_vars=["id"] + cov_cols, value_vars=items,
                           var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    return long[["id", "item", "resp"] + cov_cols]


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    raw = fetch_raw()
    raw = raw.rename(columns={"ID": "id", **COV_MAP})
    raw["id"] = raw["id"].astype(int)
    assert raw["id"].nunique() == len(raw)

    cov_cols = list(COV_MAP.values())

    recall = build_long(raw, SESS_ITEMS, cov_cols)
    intrusions = build_long(raw, INTRU_ITEMS, cov_cols)

    write_scale(recall, "mancone_2024_ravlt_recall.csv")
    write_scale(intrusions, "mancone_2024_ravlt_intrusion.csv")


if __name__ == "__main__":
    convert()
