from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
OUT = BASE / "west_2022_psychnet_pclsv"
PCL_IRR_PATH = BASE / "osfstorage-archive (3)" / "Data" / "PCL_IRR.csv"


def convert_pcl_irr() -> None:
    df = pd.read_csv(PCL_IRR_PATH)
    df.insert(0, "id", range(1, len(df) + 1))

    rater1_cols = [c for c in df.columns if re.match(r"^PCLSV_\d+$", c)]
    rater2_cols = [c for c in df.columns if re.match(r"^PCLSV_\d+_OB$", c)]

    def _melt(cols: list[str], rater: int) -> pd.DataFrame:
        long = df[["id"] + cols].melt(id_vars=["id"], var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["item"] = long["item"].str.replace("_OB", "", regex=False).str.lower()
        long["rater"] = rater
        return long

    long = pd.concat([_melt(rater1_cols, 1), _melt(rater2_cols, 2)], ignore_index=True)
    long = long[["id", "item", "resp", "rater"]]

    out = OUT / "west_2022_psychnet_pclsv.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(out, index=False)
    print(
        f"{out.name}: rows={len(long)}, items={long['item'].nunique()}, "
        f"raters={sorted(long['rater'].unique())}"
    )


def main() -> None:
    convert_pcl_irr()


if __name__ == "__main__":
    main()
