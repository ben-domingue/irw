from __future__ import annotations

from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
SRC = (BASE / "nkbt9-osfstorage-archive" / "2.Data Source" / "Clean Data" /
       "Before reverse-coding" / "FS B-MTL 2021_clean data .csv")
OUT = BASE / "schoen_2021_bmtl"

SUBSCALES = {
    "transmissionist": [2, 4, 6, 8, 10, 12, 14, 17, 18, 19, 21],
    "factsfirst":      [1, 5, 13, 15, 20],
    "fip":             [3, 7, 9, 11, 16],
}

REVERSE = {5, 6, 10, 17, 18}


def _iname(n: int) -> str:
    return f"BMTL{n:02d}"


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(SRC)

    occ = df.groupby("PublicID").cumcount()
    df["id"] = df["PublicID"].where(occ == 0, df["PublicID"] + "_" + (occ + 1).astype(str))
    assert df["id"].is_unique

    for name, nums in SUBSCALES.items():
        cols = [_iname(n) for n in nums]
        long = df.melt(id_vars=["id"], value_vars=cols,
                       var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long["itemcov_reverse_keyed"] = long["item"].str[4:].astype(int).isin(REVERSE).astype(int)
        if long["itemcov_reverse_keyed"].nunique() == 1:
            long = long.drop(columns=["itemcov_reverse_keyed"])
        long = long.sort_values(["id", "item"], kind="stable").reset_index(drop=True)

        path = OUT / f"schoen_2021_bmtl_{name}.csv"
        long.to_csv(path, index=False)
        rev = sorted(_iname(n) for n in nums if n in REVERSE)
        print(f"{path.name}: rows={len(long):,}, ids={long['id'].nunique()}, "
              f"items={long['item'].nunique()}, resp=[{long['resp'].min()},{long['resp'].max()}], "
              f"reverse_keyed_items={rev}")


if __name__ == "__main__":
    build()
