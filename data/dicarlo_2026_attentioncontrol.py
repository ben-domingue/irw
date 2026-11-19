from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
OUT = BASE / "dicarlo_2026_attentioncontrol"
DATA = BASE / "osfstorage-archive"

SCALES = [
    ("arces",  r"^ARCES_Items_\d+$"),
    ("acs",    r"^AC\.S_Items_\d+$"),
    ("acd",    r"^AC\.D_Items_\d+$"),
    ("maaslo", r"^MAASLO_Items_\d+$"),
]


def _norm_item(name: str) -> str:
    return name.lower().replace(".", "_")


def _to_unix(series: pd.Series) -> pd.Series:
    ts = pd.to_datetime(series, format="%m/%d/%y %H:%M", errors="coerce", utc=True)
    secs = (ts - pd.Timestamp("1970-01-01", tz="UTC")).dt.total_seconds()
    return secs.astype("Int64")


def _load_study1() -> pd.DataFrame:
    df = pd.read_csv(DATA / "attcon_study1_n209s.csv")
    df = df.drop(columns=["PID"])
    df = df.rename(columns={
        "Date": "date",
        "Dem_age": "cov_age",
        "Dem_gender": "cov_gender",
        "Dem_race.ethnicity": "cov_race",
        "Dem_gpa": "cov_gpa",
    })
    df["date"] = _to_unix(df["date"])
    df["cov_study"] = "study1"
    df["cov_education"] = pd.NA
    return df


def _load_study2() -> pd.DataFrame:
    df = pd.read_csv(DATA / "attcon_study2_n149s.csv")
    df = df.rename(columns={
        "PID": "id",
        "Date": "date",
        "dem_age": "cov_age",
        "dem_gender": "cov_gender",
        "dem_race": "cov_race",
        "dem_education": "cov_education",
        "dem_gpa": "cov_gpa",
    })
    df["date"] = _to_unix(df["date"])
    df["cov_study"] = "study2"
    return df


def _emit(df: pd.DataFrame) -> None:
    cov_cols = ["cov_study", "cov_age", "cov_gender", "cov_race", "cov_education", "cov_gpa"]
    for scale, pattern in SCALES:
        item_cols = [c for c in df.columns if re.match(pattern, c)]
        id_vars = ["id", "date"] + cov_cols
        long = df[id_vars + item_cols].melt(
            id_vars=id_vars, var_name="item", value_name="resp"
        )
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"])
        long["item"] = long["item"].map(_norm_item)
        long = long[["id", "item", "resp", "date"] + cov_cols]
        long = long.sort_values(["cov_study", "id", "item"], kind="stable").reset_index(drop=True)
        out = OUT / f"dicarlo_2026_attentioncontrol_{scale}.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        long.to_csv(out, index=False)
        print(f"{out.name}: rows={len(long):,}, ids={long['id'].nunique()}, "
              f"items={long['item'].nunique()}, "
              f"resp_range=[{long['resp'].min()},{long['resp'].max()}], "
              f"studies={sorted(long['cov_study'].unique())}")


def main() -> None:
    s1 = _load_study1()
    s2 = _load_study2()
    common = list(dict.fromkeys(list(s1.columns) + list(s2.columns)))
    for c in common:
        if c not in s1.columns:
            s1[c] = pd.NA
        if c not in s2.columns:
            s2[c] = pd.NA
    combined = pd.concat([s1[common], s2[common]], ignore_index=True)
    _emit(combined)


if __name__ == "__main__":
    main()
