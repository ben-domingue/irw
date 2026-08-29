"""Differentiation of Self in adolescents across six Spanish-speaking countries.

Source: Osorio, A. (2023), Zenodo 10.5281/zenodo.8300667, CC BY 4.0 --
dataset for "Differentiation of Self in Adolescents: Measurement Invariance
Analysis across six Spanish-Speaking Countries". 5,552 adolescents aged 12-19
in Spain, Chile, Argentina, Peru, Ecuador and Mexico.

One instrument, one table: 21 Differentiation of Self items (`vpa_dos01`..
`vpa_dos21`), every one on the same 0 ("Nada cierto") to 5 ("Totalmente
cierto") scale. The uniform scale is asserted rather than assumed, because
the .dta also encodes a string "No quiero contestar" category on each item;
pyreadstat maps it to NaN when value formats are off, and any survivor would
show up as an out-of-range level.

`pais` is stored against a 240-entry ISO country list, so the six observed
codes are mapped by that list rather than by position -- reading them as
1..6 would silently mislabel every country.
"""
import os

import pandas as pd
import pyreadstat
import requests

RECORD = 8300667
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "osorio_2023_dos"

N_ITEMS = 21
SCALE = {0.0, 1.0, 2.0, 3.0, 4.0, 5.0}
COVARIATES = {
    "pais": "cov_country",
    "titularidad": "cov_school_type",
    "vpa_edad": "cov_age",
    "vpa_sexo": "cov_sex",
    "vpa_religion": "cov_religion",
}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(".dta"))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df, meta = pyreadstat.read_dta(fetch_raw(path), apply_value_formats=False)

    items = sorted(c for c in df.columns if c.startswith("vpa_dos"))
    assert len(items) == N_ITEMS, f"expected {N_ITEMS} DOS items, got {len(items)}"

    observed = set(pd.unique(df[items].values.ravel()))
    observed = {v for v in observed if pd.notna(v)}
    assert observed <= SCALE, f"off-scale DOS response(s): {sorted(observed - SCALE)}"

    # Country codes index a 240-entry ISO list; map through the file's own
    # value labels so the six observed codes cannot be mis-assigned.
    labels = meta.variable_value_labels
    country = {k: v for k, v in labels.get("pais", {}).items()}
    school = {k: v for k, v in labels.get("titularidad", {}).items()}
    religion = {k: v for k, v in labels.get("vpa_religion", {}).items()}
    sex = {k: v for k, v in labels.get("vpa_sexo", {}).items()}

    d = df.rename(columns=COVARIATES)
    d["cov_country"] = d["cov_country"].map(country)
    d["cov_school_type"] = d["cov_school_type"].map(school)
    d["cov_religion"] = d["cov_religion"].map(religion)
    d["cov_sex"] = d["cov_sex"].map(sex)
    assert d["cov_country"].notna().all(), "unmapped country code"

    long = d.melt(id_vars=["id"] + list(COVARIATES.values()),
                  value_vars=items, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long["item"] = long["item"].str.replace("vpa_", "", regex=False)

    out = long[["id", "item", "resp"] + list(COVARIATES.values())]
    os.makedirs(OUT_DIR, exist_ok=True)
    out.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(out):,} responses | "
          f"{out['id'].nunique():,} ids | {out['item'].nunique()} items")


if __name__ == "__main__":
    main()
