"""Community Resilience Scale for Youth (CRS-Y), Portuguese border regions.

Source: Silva, S. M., Silva, A. M., Faria, S. & Nata, G. (2022), Zenodo
10.5281/zenodo.6557048, CC BY 4.0 -- "Development and validation of a
Community Resilience Scale for Youth (CRS-Y)". 3,563 young respondents across
four Portuguese NUTS-II regions.

All 16 administered items ship, not just the 12 the published scale retained.
The four dropped in validation (`Res_6_deleted`, `Res_11_deleted`,
`Res_12_deleted`, `Res_13_deleted`) were answered by every respondent on the
same 1-5 scale, so they are real item responses; `itemcov_retained` records
which survived rather than discarding the data.

Items are named by their ORIGINAL questionnaire position, parsed from the
variable labels, because the column names were renumbered after deletion --
`Res_6` is questionnaire item 7 and `Res_10` is item 14. Naming items after
the columns would silently renumber the instrument.

`Number` is labelled "Number of the participants" but holds only 284 distinct
values over 3,563 rows (a within-class sequence), so it is NOT a person key;
a sequential id is assigned instead. `Res_Factor1..3` are computed factor
scores and are dropped.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

RECORD = 6557048
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "silva_2022_crsy"

N_ITEMS = 16
SCALE = {1.0, 2.0, 3.0, 4.0, 5.0}
COVARIATES = {
    "Region": "cov_region",
    "Age": "cov_age_band",
    "Sex": "cov_sex",
    "School_year": "cov_school_year",
    "Course_attended": "cov_course",
    "Mother_ed": "cov_mother_education",
    "Father_ed": "cov_father_education",
    "Books_number": "cov_books_at_home",
    "dataset": "cov_analysis_split",
}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(".sav"))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    df, meta = pyreadstat.read_sav(fetch_raw(path), apply_value_formats=False)
    labels = meta.column_names_to_labels

    # Original questionnaire position lives in the label ("7. There is a lot
    # of help..."), not in the renumbered column name.
    items = {}
    for c in df.columns:
        if not c.startswith("Res_") or c.startswith("Res_Factor"):
            continue
        m = re.match(r"\s*(\d+)\.", labels.get(c) or "")
        assert m, f"no questionnaire number in label for {c}"
        items[c] = int(m.group(1))
    assert len(items) == N_ITEMS, f"expected {N_ITEMS} items, got {len(items)}"
    assert sorted(items.values()) == list(range(1, N_ITEMS + 1)), \
        f"questionnaire numbering not 1..{N_ITEMS}: {sorted(items.values())}"

    cols = list(items)
    observed = {v for v in pd.unique(df[cols].values.ravel()) if pd.notna(v)}
    assert observed <= SCALE, f"off-scale response(s): {sorted(observed - SCALE)}"

    d = df.rename(columns=COVARIATES).copy()
    for src, dst in COVARIATES.items():
        vl = meta.variable_value_labels.get(src)
        if vl:
            d[dst] = d[dst].map(vl)
    d["id"] = range(1, len(d) + 1)

    long = d.melt(id_vars=["id"] + list(COVARIATES.values()),
                  value_vars=cols, var_name="_col", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long["item"] = long["_col"].map(lambda c: f"crsy_{items[c]:02d}")
    long["itemcov_retained"] = (~long["_col"].str.endswith("_deleted")).astype(int)

    out = long[["id", "item", "resp", "itemcov_retained"]
               + list(COVARIATES.values())]
    os.makedirs(OUT_DIR, exist_ok=True)
    out.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(out):,} responses | {out['id'].nunique():,} ids | "
          f"{out['item'].nunique()} items "
          f"({out.groupby('item')['itemcov_retained'].first().sum()} retained)")


if __name__ == "__main__":
    main()
