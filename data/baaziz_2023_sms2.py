from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0295262
# DOI: 10.1371/journal.pone.0295262
# Baaziz et al. (2023), "Transcultural validation of the 'revised sport
# motivation scale' (SMS-II) in Arabic language ... Tunisian Athletes".
# CC0 1.0. All 18 items 7-point Likert (1-7).
#
# NOTE on file selection: the article's own Supporting Information list
# captions 3 XLSX files as: S1 Data (.s001) = "Data of the 780 athletes",
# S2 Data (.s002) = "Data SMS-II-EFA (N=390)", S3 Data (.s003) =
# "Data SMS-II-CFA (N=390)". The captions and actual file contents do not
# match: .s001 (fetched and verified via HTTP redirect to the exact
# `pone.0295262.s001.xlsx` object) actually contains only 390 rows with
# plain integer ids, and .s003 actually contains 780 rows whose id strings
# are prefixed "EFA"/"CFA"/"CFA.test"/"CFA.retest" -- i.e. .s003 is the
# genuine combined 780-athlete file the S1 Data caption describes (390
# EFA-phase + 390 CFA-phase, the latter including a 51-person test/retest
# reliability sub-study nested inside it). This script therefore uses
# .s003 as the full raw sample rather than trusting the caption-to-file
# mapping, since it is the internally consistent, complete dataset.
# Aggregate SDT subscale-mean columns (IM, Int.M, Id.R, Intro.R, ER, AMO)
# are excluded as composites, not raw item responses. Each row's `id`
# (the source `identifiant` string, e.g. "EFA12", "CFA45", "CFA.test391",
# "CFA.retest391") is kept as given -- the 51 test/retest pairs are
# therefore two distinct string ids per person (first vs. second
# administration), not merged, since the source data does not provide an
# unambiguous common person key across the two occasions.

URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0295262.s003")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_COLS = {
    "Age": "cov_age",
    "recoded.Age": "cov_age_group",
    "Sexe": "cov_gender",
    "sport": "cov_sport",
    "Region": "cov_region",
}


def convert():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"identifiant": "id", **COV_COLS})
    assert df["id"].is_unique and df["id"].notna().all()

    item_cols = [f"Item{i}" for i in range(1, 19)]
    cov_names = list(COV_COLS.values())
    long = df.melt(id_vars=["id"] + cov_names, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_names]
    path = OUT_DIR / "baaziz_2023_sms2.csv"
    long.to_csv(path, index=False)
    print(f"baaziz_2023_sms2.csv: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
