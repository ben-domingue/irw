import os
import re
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "kudryk_et_al_2024_social_anxiety")

COMMUNITY_CSV = "CommunitySample_FinalData_20imputations.csv"
UNDERGRAD_FILES = [
    ("Fall2018_20imputations.csv", "Fall2018", 2018),
    ("Winter2019_20imputations.csv", "Winter2019", 2019),
    ("Fall2019_20imputations.csv", "Fall2019", 2019),
    ("Fall2022_20imputations.csv", "Fall2022", 2022),
    ("Winter2022_20imputations.csv", "Winter2022", 2022),
    ("Fall2023_20imputations.csv", "Fall2023", 2023),
    ("Winter2023_20imputations.csv", "Winter2023", 2023),
]

COV_CANDIDATES = [
    "gender",
    "age",
    "sex",
    "ethnicity",
    "race",
    "race_primary",
    "race_identify",
    "ethnic_identify",
    "education",
    "univ_year",
    "sad",
    "group",
]

DERIVED_FLAG = {"spin_28", "spin_30", "spin_34", "spin_39", "sds_7", "sds_11"}

GROUP_LABELS = {1: "sad", 2: "clinical", 3: "nonclinical"}

Q_TO_SDS = {"q21": "sds_1", "q23": "sds_2", "q24": "sds_3"}


def _norm(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=lambda c: str(c).lower().replace(" ", "_").replace(".", "_"))


def _harmonize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    for c in df.columns:
        m = re.fullmatch(r"spin_1_(\d+)", c)
        if m and 1 <= int(m.group(1)) <= 17:
            rename[c] = f"spin_{m.group(1)}"
            continue
        m = re.fullmatch(r"sdiss_(\d+)", c)
        if m and 1 <= int(m.group(1)) <= 3:
            rename[c] = f"sds_{m.group(1)}"
            continue
        if c in Q_TO_SDS and Q_TO_SDS[c] not in df.columns:
            rename[c] = Q_TO_SDS[c]
    return df.rename(columns=rename) if rename else df


def _is_raw_spin(name: str) -> bool:
    n = name.lower()
    if n in DERIVED_FLAG:
        return False
    m = re.fullmatch(r"spin_(\d+)", n)
    return bool(m) and 1 <= int(m.group(1)) <= 17


def _is_raw_sds(name: str) -> bool:
    n = name.lower()
    if n in DERIVED_FLAG:
        return False
    m = re.fullmatch(r"sds_(\d+)", n)
    return bool(m) and 1 <= int(m.group(1)) <= 17


def _build_long(
    df: pd.DataFrame,
    id_col: str,
    item_cols: list[str],
    cov_cols: list[str],
    extra_cov: dict | None = None,
) -> pd.DataFrame:
    long = df.melt(
        id_vars=[id_col] + cov_cols,
        value_vars=item_cols,
        var_name="item",
        value_name="resp",
    )
    long = long.rename(columns={id_col: "id"})
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long = long.rename(columns={c: "cov_" + c for c in cov_cols})
    if extra_cov:
        for k, v in extra_cov.items():
            long[k] = v
    covs = sorted([c for c in long.columns if c.startswith("cov_")])
    return long[["id", "item", "resp"] + covs]


def _split_save(df: pd.DataFrame, prefix: str) -> None:
    spin_items = sorted({i for i in df["item"].unique() if _is_raw_spin(i)})
    sds_items = sorted({i for i in df["item"].unique() if _is_raw_sds(i)})

    if spin_items:
        spin = df[df["item"].isin(spin_items)].reset_index(drop=True)
        out = os.path.join(OUT_DIR, f"{prefix}_spin.csv")
        spin.to_csv(out, index=False)
        print(
            f"  {os.path.basename(out)}: rows={len(spin)} items={spin['item'].nunique()} "
            f"ids={spin['id'].nunique()} resp_range=({spin['resp'].min()}, {spin['resp'].max()})"
        )
    if sds_items:
        sds = df[df["item"].isin(sds_items)].reset_index(drop=True)
        out = os.path.join(OUT_DIR, f"{prefix}_sds.csv")
        sds.to_csv(out, index=False)
        print(
            f"  {os.path.basename(out)}: rows={len(sds)} items={sds['item'].nunique()} "
            f"ids={sds['id'].nunique()} resp_range=({sds['resp'].min()}, {sds['resp'].max()})"
        )


def _convert_one(path: str, term: str | None, term_year: int | None = None) -> pd.DataFrame | None:
    if not os.path.isfile(path):
        print(f"  missing: {path}")
        return None
    df = _norm(pd.read_csv(path, low_memory=False))
    if "imputation_" in df.columns:
        df = df[df["imputation_"] == 0].copy()
    df = _harmonize_columns(df)

    if "group" in df.columns:
        df["group"] = df["group"].map(GROUP_LABELS).fillna(df["group"])

    if term_year is not None and "birth_year" in df.columns:
        derived_age = term_year - pd.to_numeric(df["birth_year"], errors="coerce")
        if "age" in df.columns:
            df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(derived_age)
        else:
            df["age"] = derived_age

    item_cols = [c for c in df.columns if _is_raw_spin(c) or _is_raw_sds(c)]
    if not item_cols:
        return None
    id_col = "id" if "id" in df.columns else (
        "id_code" if "id_code" in df.columns else None
    )
    if id_col is None:
        df["id"] = range(1, len(df) + 1)
        id_col = "id"
    cov_cols = [c for c in COV_CANDIDATES if c in df.columns]
    extra = {"cov_term": term} if term else None
    return _build_long(df, id_col, item_cols, cov_cols, extra)


def convert_community() -> None:
    long = _convert_one(os.path.join(BASE_DIR, COMMUNITY_CSV), term=None)
    if long is None:
        return
    _split_save(long, "kudryk_et_al_2024_social_anxiety_community")


def convert_undergrad() -> None:
    parts = []
    for csv_name, term, term_year in UNDERGRAD_FILES:
        long = _convert_one(
            os.path.join(BASE_DIR, csv_name), term=term, term_year=term_year
        )
        if long is None or long.empty:
            continue
        parts.append(long)
    if not parts:
        return
    combined = pd.concat(parts, ignore_index=True)
    _split_save(combined, "kudryk_et_al_2024_social_anxiety_undergrad")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Community:")
    convert_community()
    print("Undergrad:")
    convert_undergrad()
