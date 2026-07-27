#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0323406
# DOI: 10.1371/journal.pone.0323406
# Supporting Information: https://doi.org/10.1371/journal.pone.0323406.s001
#
# Automated triage flagged this as n_items=1 -- wrong; the raw file has a
# 29-item ICU clinical-placement stressor scale and a 19-item coping-
# strategy scale, both 5-point frequency ratings (Never/Rarely.../Always).
# Two output files. Text responses parsed to 1-5; "Barely" and "Rarely"
# are used interchangeably as the 2nd-lowest category across different
# items (never both within the same item -- verified per-column) and
# mapped to the same value. Raw file has `Name` (4/127 non-null) and
# `Email` (127/127 non-null) columns -- real PII, dropped entirely (row
# counts checked via .notna(), values never printed/materialized).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0323406.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

FREQ_MAP = {"Never": 1, "Barely": 2, "Rarely": 2, "Sometimes": 3,
            "Frequently": 4, "Always": 5}

STRESSOR_COLS = [
    "Lack of experience and ability in providing nursing care and in making judgments",
    "Do not know how to help patients with physio-psycho-social problems",
    "Unable to reach one’s expectations",
    "Unable to provide appropriate responses to doctors’, teachers’, and patients’ questions",
    "Worry about not being trusted or accepted by patients or patients’ family",
    "Unable to provide patients with good nursing care",
    "Do not know how to communicate with patients",
    "Experience difficulties in changing from the role of a student to that of a nurse",
    "Experience discrepancy between theory and practice",
    "Do not know how to discuss patients’ illness with teachers, and medical and nursing personnel",
    "Feel stressed that teacher’s instruction is different from one’s expectations",
    "Medical personnel lack empathy and are not willing to help",
    "Feel that teachers do not give fair evaluation on students",
    "Lack of care and guidance from teachers",
    "Worry about bad grades",
    "Experience pressure from the nature and quality of clinical practice",
    "Feel that one’s performance does not meet teachers’ expectations",
    "Feel that the requirements of clinical practice exceed one’s physical and emotional   endurance",
    "Feel that dull and inflexible clinical practice affects one’s family and social life",
    "Experience competition from peers in school and clinical practice",
    "Feel pressure from teachers who evaluate students’ performance by comparison",
    "Feel that clinical practice affects one’s involvement in extracurricular activities",
    "Cannot get along with other peers in the group",
    "Unfamiliar with medical history and terms",
    "Unfamiliar with professional nursing skills",
    "Unfamiliar with patients’ diagnoses and treatments",
    "Feel stressed in the hospital environment where clinical practice takes place",
    "Unfamiliar with the ward facilities",
    "Feel stressed from the rapid change in patient’s condition",
]
COPING_COLS = [
    "To avoid difficulties during clinical practice",
    "To avoid teachers",
    "To quarrel with others and lose temper",
    "To expect miracles so one does not have to face difficulties",
    "To expect others to solve the problem",
    "To attribute to fate",
    "To adopt different strategies to solve problems",
    "To set up objectives to solve problems",
    "To make plans, list priorities, and solve stressful events",
    "To find the meaning of stressful incidents",
    "To employ past experience to solve problems",
    "To have confidence in performing as well as senior schoolmates",
    "To keep an optimistic and positive attitude in dealing with everything in life",
    "To see things objectively",
    "To have confidence in overcoming difficulties",
    "To cry, to feel moody, sad, and helpless",
    "To feast and take a long sleep",
    "To save time for sleep and maintain good health to face stress",
    "To relax via TV, movies, a shower, or physical exercises (ballplaying, jogging)",
]

COV_RENAME = {
    "\xa0What is your age in years?\xa0": "cov_age",
    "What is your marital status?": "cov_marital_status",
    "Income (self or family), can be described as": "cov_income",
    "In which semester you are?": "cov_semester",
}


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content))


def melt_scale(df: pd.DataFrame, cov_cols: list[str], item_cols: list[str], out_name: str):
    # Source column names are full sentences (meaningful but unwieldy) --
    # map to short, order-preserving generic labels, same convention as
    # datastandard.md's "no meaningful item labels" case.
    item_label = {col: f"item_{i:02d}" for i, col in enumerate(item_cols, 1)}
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = long["resp"].map(FREQ_MAP)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long["item"] = long["item"].map(item_label)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
    print(f"{out_name}.csv: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min()}-{long['resp'].max()}")


def convert():
    df = fetch_data()
    df = df.rename(columns={"ID": "id", **COV_RENAME})
    df = df.drop(columns=["Name", "Email"])
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    melt_scale(df, cov_cols, STRESSOR_COLS, "alkouri_2025_icu_stressors")
    melt_scale(df, cov_cols, COPING_COLS, "alkouri_2025_coping")


if __name__ == "__main__":
    convert()
