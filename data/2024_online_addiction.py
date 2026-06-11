from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
OUT = BASE / "2024_online_addiction"
RAW = BASE / "rawdata_.csv"


def _norm_item(name: str) -> str:
    return name.lower()


def _melt(df, item_cols, cov_cols, outfile: Path) -> int:
    id_vars = ["id"] + cov_cols
    long = df[id_vars + item_cols].melt(
        id_vars=id_vars, var_name="item", value_name="resp"
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["item"] = long["item"].map(_norm_item)
    long = long[["id", "item", "resp"] + cov_cols]
    outfile.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(outfile, index=False)
    return len(long)


def convert() -> None:
    df = pd.read_csv(RAW)

    cov_src = ["Sex", "birthdate", "Assess_Date", "Race", "Sick", "Grade"]
    for c in cov_src:
        df[c] = df[c].astype(str).str.strip().replace({"": pd.NA, "nan": pd.NA})

    df.insert(0, "id", range(1, len(df) + 1))
    df = df.rename(columns={
        "Sex": "cov_sex",
        "birthdate": "cov_birthdate",
        "Assess_Date": "cov_assess_date",
        "Race": "cov_race",
        "Sick": "cov_sick",
        "Grade": "cov_grade",
    })
    cov_cols = ["cov_sex", "cov_birthdate", "cov_assess_date",
                "cov_race", "cov_sick", "cov_grade"]

    bsmas_cols = [c for c in df.columns if re.match(r"^bsmas\d+$", c)]
    sabas_cols = [c for c in df.columns if re.match(r"^sabas\d+$", c)]
    igds_cols  = [c for c in df.columns if re.match(r"^igds\d+$", c)]

    n = _melt(df, bsmas_cols, cov_cols, OUT / "2024_online_addiction_bsmas.csv")
    print(f"2024_online_addiction_bsmas.csv: rows={n}, items={len(bsmas_cols)}")
    n = _melt(df, sabas_cols, cov_cols, OUT / "2024_online_addiction_sabas.csv")
    print(f"2024_online_addiction_sabas.csv: rows={n}, items={len(sabas_cols)}")
    n = _melt(df, igds_cols, cov_cols, OUT / "2024_online_addiction_igds.csv")
    print(f"2024_online_addiction_igds.csv: rows={n}, items={len(igds_cols)}")


if __name__ == "__main__":
    convert()
