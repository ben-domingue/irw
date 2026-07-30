from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0159647
# DOI: 10.1371/journal.pone.0159647
# RCT of paroxetine vs. placebo for depression. Three instruments, each
# scored at intake (wave 0) and week 8 (wave 1): Hamilton Rating Scale for
# Depression (HRSD; "hrsd*"=intake, "h08d*"=week8 -- week8 also includes 7
# extended items (18-24) not scored at intake, kept as wave=1-only items,
# which is valid per datastandard.md's longitudinal-data rules), Hamilton
# Rating Scale for Anxiety (HRSA; "hrsa*"/"h08a*"), and the Beck Anxiety
# Inventory (BAI, 21 items, 0-3) -- confirmed by item count and the paper's
# text (which discusses BAI results at length) even though the raw file
# labels these columns "si*"/"s08i*" rather than "bai*". Per-item value
# ranges vary (e.g. some HRSD items 0-2, others 0-4) -- this is the
# instrument's own known item-specific scoring, not a data-entry issue.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0159647.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df, _ = pyreadstat.read_sav(io.BytesIO(r.content))
    return df


def make_scale(df: pd.DataFrame, out_name: str, wave0_prefix: str, wave1_prefix: str,
              item_prefix: str):
    cols0 = [c for c in df.columns if re.fullmatch(wave0_prefix + r"\d+[a-z]?", c)]
    cols1 = [c for c in df.columns if re.fullmatch(wave1_prefix + r"\d+[a-z]?", c)]

    long0 = df.melt(id_vars=["id", "treat"], value_vars=cols0,
                    var_name="item", value_name="resp")
    long0["item"] = item_prefix + long0["item"].str[len(wave0_prefix):]
    long0["wave"] = 0

    long1 = df.melt(id_vars=["id", "treat"], value_vars=cols1,
                    var_name="item", value_name="resp")
    long1["item"] = item_prefix + long1["item"].str[len(wave1_prefix):]
    long1["wave"] = 1

    long = pd.concat([long0, long1], ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp", "wave", "treat"]]

    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()
    df = df.rename(columns={"patnod": "id", "TAF1": "treat"})
    assert df["id"].nunique() == len(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    make_scale(df, "schalet_2016_hrsd", "hrsd", "h08d", "d")
    make_scale(df, "schalet_2016_hrsa", "hrsa", "h08a", "a")
    make_scale(df, "schalet_2016_bai", "si", "s08i", "bai")


if __name__ == "__main__":
    convert()
