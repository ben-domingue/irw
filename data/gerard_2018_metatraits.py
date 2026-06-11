from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyreadstat


BASE = Path(__file__).resolve().parent
OUT = BASE / "gerard_2018_metatraits"
SAV_PATH = BASE / "dataverse_files" / "525_PDA.sav"


def convert() -> None:
    df, meta = pyreadstat.read_sav(str(SAV_PATH))

    labels = meta.column_names_to_labels
    rename = {c: labels[c].strip().lower().replace(" ", "_").replace("-", "_")
              for c in df.columns if c != "id" and labels.get(c)}

    item_cols = list(rename.keys())
    long = df[["id"] + item_cols].melt(id_vars=["id"], var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["item"] = long["item"].map(rename)
    long["id"] = long["id"].astype(int)
    long = long[["id", "item", "resp"]]

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "metatraits_525pda.csv"
    long.to_csv(out, index=False)
    print(f"{out.name}: rows={len(long)}, items={long['item'].nunique()}, "
          f"ids={long['id'].nunique()}, resp_range=[{long['resp'].min():g}, {long['resp'].max():g}]")


if __name__ == "__main__":
    convert()
