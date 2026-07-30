from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0201216
# DOI: 10.1371/journal.pone.0201216
# The raw file also has IVAMIt1-16 and xNAR1-9 item blocks not described
# anywhere in this paper's Measures section (only SCID, SCL-90-R, TAS-20,
# and the MAI clinical interview are documented) -- left unshipped rather
# than guessed at. SCL-90-R items range 0-4 in this file even though the
# paper's own text paraphrases the anchors as "1=not at all to 4=very
# much"; 0 recurs proportionally across every item (not isolated), so it's
# treated as a real response category, consistent with the standard SCL-90
# 0-4 convention.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0201216.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "AGE": "cov_age",
    "GENDER": "cov_gender",
    "NOPD_OTHERPD_NPD": "cov_diagnosis_group",
}

SCALES = {
    "bilotta_2018_tas20": r"TAS20It\d+$",
    "bilotta_2018_scl90": r"SCL\d+$",
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = fetch()
    df = df.rename(columns={"CARD": "id"})
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    df = df.rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    assert df["id"].nunique() == len(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for out_name, pattern in SCALES.items():
        pat = re.compile(pattern)
        item_cols = [c for c in df.columns if pat.fullmatch(c)]
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]

        out_path = OUT_DIR / f"{out_name}.csv"
        long.to_csv(out_path, index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
