"""Lee et al. (2020), PLOS ONE -- burnout and wellbeing in Hong Kong medical students.

Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0235154
DOI: 10.1371/journal.pone.0235154
Data: S1 Appendix (journal.pone.0235154.s001, SPSS .sav)
License: CC BY 4.0

A cross-sectional survey of Chinese University of Hong Kong medical students run
September-December 2017 (1,341 invited, 746 rows in the deposit; the paper
analyses 731 after its own screening, which the deposit does not mark, so all
rows are kept here). The .sav carries SPSS variable labels holding the full item
stem for every question and value labels for every response category, so the
instrument structure is read off the file itself rather than inferred.

Tables written
--------------
lee_2020_burnout         22 Maslach Burnout Inventory items,          0-6
lee_2020_empathy         20 Jefferson Scale of Physician Empathy,     1-7
lee_2020_social_support  10 Duke Social Support and Stress items,     1-3
lee_2020_sleep_quality   14 Pittsburgh Sleep Quality Index items,     0-3
lee_2020_alcohol_use      3 AUDIT-C items,                            0-4 / 0-5 / 0-4

Only the MBI, AUDIT-C, PSQI and a physical-activity score are reported in the
paper; the JPSE and DUSOCS blocks were administered but not analysed there.
Their item stems and response categories are taken from the file's own labels,
which reproduce the published instruments verbatim.

Notes on the source coding
--------------------------
* MBI: `MBI_EE`/`MBI_DP`/`MBI_PA` in the file equal the plain sum of the raw
  items in each subscale, confirming `MBI_1`..`MBI_22` are untransformed
  responses on the 0-6 "Never".."Every day" frequency scale.
* JPSE: `JPSE_sum_total` likewise equals the plain sum of the stored items.
  A valid JSPE total requires items 11-20 to be reverse-scored first, so the
  stored per-item values for those items are already reversed (higher = more
  empathic). They are exported as stored -- consistently coded within each
  item -- and not transformed further here.
* DUSOCS: category 4 is "There is no such person", a not-applicable sentinel
  rather than a fourth ordinal step, so it is set to NA. The exported scale is
  1 (None) - 3 (A lot).
* PSQI: only the 0-3 frequency/severity items are exported (5A-5J, 6-9). Items
  1-4 are clock times and durations recorded as free text plus a `_remarks`
  column, and 5-9 also exist as derived `component*` scores; neither is an
  ordinal item response. `PSQI_5J_plus` is the zero-filled variant of
  `PSQI_5J` used for the authors' `component5_plus`; the raw `PSQI_5J` is used
  instead so no imputed values enter the table.
* AUDIT-C: exported at the source's own per-item category counts (Q2 has six
  categories, Q1 and Q3 five), not the collapsed 0-4 AUDIT scoring in
  `drinking_habit_2_transform`.
* All derived/aggregate columns (subscale sums, ranks, cut-point indicators,
  PSQI components, GSLTPAQ score, pack-years) are excluded.
* The free-text columns (`*_remarks`, `DUSOCS_11_yes*`, `PSQI_5J_reason`,
  `Place_of_living_Others`) contain no personal identifiers, but hold no item
  responses either and are not exported.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

DOI = "10.1371/journal.pone.0235154"
SRC = ("https://journals.plos.org/plosone/article/file"
       "?id=10.1371/journal.pone.0235154.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

N_ROWS = 746

# (out_name, source columns, valid response range, sentinel codes -> NA)
SCALES = [
    ("lee_2020_burnout",
     [f"MBI_{i}" for i in range(1, 23)], (0, 6), ()),
    ("lee_2020_empathy",
     [f"JPSE_{i}" for i in range(1, 21)], (1, 7), ()),
    ("lee_2020_social_support",
     [f"DUSOCS_{i}" for i in range(1, 11)], (1, 3), (4,)),
    ("lee_2020_sleep_quality",
     [f"PSQI_5{c}" for c in "ABCDEFGHIJ"] + ["PSQI_6", "PSQI_7", "PSQI_8",
                                              "PSQI_9"], (0, 3), ()),
    ("lee_2020_alcohol_use",
     [f"Drinking_habit_{i}" for i in range(1, 4)], (0, 5), ()),
]

# source column -> IRW covariate name. Coded categoricals are exported as their
# SPSS value labels; age and study year stay numeric.
COVARIATES = {
    "Age": "cov_age",
    "Gender": "cov_gender",
    "Study_year": "cov_study_year",
    "clinical_year": "cov_clinical_stage",
    "MBChB_first_degree": "cov_first_degree",
    "Place_of_living": "cov_place_of_living",
    "Marital_status": "cov_marital_status",
    "Scholarship": "cov_scholarship",
    "Smoke": "cov_smoke",
}
NUMERIC_COVARIATES = {"cov_age", "cov_study_year"}


def fetch() -> tuple[pd.DataFrame, object]:
    r = requests.get(SRC, headers=UA, timeout=300)
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as fh:
        fh.write(r.content)
        fh.flush()
        return pyreadstat.read_sav(fh.name)


def build_frame(raw: pd.DataFrame, meta) -> pd.DataFrame:
    if len(raw) != N_ROWS:
        raise ValueError(f"expected {N_ROWS} source rows, got {len(raw)}")

    ids = raw["Subject_ID"].astype(str).str.extract(r"^BO2017-(\d{4})$")[0]
    if ids.isna().any() or ids.nunique() != len(raw):
        raise ValueError("Subject_ID is not a complete set of unique BO2017 codes")
    df = pd.DataFrame({"id": ids.astype(int)})

    labels = meta.variable_value_labels
    for src, name in COVARIATES.items():
        col = pd.to_numeric(raw[src], errors="coerce")
        if name in NUMERIC_COVARIATES:
            df[name] = col
        else:
            if src not in labels:
                raise ValueError(f"{src} has no SPSS value labels to map")
            df[name] = col.map(labels[src])

    for _, items, _, _ in SCALES:
        for c in items:
            df[c] = pd.to_numeric(raw[c], errors="coerce")
    return df


def make_scale(df: pd.DataFrame, items: list[str], bounds: tuple[int, int],
               sentinels: tuple[int, ...]) -> pd.DataFrame:
    cov_cols = list(COVARIATES.values())
    long = df[["id"] + cov_cols + items].melt(
        id_vars=["id"] + cov_cols,
        value_vars=items,
        var_name="item",
        value_name="resp",
    )
    if sentinels:
        long.loc[long["resp"].isin(sentinels), "resp"] = pd.NA
    long = long.dropna(subset=["resp"])

    lo, hi = bounds
    out_of_range = ~long["resp"].between(lo, hi)
    if out_of_range.any():
        bad = long.loc[out_of_range, ["item", "resp"]].drop_duplicates()
        raise ValueError(f"responses outside {lo}-{hi}:\n{bad}")
    long["resp"] = long["resp"].astype(int)

    order = ["id", "item", "resp"] + cov_cols
    return (long[order]
            .sort_values(["id", "item"])
            .reset_index(drop=True))


def convert() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw, meta = fetch()
    df = build_frame(raw, meta)
    for name, items, bounds, sentinels in SCALES:
        long = make_scale(df, items, bounds, sentinels)
        long.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
