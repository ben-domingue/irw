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


def _melt_with_rt(df: pd.DataFrame, score_prefix: str, outname: str) -> None:
    """Melt the polytomous (Item<N>) or dichotomous (Binary<N>) columns and
    pair each response with its matching Time<N> reaction time."""
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
        chunk = chunk.rename(columns={c: "resp", time_col: "rt"})
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


def main() -> None:
    df = _load()
    _melt_with_rt(df, "Binary", "blum_2018_imak_bin.csv")
    _melt_with_rt(df, "Item",   "blum_2018_imak_items.csv")


if __name__ == "__main__":
    main()
