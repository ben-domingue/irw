"""
Four instruments administered in Persian to 714 Iranian online shoppers:
internet addiction, online impulse buying, mindfulness and emotional
intelligence.

Source: Aghaei, A. E., Tehranizadeh, M., & Aminzadeh, M. (2025). Unpacking the
        Mechanisms Between Internet Addiction and Online Impulse Buying: Which
        is More Critical, Mindfulness or Emotional Intelligence? [Dataset].
        Zenodo.
DOI: 10.5281/zenodo.15346545
Data: https://zenodo.org/records/15346545 ("CHB Z.sav")
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id
        "cc-by-4.0")
Item text: IN HAND but NOT SHIPPED -- a rights question, not an availability
        gap, and a later pass must not re-derive it. Every item column's SPSS
        variable label IS its full Persian stem, numbered with the position it
        held in the 84-item questionnaire (OIB 20-24, EI 37-52, mindfulness
        53-64, addiction 65-84). The value-label level is EMPTY for every
        variable, so the Persian response anchors are NOT in the deposit --
        meaning even a cleared extraction would ship stems with no option text.
        Both levels were checked. The four instruments are identified below;
        all four are published scales and the administration was Persian, so
        the 2026-09-08 translated-adaptation ruling governs, and none of the
        four has a row in itemtext/instrument_rights_register.csv.

The four instruments, identified from the stems rather than from the deposit's
column prefixes:

  * `adi1`..`adi20` -- Young's Internet Addiction Test (IAT), 20 items, 1-5.
    `adi1` is "how often do you stay online longer than you intended?", which
    is the IAT's own first item.
  * `EI1`..`EI16` -- a 16-item emotional intelligence scale whose four blocks
    of four are self-emotion appraisal, others' emotion appraisal, use of
    emotion and regulation of emotion, i.e. the shape of Wong & Law's WLEIS.
    1-5.
  * `m1`..`m12` -- a 12-item mindfulness scale on 1-4, matching the Cognitive
    and Affective Mindfulness Scale-Revised (CAMS-R) in both length and
    response format.
  * `OIB1`..`OIB5` -- five online impulse-buying items, 1-5.

Neither the WLEIS nor the CAMS-R identification was confirmed by a verbatim
search (the stems are Persian, so a verbatim search needs the translation, not
the original); they are recorded as leads for the register work, not as
findings.

PII: none. The screen below prints its denominator. The six string-typed columns
are the demographic questions and the screening question, all closed
categories; there is no name, email, date, identifier or geographic column, and
no free-text column at all.

Output: four tables, 38,556 responses.
  * aghaei_2025_internet_addiction  -- 20 items, resp 1-5
  * aghaei_2025_emotional_intelligence -- 16 items, resp 1-5
  * aghaei_2025_mindfulness         -- 12 items, resp 1-4
  * aghaei_2025_impulse_buying      --  5 items, resp 1-5
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("CHB Z.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

BLOCKS = {
    "aghaei_2025_internet_addiction": ([f"adi{i}" for i in range(1, 21)],
                                       [1, 2, 3, 4, 5]),
    "aghaei_2025_emotional_intelligence": ([f"EI{i}" for i in range(1, 17)],
                                           [1, 2, 3, 4, 5]),
    "aghaei_2025_mindfulness": ([f"m{i}" for i in range(1, 13)], [1, 2, 3, 4]),
    "aghaei_2025_impulse_buying": ([f"OIB{i}" for i in range(1, 6)],
                                   [1, 2, 3, 4, 5]),
}

# The screening question's column name is the question itself with the spaces
# stripped, so it is resolved by position among the string columns rather than
# typed out here.
SCREEN_LABEL_FRAGMENT = "اینترنت"

COV_MAP = {
    "GENDER": "cov_gender",
    "E_LEVEL": "cov_education",
    "Marital_Status": "cov_marital_status",
    "age": "cov_age_band",
    "income": "cov_income_band",
}

DROP = {
    "TEI": "depositor-computed emotional-intelligence total",
    "TM": "depositor-computed mindfulness total",
    "TROE": "depositor-computed subscale total",
    "ZTM": "a z-score of TM (its variable label says 'Zscore(TM)')",
    "ZTEI": "a z-score of TEI",
    "ZTROE": "a z-score of TROE",
    "composite": "a depositor-computed composite of the z-scores",
}

# 'بله' and 'بلی' are two spellings of the same answer, yes; 'خیر' is no.
YESNO = {"بله": 1, "بلی": 1, "خیر": 0}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {[c[:30] for c in text_cols]}")
    assert len(df.columns) > 0
    assert text_cols, "the screen selected no columns -- check the dtype test"
    # None is free text: each has a handful of distinct closed-category values.
    for c in text_cols:
        k = df[c].nunique()
        assert k <= 8, f"{c[:30]} has {k} distinct values -- check for free text"


def main() -> None:
    df, meta = pyreadstat.read_sav(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 714, len(df)

    labelled = sum(1 for c in df.columns
                   if (meta.column_names_to_labels.get(c) or "").strip())
    print(f"variable labels present: {labelled} of {len(df.columns)} (every "
          f"item's label is its full Persian stem); value-labelled variables: "
          f"{len(meta.variable_value_labels)} -- so the response anchors are "
          "NOT in the deposit, see the docstring")

    screen = [c for c in df.columns
              if pd.api.types.is_string_dtype(df[c]) and c not in COV_MAP]
    assert len(screen) == 1, screen
    screen = screen[0]
    assert SCREEN_LABEL_FRAGMENT in (meta.column_names_to_labels.get(screen) or "")

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = pd.to_numeric(df[src].replace("", pd.NA), errors="raise")
    vals = set(df[screen].dropna().unique())
    assert vals <= set(YESNO), vals
    df["cov_buys_online_regularly"] = df[screen].map(YESNO)
    covs = list(COV_MAP.values()) + ["cov_buys_online_regularly"]

    accounted = (set(COV_MAP) | set(covs) | set(DROP) | {"id", screen}
                 | {c for cols, _p in BLOCKS.values() for c in cols})
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in DROP.items():
        print(f"skipped column {c}: {why}")

    for table, (cols, permitted) in BLOCKS.items():
        assert all(c in df.columns for c in cols), (table, cols)
        codes = {c: c.lower() for c in cols}
        assert len(set(codes.values())) == len(cols), codes
        long = df[["id"] + covs + cols].rename(columns=codes)
        long = long.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
        before = long["resp"].notna().sum()
        long = long[long["resp"].isin(permitted)]
        if before != len(long):
            print(f"{table}: dropped {before - len(long)} cell(s) of {before} "
                  f"outside {permitted}")
        write(long, table, covs)


def write(long: pd.DataFrame, table: str, covs: list) -> None:
    long = long.copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:200]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
