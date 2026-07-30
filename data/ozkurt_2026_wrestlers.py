from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0353067
# DOI: 10.1371/journal.pone.0353067
# Uses S2_File.sav (clean per-instrument column labels: EGOQ/BPNS/SMS/PACES/INT)
# rather than S1_File.xlsx, whose item headers are ambiguous/incomplete
# (e.g. missing item 1, mislabeled "Ego Orientation"/"Task Orientation" per
# column) for the same underlying data.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0353067.s002")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "D1": "cov_age",
    "D4": "cov_gender",
    "D5": "cov_education",
    "D6": "cov_wrestling_style",
    "D7": "cov_sport_experience",
}

SCALES = {
    "ozkurt_2026_ego_orientation": r"EGOQ\d+$",
    "ozkurt_2026_basic_psych_needs": r"BPNS\d+$",
    "ozkurt_2026_sport_motivation": r"SMS\d+$",
    "ozkurt_2026_paces_enjoyment": r"PACES\d+$",
    "ozkurt_2026_continuance_intention": r"INT\d+$",
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def convert():
    df = fetch()
    df = df.reset_index(drop=True)
    df.insert(0, "id", df.index + 1)
    df = df.rename(columns=COV_MAP)
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]

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
