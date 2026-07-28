#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0141875
# DOI: 10.1371/journal.pone.0141875
# Supporting Information: https://doi.org/10.1371/journal.pone.0141875.s001
#
# The raw file has every respondent duplicated as two byte-identical rows
# (an export artifact, confirmed by comparing full rows within each
# "number" id) -- deduplicated here before melting. The t1-t104 item block
# combines several constructs (essentialism, multicultural ideology,
# cultural anxiety) under undifferentiated names with no codebook to split
# them further, so they are kept as one file. The "reverset*" columns are
# manually reverse-coded duplicates of a subset of t-items and are
# excluded (datastandard.md: don't recode/duplicate reverse-scored items),
# as are the derived composite columns (essentialism, mutideology,
# culanxiety, ZSco01). q1/q3/q4/q5/q7 are kept as demographic covariates;
# q2 (entirely empty) and the remaining ambiguous q-columns are dropped.
# One isolated non-integer value (3.75 on t80, a single respondent, vs.
# clean 1-7 integers for everyone else on that item) is a data-entry
# error and is dropped.

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0141875.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"q1": "cov_gender", "q3": "cov_class_year", "q4": "cov_ethnicity",
              "q5": "cov_region", "q7": "cov_ethnicity_self"}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={"number": "id", **COV_RENAME})
    df = df.drop_duplicates(subset=["id"]).reset_index(drop=True)

    item_cols = [f"t{i}" for i in range(1, 105)]
    cov_cols = list(COV_RENAME.values())
    for c in cov_cols:
        df[c] = df[c].astype(str)

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long.loc[long["resp"] % 1 != 0, "resp"] = float("nan")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_name = "yang_2015_ethnic_essentialism.csv"
    long.to_csv(OUT_DIR / out_name, index=False)
    print(f"{out_name}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
