from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pyreadstat


BASE = Path(__file__).resolve().parent
OUT = BASE / "jovanovic_2026_conscientiousness"
DATA = BASE / "osfstorage-archive (3)"


def _norm_item(name: str) -> str:
    return name.lower()


def _load(filename: str, sample_num: int, id_offset: int) -> pd.DataFrame:
    df, _ = pyreadstat.read_sav(str(DATA / filename))
    df.insert(0, "id", range(id_offset + 1, id_offset + 1 + len(df)))
    df["cov_sample"] = sample_num
    return df.rename(columns={"Gender": "cov_gender", "Age": "cov_age"})


def _melt_long(df: pd.DataFrame, item_cols: list[str], cov_cols: list[str]) -> pd.DataFrame:
    id_vars = ["id"] + cov_cols
    long = df[id_vars + item_cols].melt(
        id_vars=id_vars, var_name="item", value_name="resp"
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long[long["resp"] == long["resp"].round()]
    long["resp"] = long["resp"].astype(int)
    long["item"] = long["item"].map(_norm_item)
    return long[["id", "item", "resp"] + cov_cols]


def _write(long: pd.DataFrame, name: str) -> None:
    out = OUT / name
    out.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(out, index=False)
    print(f"{out.name}: rows={len(long)}, items={long['item'].nunique()}, "
          f"samples={sorted(long['cov_sample'].unique())}")


def main() -> None:
    s1 = _load("1. SAMPLE 1 Data.sav", 1, 0)
    s2 = _load("2. SAMPLE 2 Data.sav", 2, len(s1))
    s3 = _load("3. SAMPLE 3 Data.sav", 3, len(s1) + len(s2))

    cov = ["cov_gender", "cov_age", "cov_sample"]

    bfi1 = _melt_long(s1, [c for c in s1.columns if re.match(r"^BFI_Consc\d+$", c)], cov)
    bfi2 = _melt_long(s2, [c for c in s2.columns if re.match(r"^BFI_Consc\d+$", c)], cov)
    bfi3 = _melt_long(s3, [c for c in s3.columns if re.match(r"^BFI2_Consc\d+$", c)], cov)
    _write(pd.concat([bfi1, bfi2, bfi3], ignore_index=True),
           "jovanovic_2026_conscientiousness_bfi.csv")

    panas = _melt_long(s1, [c for c in s1.columns if re.match(r"^panas_na\d+$", c)], cov)
    _write(panas, "jovanovic_2026_conscientiousness_panas_na.csv")

    spane2 = _melt_long(s2, [c for c in s2.columns if re.match(r"^SPANE_NA\d+$", c)], cov)
    spane3 = _melt_long(s3, [c for c in s3.columns if re.match(r"^SPANE_NA\d+$", c)], cov)
    _write(pd.concat([spane2, spane3], ignore_index=True),
           "jovanovic_2026_conscientiousness_spane_na.csv")

    dass1 = _melt_long(s1, [c for c in s1.columns if re.match(r"^DASS_D\d+$", c)], cov)
    dass2 = _melt_long(s2, [c for c in s2.columns if re.match(r"^DASS_D\d+$", c)], cov)
    _write(pd.concat([dass1, dass2], ignore_index=True),
           "jovanovic_2026_conscientiousness_dass_d.csv")

    yips = _melt_long(s3, [c for c in s3.columns if re.match(r"^YIPS\d+$", c)], cov)
    _write(yips, "jovanovic_2026_conscientiousness_yips.csv")

if __name__ == "__main__":
    main()
