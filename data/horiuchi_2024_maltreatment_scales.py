#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0298214
# DOI: 10.1371/journal.pone.0298214
# Horiuchi, Nishimura, Taniike & Tachibana (2024), "Development of a rating
# scale for maladaptive symptoms by maltreatment: Perspectives of attachment
# and dissociation", PLOS ONE. CC BY 4.0.
# Two raw files:
#   Survey 1: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0298214.s008
#     -- attach1-20 (items selected from the Attachment Disorder Assessment
#        Scale-Revised, ADAS-R), dissoc1-20 (Child Dissociative Checklist, CDC)
#   Survey 2: https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0298214.s009
#     -- MSM1-20, the newly developed RS-MSM scale (combines/modifies ADAS-R + CDC items)
# Both files have a blank super-header row above the real column-name row
# (header offset of 2, 0-indexed).

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

UA = {"User-Agent": "irw-batch/1.0 (research)"}
URL_S1 = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0298214.s008"
URL_S2 = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0298214.s009"


def _fetch(url: str, header: int) -> pd.DataFrame:
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return pd.read_excel(io.BytesIO(r.content), header=header)


def _add_cov_sex(df: pd.DataFrame) -> pd.DataFrame:
    df["cov_sex"] = df["male"].map({1: "male"}).fillna(df["female"].map({1: "female"}))
    return df.drop(columns=["male", "female"])


def _melt(df: pd.DataFrame, item_cols: list[str]) -> pd.DataFrame:
    cov_cols = ["cov_sex", "cov_abuse", "cov_age", "cov_grade"]
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    return long[["id", "item", "resp"] + cov_cols]


def convert():
    s1 = _fetch(URL_S1, header=2)
    s1 = s1.rename(columns={"ID": "id", "abuse": "cov_abuse", "age": "cov_age", "grade": "cov_grade"})
    s1 = _add_cov_sex(s1)

    attach_cols = [c for c in s1.columns if c.startswith("attach")]
    dissoc_cols = [c for c in s1.columns if c.startswith("dissoc")]

    s2 = _fetch(URL_S2, header=1)
    s2 = s2.rename(columns={"ID": "id", "abuse": "cov_abuse", "age": "cov_age", "grade": "cov_grade"})
    s2 = _add_cov_sex(s2)
    msm_cols = [c for c in s2.columns if c.startswith("MSM")]

    tables = {
        "horiuchi_2024_attachment": (s1, attach_cols),
        "horiuchi_2024_dissociation": (s1, dissoc_cols),
        "horiuchi_2024_rsmsm": (s2, msm_cols),
    }
    for out_name, (df, item_cols) in tables.items():
        long = _melt(df, item_cols)
        path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
