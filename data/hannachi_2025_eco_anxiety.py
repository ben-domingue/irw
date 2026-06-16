from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


BASE = Path(__file__).resolve().parent
OUT = BASE / "hannachi_2025_eco_anxiety"
SRC = BASE / "osfstorage-archive (3)" / "Data set.csv"


AFFECT_ITEMS = [
    "heureux.se", "nerveux.se", "ennuye.e", "satisfait.e", "gai",
    "stresse.e", "fatigue.e", "stimule.e", "contrarie.e", "calme",
    "en alerte", "triste", "detendu", "tendu", "deprime.e",
    "serein.e", "inquiet.e", "indifferent.e", "en colere", "anxieuxs.e",
    "optimiste", "terrifie.e", "impuissant.e", "Honteux.se", "coupable",
    "frustre.e",
]

SHARED_CAS_HEAS = {
    "CAS2/HEAS8":   ("cas2",  "heas8"),
    "CAS9/HEAS9":   ("cas9",  "heas9"),
    "CAS11/HEAS10": ("cas11", "heas10"),
}


def _sanitize(name: str) -> str:
    return (name.lower()
                .replace(" ", "_")
                .replace(".", "_"))


def _load() -> pd.DataFrame:
    df = pd.read_csv(SRC, sep=";", encoding="latin-1")
    df = df.rename(columns={
        "ID ":         "id",
        "Age":         "cov_age",
        "Genre":       "cov_gender",
        "Etude":       "cov_education",
        "domaine":     "cov_field",
        "Temps total": "cov_total_time",
    })
    df["cov_total_time"] = pd.to_numeric(
        df["cov_total_time"].str.replace(",", ".", regex=False),
        errors="coerce",
    )
    return df


def _melt_scale(df: pd.DataFrame, item_cols: list[str],
                rename_map: dict[str, str], outname: str) -> None:
    cov = ["cov_age", "cov_gender", "cov_education", "cov_field", "cov_total_time"]
    long = df[["id"] + cov + item_cols].melt(
        id_vars=["id"] + cov, var_name="item", value_name="resp"
    )
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long["item"] = long["item"].map(rename_map)
    long = long[["id", "item", "resp"] + cov]
    out = OUT / outname
    out.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(out, index=False)
    print(f"{out.name}: rows={len(long)}, items={long['item'].nunique()}, "
          f"ids={long['id'].nunique()}, resp_range=[{long['resp'].min()}, {long['resp'].max()}]")


def main() -> None:
    df = _load()

    _melt_scale(df, AFFECT_ITEMS,
                {src: _sanitize(src) for src in AFFECT_ITEMS},
                "hannachi_2025_eco_anxiety_affect.csv")

    cop_cols = [c for c in df.columns if re.match(r"^COP\d+$", c)]
    _melt_scale(df, cop_cols,
                {c: c.lower() for c in cop_cols},
                "hannachi_2025_eco_anxiety_cope.csv")

    cas_solo = [c for c in df.columns if re.match(r"^CAS\d+$", c)]
    heas_solo = [c for c in df.columns if re.match(r"^HEAS\d+$", c)]
    shared = list(SHARED_CAS_HEAS.keys())

    cas_rename = {**{c: c.lower() for c in cas_solo},
                  **{src: cas for src, (cas, _) in SHARED_CAS_HEAS.items()}}
    heas_rename = {**{c: c.lower() for c in heas_solo},
                   **{src: heas for src, (_, heas) in SHARED_CAS_HEAS.items()}}

    _melt_scale(df, cas_solo + shared, cas_rename,
                "hannachi_2025_eco_anxiety_cas.csv")
    _melt_scale(df, heas_solo + shared, heas_rename,
                "hannachi_2025_eco_anxiety_heas.csv")


if __name__ == "__main__":
    main()
