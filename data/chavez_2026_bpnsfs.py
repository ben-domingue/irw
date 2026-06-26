from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
OUT = BASE / "chavez_2026_bpnsfs"
SRC = BASE / "Data NPB.xlsx"


SHEETS = [("Perú", "Peru", "PE"), ("México", "Mexico", "MX")]

ITEM_NAMES = (
    [f"autonomy_sat_{i}"   for i in range(1, 5)] +
    [f"autonomy_frust_{i}" for i in range(1, 5)] +
    [f"relatedness_sat_{i}"   for i in range(1, 5)] +
    [f"relatedness_frust_{i}" for i in range(1, 5)] +
    [f"competence_sat_{i}"   for i in range(1, 5)] +
    [f"competence_frust_{i}" for i in range(1, 5)]
)


def _load_sheet(sheet: str, country: str, id_prefix: str) -> pd.DataFrame:
    df = pd.read_excel(SRC, sheet_name=sheet)
    item_cols = [f"{n}(C2)" for n in range(1, 25)]
    out = df[["Género", "Edad"] + item_cols].copy()
    out.columns = ["cov_gender", "cov_age"] + ITEM_NAMES
    out["id"] = [f"{id_prefix}{i:03d}" for i in range(1, len(out) + 1)]
    out["cov_country"] = country
    return out


def main() -> None:
    parts = [_load_sheet(sheet, country, pfx) for sheet, country, pfx in SHEETS]
    wide = pd.concat(parts, ignore_index=True)

    long = wide.melt(
        id_vars=["id", "cov_country", "cov_gender", "cov_age"],
        value_vars=ITEM_NAMES, var_name="item", value_name="resp",
    )
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long["cov_age"] = long["cov_age"].astype(int)
    long["cov_gender"] = long["cov_gender"].astype(int)
    long = long[["id", "item", "resp", "cov_country", "cov_age", "cov_gender"]]
    long = long.sort_values(["cov_country", "id", "item"], kind="stable").reset_index(drop=True)

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "chavez_2026_bpnsfs.csv"
    long.to_csv(path, index=False)
    print(f"{path.name}: rows={len(long):,}, ids={long['id'].nunique()}, "
          f"items={long['item'].nunique()}, "
          f"resp_range=[{long['resp'].min()},{long['resp'].max()}], "
          f"countries={sorted(long['cov_country'].unique())}, "
          f"age_range=[{long['cov_age'].min()},{long['cov_age'].max()}]")


if __name__ == "__main__":
    main()
