from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0138219
# DOI: 10.1371/journal.pone.0138219
# Wang, Tang & Wang (2015), N=371 (208 Chinese, 163 American). Each
# participant read one donation scenario (1 vs. 8 sick children x
# identified vs. unidentified, between-subjects) and rated: distress
# ("felt worried, upset, sad") and sympathy ("felt sympathy and
# compassion"), each on the paper's 7-point scale (raw codes run 0-7,
# 8 steps); and Q4WTC, the raw donation amount out of 100
# yuan/dollars (kept as-collected, by-10s). `WTC` (a log-transformed
# version of Q4WTC, per the paper's own normality-driven transform for
# analysis) and `count` (a derived donated-something binary) are
# excluded as composites/transforms, not raw responses.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0138219.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "country": "cov_country",
    "gender": "cov_gender",
    "condition1singleun2singlein3groupun4groupin": "cov_condition",
    "GroupVSsingle1single2group": "cov_group_vs_single",
    "identified1unidentified2identified": "cov_identified",
}

ITEM_MAP = {
    "distress": "distress",
    "sympthy": "sympathy",
    "Q4WTC": "wtc_amount",
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content))
    df = df.rename(columns={"subject": "id", **COV_MAP})
    return df


def convert():
    df = fetch()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_MAP.values())

    long = df.melt(id_vars=["id"] + cov_cols, value_vars=list(ITEM_MAP.keys()),
                    var_name="item", value_name="resp")
    long["item"] = long["item"].map(ITEM_MAP)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    long = long[["id", "item", "resp"] + cov_cols]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "wang_2015_donation_decision.csv"
    long.to_csv(out_path, index=False)
    print(f"wang_2015_donation_decision: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
