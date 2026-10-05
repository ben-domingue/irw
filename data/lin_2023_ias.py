"""Lin et al. (2023) Chinese Interoceptive Accuracy Scale converter (OSF bx7je).

Processing notes:
  * lin_2023_phq9 has 8 items. PHQ-9 item 9 (suicidal ideation) was never
    deposited so Study 2.sav contains only PHQ9_1 to PHQ9_8.
  * lin_2023_tas has 12 items. Only the DIF and DDF subscales of the TAS-20
    are present.
  * Ids. Study 1 & 3.sav ids are sample x 10,000 + ID. Study 2.sav uses hc001 /
    cp001 ids for the same 500 people who are samples 2 and 3 of Study 1 & 3.sav.
    The deposit does not link them, so the mapping is inferred here by an exact
    match on all 20 IAS item responses plus age and sex. The script asserts the
    key is unique on both sides and that the merge is one-to-one,
    so phq9, phq15 and tas carry the same ids as lin_2023_ias.
  * lin_2023_ias and lin_2023_iats are two different scales answered by the same
    people at one administration on one id axis.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pyreadstat

BASE = Path(__file__).resolve().parent
ARCHIVE = BASE / "bx7je-osfstorage-archive" / ".sav data for SPSS"
OUT = BASE / "lin_2023_ias"

IAS_ITEMS = ["Heart", "HUNGR", "BREAT", "Thirs", "URINA", "Defec", "TASTE",
             "VOMIT", "Sneez", "COUGH", "TEMPE", "SEXAR", "WIND", "Burp",
             "MUSCL", "Bruis", "PAIN", "BloSu", "Touch", "ITCH"]
SAMPLE_LABEL = {1: "convergent_discriminant", 2: "healthy_control",
                3: "chronic_pain", 4: "retest_baseline"}


def _melt(df: pd.DataFrame, items: list[str], cov_cols: list[str]) -> pd.DataFrame:
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=items,
                   var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    standard = [c for c in ("id", "item", "resp") if c in long.columns]
    rest = [c for c in long.columns if c not in standard]
    long = long[standard + rest]
    return long.sort_values(["id", "item"], kind="stable").reset_index(drop=True)


def _write(df: pd.DataFrame, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    df.to_csv(path, index=False)
    print(f"{path.name}: rows={len(df):,}, ids={df['id'].nunique()}, "
          f"items={df['item'].nunique()}, resp=[{df['resp'].min()},{df['resp'].max()}]")


def build() -> None:
    df1, _ = pyreadstat.read_sav(str(ARCHIVE / "Study 1 & 3.sav"), apply_value_formats=False)
    df1["id"] = df1["sample"].astype(int) * 10_000 + df1["ID"].astype(int)
    df1["cov_sample"] = df1["sample"].astype(int).map(SAMPLE_LABEL)
    df1["cov_gender"] = df1["sex_dummy"].map({0: "female", 1: "male"})
    df1["cov_age"] = df1["age"]

    df2, _ = pyreadstat.read_sav(str(ARCHIVE / "Study 2.sav"), apply_value_formats=False)
    df2["cov_group"] = df2["group"].map({0: "healthy_control", 1: "chronic_pain"})
    df2["cov_gender"] = df2["Sex"].map({"女": "female", "男": "male"})
    df2["cov_age"] = df2["Age"]

    key = IAS_ITEMS + ["cov_age", "cov_gender"]
    ref = df1.loc[df1["sample"].isin([2, 3]), key + ["id"]]
    assert not ref.duplicated(key).any() and not df2.duplicated(key).any()
    df2 = df2.merge(ref, on=key, how="left", validate="one_to_one")
    assert df2["id"].notna().all() and df2["id"].nunique() == len(df2) == len(ref)
    df2["id"] = df2["id"].astype(int)

    _write(_melt(df1, IAS_ITEMS, ["cov_sample", "cov_gender", "cov_age"]), "lin_2023_ias.csv")

    at_cols = ["id", "cov_sample", "cov_gender", "cov_age"] + [f"at_{c.lower()}" for c in IAS_ITEMS]
    iats = df1.loc[df1["sample"].isin([1, 4]), at_cols].rename(
        columns={f"at_{c.lower()}": c for c in IAS_ITEMS})
    _write(_melt(iats, IAS_ITEMS, ["cov_sample", "cov_gender", "cov_age"]), "lin_2023_iats.csv")

    s1 = df1[df1["sample"] == 1]
    edi_items = [f"EDI{i}" for i in range(1, 11)]
    _write(_melt(s1, edi_items, ["cov_gender", "cov_age"]), "lin_2023_edi_ia.csv")
    bpq_items = [f"BPQ{i}" for i in range(1, 13)]
    _write(_melt(s1, bpq_items, ["cov_gender", "cov_age"]), "lin_2023_bpqa.csv")

    pain_cols = ["Painfree_days", "Average_intensity", "Pain_now", "pain_disability"]
    df2 = df2.rename(columns={c: f"cov_{c.lower()}" for c in pain_cols})
    cov2 = ["cov_group", "cov_gender", "cov_age"] + [f"cov_{c.lower()}" for c in pain_cols]

    phq9_items = [f"PHQ9_{i}" for i in range(1, 9)]
    _write(_melt(df2, phq9_items, cov2), "lin_2023_phq9.csv")

    phq15_items = [f"PHQ15_{i}" for i in range(1, 14)]
    _write(_melt(df2, phq15_items, cov2), "lin_2023_phq15.csv")

    tas_items = [f"TAS_DIF{i}" for i in range(1, 8)] + [f"TAS_DDF{i}" for i in range(1, 6)]
    tas = _melt(df2, tas_items, cov2)
    tas.insert(3, "itemcov_subscale",
               tas["item"].apply(lambda x: "DIF" if "DIF" in x else "DDF"))
    _write(tas, "lin_2023_tas.csv")


if __name__ == "__main__":
    build()
