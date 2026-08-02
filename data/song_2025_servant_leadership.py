from __future__ import annotations

import io
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0323811
# DOI: 10.1371/journal.pone.0323811
# Song et al. (2025), "The dilemma of frontline servant leadership: The
# conflict between top management directives and grassroots employee
# wellbeing and retention". S1 Appendix. CC BY 4.0. N=486. 15 column-
# prefix-coded scales (no item text in the file), 1-5 Likert -- each
# shipped under its raw source prefix.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0323811.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Gender": "cov_gender", "Age": "cov_age", "Education level": "cov_education",
           "Years of work": "cov_years_work"}
ITEM_RE = re.compile(r"^([A-Za-z]+)(\d+)$")


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns=COV_MAP)
    df["id"] = range(1, len(df) + 1)
    return df


def convert():
    df = fetch()
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    groups = defaultdict(list)
    for c in df.columns:
        m = ITEM_RE.match(str(c))
        if m:
            groups[m.group(1)].append(c)
    groups = {k: v for k, v in groups.items() if len(v) >= 2}

    for prefix, item_cols in groups.items():
        out_name = f"song_2025_{prefix.lower()}"
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
