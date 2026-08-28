"""Workplace Incivility Scale (WIS) and NAQ-R, Swedish sample.

Source: Daderman & Cider (2023), Mendeley Data 10.17632/j95y99fzb9, CC BY 4.0 --
"Workplace Incivility Scale Swedish Version N426". Single .sav, 426
respondents x 36 columns.

Two instruments ship:

  daderman_2023_wis     7 WIS items, 0-4
  daderman_2023_naq_r   22 Negative Acts Questionnaire-Revised items, 1-5

The EQ-5D block (`H1`..`H5`) is NOT shipped. `H2` is constant at 1 across all
426 respondents -- a zero-variance dimension carries no item response
information, and dropping it to salvage the other four would ship a
four-dimension EQ-5D, which is not the instrument. `EQ_VAS` and `EQ5D_Index`
are a visual-analogue rating and a derived utility index respectively, neither
of them item responses; both are kept as covariates instead.

Several NAQ-R items top out at 3 or 4 rather than 5. That is non-use of the
upper categories in a low-incivility sample, not a different response format:
the items with a 5 are spread across the block rather than confined to one
subscale, so there is no basis for treating them as differently scaled.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

DOI = "10.17632/j95y99fzb9"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")

SCALES = {"daderman_2023_wis": (r"^WIS\d+$", 7, (0, 4)),
          "daderman_2023_naq_r": (r"^naq\d+$", 22, (1, 5))}
COVARIATES = {"EQ_VAS": "cov_eq_vas", "EQ5D_Index": "cov_eq5d_index"}
NOT_SHIPPED = [f"H{i}" for i in range(1, 6)]


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    key = DOI.split("/")[-1]
    data = requests.get(f"https://data.mendeley.com/public-api/datasets/{key}",
                        timeout=120).json()
    sav = [f for f in data.get("files", [])
           if f.get("filename", "").lower().endswith(".sav")]
    assert len(sav) == 1, f"expected one .sav, found {len(sav)}"
    r = requests.get(sav[0]["content_details"]["download_url"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", sav[0]["filename"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    src = fetch_raw(path)
    try:
        df, _meta = pyreadstat.read_sav(src, apply_value_formats=False)
    except Exception:
        df, _meta = pyreadstat.read_sav(src, apply_value_formats=False,
                                        encoding="latin1")

    item_cols = {}
    for table, (pat, n, _rng) in SCALES.items():
        cols = [c for c in df.columns if re.match(pat, str(c))]
        assert len(cols) == n, f"{table}: expected {n} items, found {len(cols)}"
        item_cols[table] = cols

    accounted = set(sum(item_cols.values(), [])) | set(COVARIATES) \
        | set(NOT_SHIPPED)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    # The stated reason for excluding EQ-5D must actually hold.
    assert df["H2"].nunique(dropna=True) == 1, \
        "H2 is no longer constant; revisit the EQ-5D exclusion"

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    covs = list(COVARIATES.values())
    df["id"] = df.index + 1

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, (_pat, n, (lo, hi)) in SCALES.items():
        long = (df.melt(id_vars=["id"] + covs, value_vars=item_cols[table],
                        var_name="item", value_name="resp")
                  .dropna(subset=["resp"]))
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]
        assert long["id"].nunique() >= 100, table
        assert long["item"].nunique() == n, table
        assert long["resp"].between(lo, hi).all(), \
            f"{table}: expected {lo}-{hi}"
        long.to_csv(os.path.join(OUT_DIR, f"{table}.csv"), index=False)
        print(f"{table}: {len(long):,} rows, {long['id'].nunique():,} ids, "
              f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
