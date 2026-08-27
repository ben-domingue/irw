from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

DOI   = "10.7910/DVN/ALYGQS"
TITLE = ("Replication Data for: Does Islamist Terrorism Still Affect "
         "Political Attitudes?")
UA    = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_ID = 13400055  # LondonBridgeAttack2017.tab

IMM_ITEMS     = ["imm1", "imm2", "imm3"]
REDISTR_ITEMS = ["redistr1", "redistr2", "redistr3", "redistr4"]
STATINT_ITEMS = ["statint1", "statint2"]
ENV_ITEMS     = ["env1", "env2"]
NATID_ITEMS   = ["englid", "britid", "euid", "scotid", "welshid"]

COV_MAP = {
    "gender": "cov_gender",
    "age":    "cov_age",
    "edu":    "cov_edu",
    "pol_interest": "cov_pol_interest",
    "lr":     "cov_lr",
    "region": "cov_region",
}
COV_ORDER = list(COV_MAP.values()) + ["cov_attack_timing"]


def fetch_data() -> pd.DataFrame:
    url = f"https://dataverse.harvard.edu/api/access/datafile/{FILE_ID}"
    r = requests.get(url, headers=UA, timeout=300, stream=True)
    r.raise_for_status()
    chunks = []
    for chunk in r.iter_content(chunk_size=1 << 20):
        chunks.append(chunk)
    return pd.read_csv(io.BytesIO(b"".join(chunks)), sep="\t", low_memory=False)


def derive_attack_timing(df: pd.DataFrame) -> pd.Series:
    # Each respondent appears exactly once (76,466 rows, 76,466 distinct
    # newid), so pre/during/post separates *different* people interviewed
    # before, during and after the London Bridge attack. That is a
    # between-subjects grouping, not a longitudinal wave, so it ships as a
    # covariate (see datastandard.md).
    attack     = pd.to_numeric(df["attack"],     errors="coerce")
    postattack = pd.to_numeric(df["postattack"], errors="coerce")
    timing = pd.Series("pre", index=df.index)
    timing[postattack == 1] = "post"
    timing[attack == 1]     = "during"
    return timing


def make_scale(df: pd.DataFrame, items: list[str], resp_as_float: bool = False) -> pd.DataFrame:
    cov_cols = [c for c in COV_ORDER if c in df.columns]
    long = df[["id"] + cov_cols + items].melt(
        id_vars=["id"] + cov_cols,
        value_vars=items,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    if not resp_as_float:
        long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp"] + cov_cols
    return long[col_order].sort_values(["id", "item"]).reset_index(drop=True)


def write_scale(long: pd.DataFrame, fname: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT_DIR / fname, index=False)
    resp_min = long["resp"].min()
    resp_max = long["resp"].max()
    print(f"{fname}: ids={long['id'].nunique()} items={long['item'].nunique()} "
          f"resp={resp_min}-{resp_max}")


def convert():
    print("Downloading LondonBridgeAttack2017.tab …")
    raw = fetch_data()
    raw.columns = raw.columns.str.lower()

    # `id` restarts from 1 in each of the three country sub-samples, so it
    # collides across them; `newid` (= country prefix * 100000 + id) is
    # unique across all rows and is the real person identifier.
    raw["id"] = raw["newid"].astype("Int64")

    raw["cov_attack_timing"] = derive_attack_timing(raw)
    for src, dst in COV_MAP.items():
        if src in raw.columns:
            raw = raw.rename(columns={src: dst})

    scales = [
        (IMM_ITEMS,     "germann_2026_immigration.csv",       False),
        (REDISTR_ITEMS, "germann_2026_redistribution.csv",    False),
        (STATINT_ITEMS, "germann_2026_state_intervention.csv", False),
        (ENV_ITEMS,     "germann_2026_environment.csv",        False),
        (NATID_ITEMS,   "germann_2026_national_identity.csv",  True),
    ]

    for items, fname, as_float in scales:
        long = make_scale(raw, items, resp_as_float=as_float)
        write_scale(long, fname)


if __name__ == "__main__":
    convert()
