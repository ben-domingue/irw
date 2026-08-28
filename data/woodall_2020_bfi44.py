"""Big Five Inventory (BFI-44).

Source: Woodall, Tony (2020), Zenodo 10.5281/zenodo.3695861, CC BY 4.0,
"BFI Inventory Scores". Single file `BFI Inventory With Reversed Scores.sav`,
271 respondents x 51 columns; 44 BFI items on a 1-5 agreement scale.

The five trait scores (Extraversion, Agreeableness, Conscientiousness,
Neuroticism, Open) are dropped as composites.

**The shipped responses are already reverse-scored where the BFI requires it.**
The file is named "With Reversed Scores" and 16 of the 44 item columns carry an
`RRRRR` suffix -- the BFI-44 has exactly 16 reverse-keyed items, so the marked
columns hold the recoded value rather than the respondent's raw selection. The
deposit publishes no un-reversed copy, so that is what is available. The suffix
is kept in the item code rather than stripped, so the transformation stays
visible to anyone reading the item set instead of being hidden behind a tidier
name.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

RECORD = 3695861
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "woodall_2020_bfi44"

COVARIATES = {"Cohort_1_to_5": "cov_cohort", "Gender_1M_2F": "cov_gender"}
COMPOSITES = ["Extraversion", "Agreeableness", "Conscientiousness",
              "Neuroticism", "Open"]


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
    src = fetch_raw(path)
    try:
        df, _meta = pyreadstat.read_sav(src, apply_value_formats=False)
    except Exception:
        df, _meta = pyreadstat.read_sav(src, apply_value_formats=False,
                                        encoding="latin1")

    items = [c for c in df.columns if re.match(r"^[EACNO]_", str(c))]
    assert len(items) == 44, f"expected 44 BFI items, found {len(items)}"
    reversed_items = [c for c in items if str(c).endswith("RRRRR")]
    assert len(reversed_items) == 16, \
        f"BFI-44 has 16 reverse-keyed items; found {len(reversed_items)} marked"

    accounted = set(items) | set(COVARIATES) | set(COMPOSITES)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES).reset_index(drop=True)
    covs = list(COVARIATES.values())
    df["id"] = df.index + 1

    long = (df.melt(id_vars=["id"] + covs, value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 44
    assert long["resp"].between(1, 5).all(), "BFI is a 1-5 scale"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
