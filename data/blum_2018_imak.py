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


def _melt_with_rt(df: pd.DataFrame, score_prefix: str, outname: str, resp_col: str = "resp") -> None:
    score_cols = sorted(
        [c for c in df.columns if re.match(rf"^{score_prefix}\d+$", c)],
        key=lambda c: int(c[len(score_prefix):]),
    )
    cov = list(COV_RENAME.values())
    id_vars = ["id"] + cov

    rows = []
    for c in score_cols:
        n = int(c[len(score_prefix):])
        time_col = f"Time{n}"
        chunk = df[id_vars + [c, time_col]].copy()
        chunk["item"] = f"item_{n:02d}"
        chunk = chunk.rename(columns={c: resp_col, time_col: "rt"})
        rows.append(chunk)
    long = pd.concat(rows, ignore_index=True)
    long[resp_col] = pd.to_numeric(long[resp_col], errors="coerce")
    long["rt"] = pd.to_numeric(long["rt"], errors="coerce")
    long = long.dropna(subset=[resp_col])
    long[resp_col] = long[resp_col].astype(int)
    long = long[["id", "item", resp_col, "rt"] + cov]
    out = OUT / outname
    out.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(out, index=False)
    print(f"{out.name}: rows={len(long)}, items={long['item'].nunique()}, "
          f"ids={long['id'].nunique()}, {resp_col}_range=[{long[resp_col].min()}, {long[resp_col].max()}], "
          f"rt_range=[{long['rt'].min():.2f}, {long['rt'].max():.2f}]s")


def main() -> None:
    df = _load()
    _melt_with_rt(df, "Binary", "blum_2018_imak_bin.csv", resp_col="resp")
    _melt_with_rt(df, "Item",   "blum_2018_imak_items.csv", resp_col="text")


if __name__ == "__main__":
    main()
