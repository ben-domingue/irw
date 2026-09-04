from __future__ import annotations

from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
ARCHIVE = BASE / "osfstorage-archive (4)" / "Data"
OUT = BASE / "christensen_2018_wsssf"


SUBSCALES = {
    "mi": "Magical Ideation",
    "py": "Physical Anhedonia",
    "pb": "Perceptual Aberration",
    "sa": "Social Anhedonia",
}

ITEM_ORDER = (
    [f"mi{i:02d}" for i in range(1, 16)] +
    [f"py{i:02d}" for i in range(1, 16)] +
    [f"pb{i:02d}" for i in range(1, 16)] +
    [f"sa{i:02d}" for i in range(1, 16)]
)


def _melt_items(wide: pd.DataFrame, id_vars: list[str]) -> pd.DataFrame:
    long = wide.melt(id_vars=id_vars, value_vars=ITEM_ORDER,
                     var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long["cov_subscale"] = long["item"].str[:2].map(SUBSCALES)
    return long


def build_5831() -> None:
    df = pd.read_csv(ARCHIVE / "WSS-SF_5831.csv")
    df["id"] = [f"s5831_{i:04d}" for i in range(1, len(df) + 1)]
    long = _melt_items(df, ["id"])
    long = long[["id", "item", "resp", "cov_subscale"]]
    long = long.sort_values(["id", "item"], kind="stable").reset_index(drop=True)
    path = OUT / "christensen_2018_wsssf_5831.csv"
    long.to_csv(path, index=False)
    print(f"{path.name}: rows={len(long):,}, ids={long['id'].nunique()}, "
          f"items={long['item'].nunique()}, resp_range=[{long['resp'].min()},{long['resp'].max()}]")


def build_2171() -> None:
    items = pd.read_csv(ARCHIVE / "WSS-SF_2171.csv")
    demo = pd.read_csv(ARCHIVE / "share_2171n_WSS-SF.csv",
                       na_values=[" ", ""])[["subjnumb", "sex", "ethnic"]]
    if len(items) != len(demo):
        raise RuntimeError(f"row mismatch: items={len(items)} demo={len(demo)}")
    wide = pd.concat([demo.reset_index(drop=True), items.reset_index(drop=True)], axis=1)
    wide = wide.rename(columns={"subjnumb": "id", "sex": "cov_sex", "ethnic": "cov_ethnic"})
    long = _melt_items(wide, ["id", "cov_sex", "cov_ethnic"])
    long = long[["id", "item", "resp", "cov_subscale", "cov_sex", "cov_ethnic"]]
    long = long.sort_values(["id", "item"], kind="stable").reset_index(drop=True)
    path = OUT / "christensen_2018_wsssf_2171.csv"
    long.to_csv(path, index=False)
    print(f"{path.name}: rows={len(long):,}, ids={long['id'].nunique()}, "
          f"items={long['item'].nunique()}, resp_range=[{long['resp'].min()},{long['resp'].max()}], "
          f"sex={sorted(long['cov_sex'].dropna().unique())}, "
          f"ethnic={sorted(long['cov_ethnic'].dropna().unique())}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    build_5831()
    build_2171()


if __name__ == "__main__":
    main()
