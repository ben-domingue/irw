#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0289553
# DOI: 10.1371/journal.pone.0289553
# "Adolescent relational behaviour and the obesity pandemic: a study of the
# mechanisms of influence of social contagion in Spanish schoolchildren"
# (Marques-Sanchez et al., 2023). N=235 students from 11 classrooms in 5
# schools.
#
# SI file used: S1 Data (SAV, the only SI file),
# https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0289553.s001&type=supplementary
# License: CC BY 4.0 (confirmed on article page).
#
# The SI file (139 columns) is dominated by two categories of columns that
# are NOT raw item responses and are excluded here:
#   - Friendship-network centrality metrics (D1/D2/D3 NrmOutDeg, NrmInDeg,
#     Closeness, Betweenness, Eigenvec, ...): these are derived graph-theory
#     composites computed from the raw "who do you spend time with"
#     nomination matrix, not per-item responses -- excluded as composites.
#   - Aggregate/terciles/dichotomized columns (ALI total score, IALI2,
#     tercilesALI, dicALI, CAS* combined screen-time sums, terciles*, CAF
#     composite, Percentile, BMC-derived groupings, etc.): excluded as
#     aggregate/derived per datastandard.md.
#   - HOURS* columns (per-medium weekly screen-time hours: TV, DVD, video
#     games, etc.) look like a plausible raw item battery but the paper's
#     own Methods text states only "gender, diet and friendship network
#     were collected" -- no screen-time/media-use instrument is described
#     anywhere in this paper. Since we cannot verify the item wording,
#     response scale, or provenance of these columns against this paper's
#     text (per datastandard.md's "verify against paper text" rule for
#     continuous columns), they are excluded rather than guessed at.
#
# The only item battery the paper's Methods text explicitly describes is
# the KIDMED Test of Adherence to the Mediterranean Diet -- the standard
# 16-item yes/no diet questionnaire (raw binary items ALIFD...ALIGC below;
# the ALI column itself is the 0-12 aggregate KIDMED score and is excluded).
#
# id verification: ID is unique per row (235 rows, 235 unique values) --
# confirmed with nunique()==len(df), overriding the triage's low-confidence
# flag on this column.

import io
import os

import pandas as pd
import pyreadstat
import requests

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SRC_URL = ("https://journals.plos.org/plosone/article/file?"
           "id=10.1371/journal.pone.0289553.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

KIDMED_COLS = [
    "ALIFD", "ALI2FD", "ALIVD", "ALI2VD", "ALIP", "ALIH", "ALIL", "ALIPA",
    "ALIC", "ALIFS", "ALIAO", "ALIDES", "ALILAC", "ALIBI", "ALIY", "ALIGC",
]

COV_RENAME = {
    "AGE": "cov_age",
    "GENDER": "cov_gender",
    "IDSCHOOL": "cov_school",
    "IDCLASS": "cov_class",
    "BMC": "cov_bmi",
}


def load_raw() -> pd.DataFrame:
    r = requests.get(SRC_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = load_raw()

    df = df.rename(columns={"ID": "id"})
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id column is not unique per person"

    df = df.rename(columns=COV_RENAME)
    cov_cols = list(COV_RENAME.values())

    os.makedirs(OUT_DIR, exist_ok=True)

    sub = df[["id"] + cov_cols + KIDMED_COLS].copy()
    long = sub.melt(id_vars=["id"] + cov_cols, value_vars=KIDMED_COLS,
                     var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)

    out_cols = ["id", "item", "resp"] + cov_cols
    long = long[out_cols]

    out_name = "marquessanchez_2023_kidmed"
    out_path = os.path.join(OUT_DIR, f"{out_name}.csv")
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
