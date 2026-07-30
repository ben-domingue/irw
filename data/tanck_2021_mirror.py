from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0257303
# DOI: 10.1371/journal.pone.0257303
# Two scales, pre/post full-body-mirror-exposure: Eating Disorder
# Examination Questionnaire (EDE-Q, 28 items -- items 13/15 are frequency
# counts rather than 0-6 severity ratings, per the instrument's own mixed
# item design, not a data error) and Body Checking Questionnaire (BCQ, 23
# items). Source column numbering is zero-padded at "_pre" (BCQ_01_pre)
# but not at "_post" (BCQ_1_post) -- normalized to a shared item label.
# "Valence" (positive/negative verbalization condition) kept as a
# covariate rather than treat, since it's a between-subjects comparison
# condition within a single study arm, not a treatment-vs-control RCT.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0257303.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def make_scale(df: pd.DataFrame, out_name: str, prefix: str, n_items: int):
    cov_cols = ["Valence"] if "Valence" in df.columns else []
    frames = []
    for wave, suffix in enumerate(["pre", "post"]):
        cols = []
        for i in range(1, n_items + 1):
            c1 = f"{prefix}_{i:02d}_{suffix}"
            c2 = f"{prefix}_{i}_{suffix}"
            if c1 in df.columns:
                cols.append((c1, i))
            elif c2 in df.columns:
                cols.append((c2, i))
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=[c for c, _ in cols],
                       var_name="src_col", value_name="resp")
        item_map = {c: f"item{i}" for c, i in cols}
        long["item"] = long["src_col"].map(item_map)
        long["wave"] = wave
        frames.append(long.drop(columns=["src_col"]))

    long = pd.concat(frames, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "wave"] + cov_cols]

    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()
    df = df.rename(columns={"Number": "id"})
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    make_scale(df, "tanck_2021_edeq", "EDEQ", 28)
    make_scale(df, "tanck_2021_bcq", "BCQ", 23)


if __name__ == "__main__":
    convert()
