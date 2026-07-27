#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0217848
# DOI: 10.1371/journal.pone.0217848
# Supporting Information: https://doi.org/10.1371/journal.pone.0217848.s002 (Study 1)
#
# Study 1 (N=106): online validation of the Velten Mood Induction
# Procedure -- 80 individual mood statements (e.g. "I can make any
# situation turn out right" / "When I talk no one really listens"),
# each rated 1(very unhappy)-9(very happy). Item wording confirmed via
# SPSS variable labels (LimeSurvey's opaque `vNN_SQ001` codes only
# resolve to real item text through the labels, not the column names
# themselves). Exported as text with the endpoint categories spelled out
# ("1(very unhappy)", "9(very happy)") and bare digits in between; a
# regex on the leading digit recovers the 1-9 code uniformly (one
# category set confirmed across all 80 items). The 2 `ctrlvelten*`
# columns are attention-check items ("Select alternative 3 here"), not
# real mood statements, excluded. `device`/`device_other` are covariates,
# not items.
#
# Study 2 (S3 file) was not processed here -- it uses fully different,
# pre-identified PANAS-style items (sad/happy/joyful/etc., already named
# plainly) rather than the raw Velten statement pool, and is a
# structurally distinct design; left for a possible separate pass.

from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?type=supplementary&id=10.1371/journal.pone.0217848.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_RENAME = {"Gender": "cov_sex", "age": "cov_age", "device": "cov_device"}


def parse_resp(v) -> float:
    if v is None:
        return float("nan")
    m = re.match(r"^(\d)", str(v).strip())
    return float(m.group(1)) if m else float("nan")


def fetch_data() -> pd.DataFrame:
    r = requests.get(SI_URL, headers=UA, timeout=60)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    return df.rename(columns=COV_RENAME)


def convert():
    df = fetch_data()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_RENAME.values())

    item_cols = [c for c in df.columns if c.startswith("v") and c.endswith("_SQ001") and c[1].isdigit()]
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols, var_name="item", value_name="resp")
    long["item"] = long["item"].str.replace("_SQ001", "", regex=False)
    long["resp"] = long["resp"].map(parse_resp)
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / "marcussonclavertz_2019_velten.csv", index=False)
    print(f"marcussonclavertz_2019_velten.csv: ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
