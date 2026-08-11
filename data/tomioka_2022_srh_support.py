#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0265830
# DOI: 10.1371/journal.pone.0265830
# S1 Data (raw survey data): https://doi.org/10.1371/journal.pone.0265830.s003
#   (resolves to https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0265830.s003&type=supplementary)
#
# Paper: Tomioka A, Obama K, Okada H, Yamauchi E, Iwase K, Maru M (2022).
# "Nurse's perceptions of support for sexual and reproductive issues in
# adolescents and young adults with cancer." PLOS ONE.
#
# The raw file ("Dataset" sheet, 865 nurses) plus its "variable" codebook
# sheet together cover four distinct question groups that are shipped as
# four separate IRW files per datastandard.md's "one file per scale" rule:
#   - B1-B2:  importance of explaining sexual/reproductive issues to patients
#             by age group (4-pt: 1=very important ... 4=not important)
#   - B3-B6:  perceived sufficiency of information/support
#             (4-pt: 1=sufficient ... 4=insufficient; rows coded 5="I don't
#              know" are a non-response and are already absent from the raw
#              file for these items, consistent with the paper's exclusion
#              of "I don't know" respondents from this measure)
#   - B7-1..B7-12: binary (0/1) applicable/not-applicable indicators for
#             12 types of support currently provided
#   - B9-1..B9-7:  binary (0/1) "necessary" indicators for 7 future-challenge
#             areas
# B8 (a single item) is excluded per datastandard.md's no-single-item rule.
# A1-A11 demographic/workplace columns become cov_* covariates.

import os
import pandas as pd
import requests

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "..", "automated_finding", "irw_output")
URL = "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0265830.s003&type=supplementary"
HEADERS = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "A1": "cov_institution", "A2": "cov_facility_certification",
    "A3": "cov_prefecture", "A4": "cov_n_beds",
    "A5": "cov_department", "A5-1": "cov_department_detail",
    "A6": "cov_ward_type", "A7": "cov_manager",
    "A7-1": "cov_manager_role", "A8": "cov_certified_nurse",
    "A8-1": "cov_certification_type", "A9": "cov_years_nursing",
    "A10": "cov_years_oncology_nursing", "A11": "cov_academic_society",
}

SCALES = {
    "tomioka_2022_srh_importance": (["B1", "B2"], 1, 4),
    "tomioka_2022_srh_sufficiency": (["B3", "B4", "B5", "B6"], 1, 4),
    "tomioka_2022_srh_support_types": ([f"B7-{i}" for i in range(1, 13)], 0, 1),
    "tomioka_2022_srh_future_needs": ([f"B9-{i}" for i in range(1, 8)], 0, 1),
}


def fetch_raw():
    local = os.path.join(BASE, "pone0265830_s003.xlsx")
    if not os.path.exists(local):
        r = requests.get(URL, headers=HEADERS, timeout=120)
        r.raise_for_status()
        with open(local, "wb") as f:
            f.write(r.content)
    return local


def convert():
    raw = fetch_raw()
    df = pd.read_excel(raw, sheet_name="Dataset")
    df = df.rename(columns={"ID": "id"})
    # A handful of source IDs are non-numeric strings (e.g. "01104-1") that
    # a naive to_numeric() coercion would turn into NaN and silently drop
    # those respondents. Per datastandard.md's "Text IDs that cannot be
    # made numeric" guidance, keep id as string when any value can't be
    # coerced, rather than forcing numeric conversion and losing rows.
    numeric_id = pd.to_numeric(df["id"], errors="coerce")
    if numeric_id.isna().any():
        df["id"] = df["id"].astype(str)
    else:
        df["id"] = numeric_id.astype(int)
    df = df.dropna(subset=["id"]).reset_index(drop=True)
    assert df["id"].nunique() == len(df), "id column is not unique"

    df = df.rename(columns=COV_MAP)
    cov_cols = list(COV_MAP.values())

    for out_name, (item_cols, lo, hi) in SCALES.items():
        item_cols = [c for c in item_cols if c in df.columns]
        sub = df[["id"] + cov_cols + item_cols]
        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long = long[(long["resp"] >= lo) & (long["resp"] <= hi)].reset_index(drop=True)

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols]
        path = os.path.join(OUT_DIR, f"{out_name}.csv")
        long.to_csv(path, index=False)
        print(f"{out_name}.csv: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


if __name__ == "__main__":
    convert()
