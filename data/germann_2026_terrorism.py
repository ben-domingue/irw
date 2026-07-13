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


def fetch_data() -> pd.DataFrame:
    url = f"https://dataverse.harvard.edu/api/access/datafile/{FILE_ID}"
    r = requests.get(url, headers=UA, timeout=300, stream=True)
    r.raise_for_status()
    chunks = []
    for chunk in r.iter_content(chunk_size=1 << 20):
        chunks.append(chunk)
    return pd.read_csv(io.BytesIO(b"".join(chunks)), sep="\t", low_memory=False)


def derive_wave(df: pd.DataFrame) -> pd.Series:
    attack    = pd.to_numeric(df["attack"],    errors="coerce")
    postattack = pd.to_numeric(df["postattack"], errors="coerce")
    wave = pd.Series("pre", index=df.index)
    wave[postattack == 1] = "post"
    wave[attack == 1]     = "during"
    return wave


def make_scale(df: pd.DataFrame, items: list[str], resp_as_float: bool = False) -> pd.DataFrame:
    cov_cols = [c for c in COV_MAP.values() if c in df.columns]
    long = df[["id", "wave"] + cov_cols + items].melt(
        id_vars=["id", "wave"] + cov_cols,
        value_vars=items,
        var_name="item",
        value_name="resp",
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"]).reset_index(drop=True)
    if not resp_as_float:
        long["resp"] = long["resp"].astype(int)
    col_order = ["id", "item", "resp", "wave"] + cov_cols
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

    raw["wave"] = derive_wave(raw)
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
