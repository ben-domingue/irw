from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR   = REPO_ROOT / "automated_finding" / "irw_output"

TITLE = ("U.S. Federal Employees With Disabilities: How Perceptions of "
         "Diversity, Equity, Inclusion, and Accessibility Affect "
         "Differences in Job Satisfaction, Organizational Commitment, and "
         "Job Involvement (Emidy, Lewis & Pizarro-Bore, 2024, Public "
         "Personnel Management) -- 2022 Federal Employee Viewpoint Survey "
         "(FEVS) microdata")
URL  = "https://doi.org/10.7910/DVN/UXRFPV"
DOI  = "10.1177/00910260241253577"
UA   = {"User-Agent": "irw-batch/1.0 (research)"}

FILE_URL = "https://dataverse.harvard.edu/api/access/datafile/10255219"

# FEVS 2022 uses 5 distinct 5-point value-label sets across its items
# (fscale/rscale = agree-disagree in each direction, gscale = poor-good,
# sscale = dissatisfied-satisfied, ascale = never-always) -- all genuine
# ordinal Likert, just different item wording, so kept as one instrument
# file. Excluded: q15_1-6 (unlabeled binary multi-select checklist, not
# clearly an attitude item), and q90-93/q95 (labeled t1/t2/t3/t4/l1 --
# nominal/factual telework-arrangement questions, not ordinal attitude
# items). Confirmed via the .dta file's own embedded Stata value-label
# metadata, not guessed from value ranges alone.
VALID_LABEL_SETS = {"fscale", "rscale", "gscale", "sscale", "ascale"}

COV_COLS = {
    "disability": "cov_disability",
}


def get_item_columns() -> list[str]:
    reader = pd.io.stata.StataReader(_local_path)
    reader._ensure_open()
    lbllist = dict(zip(reader._varlist, reader._lbllist))
    return [c for c, l in lbllist.items() if l in VALID_LABEL_SETS]


_local_path = None


def convert():
    global _local_path
    import os
    import requests
    _local_path = "/tmp/FEVS2022_Clean_2-22-23.dta"
    if os.path.exists(_local_path):
        print(f"Using cached {_local_path}")
    else:
        print("Downloading FEVS2022_Clean_2-22-23.dta (large file, may take a while)...")
        r = requests.get(FILE_URL, headers=UA, timeout=300, stream=True)
        r.raise_for_status()
        with open(_local_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)

    item_cols = get_item_columns()
    print(f"{len(item_cols)} item columns identified via Stata value-label metadata")

    raw = pd.read_stata(_local_path, convert_categoricals=False,
                         columns=list(COV_COLS.keys()) + item_cols)
    # "randomid" is NOT a unique person key despite the name -- confirmed
    # empirically: 557,778 raw rows but only 99,615 unique randomid values
    # (up to 18 rows sharing one), so joining on it produces a cartesian-
    # product blowup. Use row position instead, matching this pipeline's
    # standard fallback whenever a source ID column turns out unreliable.
    raw = raw.reset_index(drop=True)
    raw.insert(0, "id", raw.index + 1)
    raw = raw.rename(columns=COV_COLS)
    cov_cols = list(COV_COLS.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "emidy2024_fevs.csv"
    header_written = False
    total_rows = 0

    # Process one item column at a time to keep peak memory bounded --
    # melting all 93 items x 557,778 respondents at once (~52M rows) in a
    # single frame is unnecessary when each item's long-format slice can be
    # written and discarded independently. id/items/covariates are all
    # already row-aligned in `raw`, so a direct column slice replaces the
    # merge entirely (no duplicate-key risk, no merge overhead x93).
    for i, item in enumerate(item_cols, 1):
        long = raw[["id", item] + list(COV_COLS.values())].copy()
        long = long.rename(columns={item: "resp"})
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        # Valid range for every label set here is 1-5; anything else (0, 6,
        # etc. seen in a handful of items) is an unlabeled sentinel
        # ("Do Not Know"/"Does Not Apply" per FEVS methodology), not a real
        # scale point -- filter before it contaminates resp.
        long = long[(long["resp"] >= 1) & (long["resp"] <= 5)]
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        long["resp"] = long["resp"].astype(int)
        long["item"] = item
        col_order = ["id", "item", "resp"] + cov_cols
        long = long[col_order]
        long.to_csv(out_path, mode="a" if header_written else "w",
                    header=not header_written, index=False)
        header_written = True
        total_rows += len(long)
        if i % 20 == 0 or i == len(item_cols):
            print(f"  [{i}/{len(item_cols)}] {item} -> {total_rows:,} rows written so far")

    print(f"emidy2024_fevs.csv: ids={raw['id'].nunique()} items={len(item_cols)} "
          f"resp=1-5 rows={total_rows:,}")


if __name__ == "__main__":
    convert()
