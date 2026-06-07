from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
OUT = BASE / "west_2021_aggnet"
BFI_PATH = BASE / "osfstorage-archive" / "Data + Code" / "Raw Data" / "BFIItemsN.csv"


def _strip_reverse_suffix(name: str) -> str:
    return re.sub(r"r$", "", name)


def _norm_item(name: str) -> str:
    n = name.lower().replace(".", "_")
    return _strip_reverse_suffix(n)


def _melt(df: pd.DataFrame, item_cols: list[str], outfile: Path) -> int:
    id_col = "id"
    long = df[[id_col] + item_cols].melt(id_vars=[id_col], var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["item"] = long["item"].map(_norm_item)
    long = long[["id", "item", "resp"]]
    outfile.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(outfile, index=False)
    return len(long)


def convert_bfi_items() -> None:
    df = pd.read_csv(BFI_PATH)
    df.insert(0, "id", range(1, len(df) + 1))

    bpaq_drop = {"BPAQ.1", "BPAQ.4"}
    bpaq_cols = [c for c in df.columns if c.startswith("BPAQ.") and c not in bpaq_drop]
    n = _melt(df, bpaq_cols, OUT / "west_2021_aggnet_bpaq.csv")
    print(f"west_2021_aggnet_bpaq.csv: rows={n}, items={len(bpaq_cols)}")

    bfi2_cols = [c for c in df.columns if c.startswith("aBF") or c.startswith("nBF")]
    n = _melt(df, bfi2_cols, OUT / "west_2021_aggnet_bfi2_agg_neu.csv")
    print(f"west_2021_aggnet_bfi2_agg_neu.csv: rows={n}, items={len(bfi2_cols)}")


def main() -> None:
    convert_bfi_items()


if __name__ == "__main__":
    main()
