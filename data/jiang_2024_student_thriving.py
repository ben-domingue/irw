from __future__ import annotations

import io
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0312338
# DOI: 10.1371/journal.pone.0312338
# Jiang et al. (2024), "Psychological sense of community as mediator and
# growth mindset as moderator in the impact of institutional integrity
# and perceived teacher support on student thriving: Evidence from
# private universities in China". S1 Data. CC BY 4.0. N=1792.
# A large bundle of ~21 column-prefix-coded subscales (no item text in
# the file), 1-5 Likert -- each block shipped under its raw source
# prefix as a separate scale. `totalseconds` is whole-survey completion
# time (seconds), not a per-item response time -- per datastandard.md,
# the `rt` column name is reserved for response-level (per-item) timing,
# so this is kept as a covariate (`cov_completion_time_s`) instead of
# `rt`. Non-prefix-numbered demographic columns (Gender/Age/Home/...)
# kept as covariates where clearly labeled.
URL = ("https://journals.plos.org/plosone/article/file"
       "?type=supplementary&id=10.1371/journal.pone.0312338.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {"Gender": "cov_gender", "Age": "cov_age", "ClassL": "cov_class_level",
           "Degree": "cov_degree", "Major": "cov_major",
           "totalseconds": "cov_completion_time_s"}

ITEM_RE = re.compile(r"^([A-Za-z]+)(\d+)$")

# Item columns hold text-coded 7-point Likert responses (Chinese), not
# numeric codes -- recoded 1 (strongly disagree) - 7 (strongly agree).
LIKERT_MAP = {
    "非常不同意": 1, "不同意": 2, "有些不同意": 3, "既不同意也不反对": 4,
    "有些同意": 5, "同意": 6, "非常同意": 7,
}


def fetch() -> pd.DataFrame:
    r = requests.get(URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_spss(io.BytesIO(r.content))
    df = df.rename(columns={**COV_MAP, "index": "id"})
    for c in df.columns:
        if ITEM_RE.match(str(c)):
            df[c] = df[c].map(LIKERT_MAP)
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
        out_name = f"jiang_2024_{prefix.lower()}"
        keep_cols = ["id"] + cov_cols
        long = df.melt(id_vars=keep_cols, value_vars=item_cols, var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[["id", "item", "resp"] + cov_cols]
        long.to_csv(OUT_DIR / f"{out_name}.csv", index=False)
        print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
