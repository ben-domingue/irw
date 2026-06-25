from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
ARCHIVE = BASE / "osfstorage-archive (2)"
OUT = BASE / "kay_2025_antonyms"
DATA = ARCHIVE / "data"


SAMPLES = [
    ("data_1_deidentified.csv",   "Connect"),
    ("data_2_deidentified.xlsx",  "Prolific"),
    ("data_3_deidentified.xlsx",  "MTurk_400"),
    ("data_4_deidentified.xlsx",  "MTurk_600"),
]

ITEM_PATTERN = re.compile(r"^sasx_([a-z]+\d?)_xxxx_(\d+)_([xr])$")

COV_COLS = ["gender", "culture", "education", "income", "ses_1",
            "poli_cat", "poli_cont", "att_chk"]


def _read(filename: str) -> pd.DataFrame:
    path = DATA / filename
    return pd.read_csv(path) if path.suffix == ".csv" else pd.read_excel(path)


def _load_sample(filename: str, source: str) -> pd.DataFrame:
    df = _read(filename)
    df = df[df["finished"] == 1].copy()

    rename = {}
    for col in df.columns:
        m = ITEM_PATTERN.match(col)
        if m:
            rename[col] = f"{m.group(1)}_{m.group(2)}_{m.group(3)}"
    df = df.rename(columns=rename)
    item_cols = sorted(rename.values())

    keep = ["response_id"] + item_cols + [c for c in COV_COLS if c in df.columns]
    sel = df[keep].copy()
    sel["cov_source"] = source
    return sel, item_cols


def main() -> None:
    parts, all_items = [], None
    for filename, source in SAMPLES:
        sel, items = _load_sample(filename, source)
        if all_items is None:
            all_items = items
        parts.append(sel)
    wide = pd.concat(parts, ignore_index=True)
    wide = wide.rename(columns={"response_id": "id"})

    id_vars = ["id", "cov_source"] + [f"cov_{c}" if c != "att_chk" else "cov_att_chk"
                                       for c in COV_COLS if any(c in p.columns for p in parts)]
    rename_covs = {c: (f"cov_{c}") for c in COV_COLS if c in wide.columns}
    wide = wide.rename(columns=rename_covs)
    id_vars = ["id", "cov_source"] + list(rename_covs.values())

    long = wide.melt(id_vars=id_vars, value_vars=all_items,
                     var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + id_vars[1:]]
    long = long.sort_values(["cov_source", "id", "item"], kind="stable").reset_index(drop=True)

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "kay_2025_antonyms.csv"
    long.to_csv(path, index=False)
    print(f"{path.name}: rows={len(long):,}, ids={long['id'].nunique()}, "
          f"items={long['item'].nunique()}, "
          f"resp_range=[{long['resp'].min()},{long['resp'].max()}], "
          f"sources={sorted(long['cov_source'].unique())}")
    print("retained per source (finished==1):")
    print(long.groupby('cov_source')['id'].nunique().to_string())


if __name__ == "__main__":
    main()
