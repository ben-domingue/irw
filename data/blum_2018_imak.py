from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
OUT = BASE / "blum_2018_imak"
SRC = BASE / "Data Sheet 1" / "Unpurified data matrix with variable definitions.xlsx"


COV_RENAME = {
    "Age":       "cov_age",
    "Gender":    "cov_gender",
    "Secondary": "cov_secondary",
    "Country":   "cov_country",
    "Language":  "cov_language",
}


def _load() -> pd.DataFrame:
    df = pd.read_excel(SRC, sheet_name="Unpurified data matrix")
    return df.rename(columns={"Participant": "id", **COV_RENAME})


def _build_bin(df: pd.DataFrame, outname: str) -> None:
    cov = list(COV_RENAME.values())
    id_vars = ["id"] + cov
    item_nums = sorted(
        int(c[len("Binary"):])
        for c in df.columns if re.match(r"^Binary\d+$", c)
    )

    rows = []
    for n in item_nums:
        bin_col = f"Binary{n}"
        time_col = f"Time{n}"
        chunk = df[id_vars + [bin_col, time_col]].copy()
        chunk["item"] = f"item_{n:02d}"
        chunk = chunk.rename(columns={bin_col: "resp", time_col: "rt"})
        rows.append(chunk)
    long = pd.concat(rows, ignore_index=True)
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long["rt"] = pd.to_numeric(long["rt"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp", "rt"] + cov]
    out = OUT / outname
    out.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(out, index=False)
    print(f"{out.name}: rows={len(long)}, items={long['item'].nunique()}, "
          f"ids={long['id'].nunique()}, resp_range=[{long['resp'].min()}, {long['resp'].max()}], "
          f"rt_range=[{long['rt'].min():.2f}, {long['rt'].max():.2f}]s")


def _build_nominal(df: pd.DataFrame, outname: str) -> None:
    cov = list(COV_RENAME.values())
    id_vars = ["id"] + cov
    item_nums = sorted(
        int(c[len("Item"):])
        for c in df.columns if re.match(r"^Item\d+$", c)
    )

    rows = []
    for n in item_nums:
        item_col = f"Item{n}"
        bin_col = f"Binary{n}"
        time_col = f"Time{n}"
        chunk = df[id_vars + [item_col, bin_col, time_col]].copy()
        chunk["item"] = f"item_{n:02d}"
        chunk = chunk.rename(columns={item_col: "text", bin_col: "resp", time_col: "rt"})
        rows.append(chunk)
    long = pd.concat(rows, ignore_index=True)
    long["text"] = pd.to_numeric(long["text"], errors="coerce")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long["rt"] = pd.to_numeric(long["rt"], errors="coerce")
    long = long.dropna(subset=["text"])
    long["text"] = long["text"].astype(int)
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "text", "resp", "rt"] + cov]
    out = OUT / outname
    out.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(out, index=False)
    print(f"{out.name}: rows={len(long)}, items={long['item'].nunique()}, "
          f"ids={long['id'].nunique()}, text_range=[{long['text'].min()}, {long['text'].max()}], "
          f"resp_range=[{long['resp'].min()}, {long['resp'].max()}], "
          f"rt_range=[{long['rt'].min():.2f}, {long['rt'].max():.2f}]s")


def main() -> None:
    df = _load()
    _build_bin(df, "blum_2018_imak_bin.csv")
    _build_nominal(df, "blum_2018_imak_nominal.csv")


if __name__ == "__main__":
    main()
