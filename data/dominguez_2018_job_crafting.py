#!/usr/bin/env python3
# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0197276
# DOI: 10.1371/journal.pone.0197276
# SI: S1 File (10.1371/journal.pone.0197276.s001), XLSX
#
# Sheet layout: row0 = scale name/response-scale text (merged),
# row1 = subscale label, row2 = column header ("Item N" / "Subtotal" /
# "Total ..."), data starts row3. Four scales in one file: Job Crafting
# Scale (JCS, 1-5), Work Engagement (UWES, 0-6), Maslach Burnout
# Inventory (MBI, 0-6), Intention To Leave (ITL, 1-5). Subtotal/total
# aggregate columns are excluded.

import os
import io
import requests
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "automated_finding", "irw_output")

SI_URL = ("https://journals.plos.org/plosone/article/file"
          "?id=10.1371/journal.pone.0197276.s001&type=supplementary")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

# (output name, list of column indices, valid_max)
#
# JCS omits column 25, headed "Item 17". That column does not hold Item 17's
# responses: for 200 of the 202 respondents it holds the MEAN of columns
# 26-29, byte-identical to the block's own Subtotal in column 30, and 141 of
# its 202 values are non-integers on a 1-5 Likert (4.25, 2.75, 3.5, ...).
# A subscale-mean formula was filled one column too far left in the deposited
# workbook and overwrote the item. The last two rows escaped the fill -- they
# carry an integer response, and for those two the Subtotal is correctly a
# five-item mean -- which is what identifies it as a fill rather than a
# deliberate aggregate. See #1965.
#
# Item 17's responses are therefore not recoverable from this deposit for
# anyone but those two respondents, so the item is dropped rather than
# published as a truncated mean. (`resp.astype(int)` was silently turning
# 4.25 into 4, which is why it read as a plausible response.)
#
# The workbook's own `Total JCS` (column 31) averages all 21 columns including
# the damaged one, so the paper's JCS totals inherit the same defect. Not
# something this script can repair.
SCALES = {
    "dominguez_2018_jcs": ([6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 19, 20, 21,
                             22, 23, 26, 27, 28, 29], 5),
    "dominguez_2018_uwes": (list(range(32, 49)), 6),
    "dominguez_2018_mbi": (list(range(56, 78)), 6),
    "dominguez_2018_itl": ([85, 86, 87], 5),
}

# The source's own item numbers, where they are not simply 1..n. JCS keeps the
# workbook's numbering across the gap: `item_18`..`item_21` stay the paper's
# items 18-21 rather than sliding down to fill 17-20. Positional renumbering
# would silently change what every label after the gap refers to, and change
# the join key for anyone already using the table.
ITEM_NUMBERS = {
    "dominguez_2018_jcs": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                            16, 18, 19, 20, 21],
}

# Aggregate columns that must never enter an item set, as (out_name, column,
# what it is). Checked at build time so a future edit to SCALES cannot
# reintroduce one, and so this file states the evidence rather than asserting
# the conclusion.
AGGREGATE_COLS = {
    11: "JCS subscale mean (items 1-5)",
    18: "JCS subscale mean (items 6-11)",
    24: "JCS subscale mean (items 12-16)",
    25: "JCS subscale mean (items 18-21), mis-headed `Item 17` -- #1965",
    30: "JCS subscale mean (items 18-21), duplicate of column 25",
    31: "Total JCS",
    88: "Intention To Leave total",
}

COV_COLS = {
    1: "cov_age",
    2: "cov_institution",
    3: "cov_gender",
    4: "cov_institution_type",
    5: "cov_residency_level",
}


def convert():
    r = requests.get(SI_URL, headers=UA, timeout=120)
    r.raise_for_status()
    raw = pd.read_excel(io.BytesIO(r.content), sheet_name="Hoja1", header=None)
    data = raw.iloc[3:].reset_index(drop=True)
    data.columns = range(raw.shape[1])

    data = data.rename(columns=COV_COLS)
    data.insert(0, "id", range(1, len(data) + 1))
    cov_cols = list(COV_COLS.values())
    for c in cov_cols:
        data[c] = pd.to_numeric(data[c], errors="coerce")

    os.makedirs(OUT_DIR, exist_ok=True)
    for out_name, (item_cols, valid_max) in SCALES.items():
        item_cols = [c for c in item_cols]
        bad = [c for c in item_cols if c in AGGREGATE_COLS]
        assert not bad, (f"{out_name}: aggregate column(s) in the item set: " +
                         ", ".join(f"{c} ({AGGREGATE_COLS[c]})" for c in bad))
        assert len(item_cols) == len(set(item_cols)), f"{out_name}: duplicate column"
        assert len(ITEM_NUMBERS.get(out_name, item_cols)) == len(item_cols), \
            f"{out_name}: ITEM_NUMBERS does not match the column list"
        cols = ["id"] + cov_cols + item_cols
        sub = data[cols].copy()
        numbers = ITEM_NUMBERS.get(out_name, range(1, len(item_cols) + 1))
        item_names = {c: f"item_{n}" for c, n in zip(item_cols, numbers)}
        sub = sub.rename(columns=item_names)
        item_col_names = list(item_names.values())

        long = sub.melt(id_vars=["id"] + cov_cols, value_vars=item_col_names,
                         var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        # isolated data-entry error check: drop values outside documented scale
        long = long[(long["resp"] >= 0) & (long["resp"] <= valid_max)]
        # A non-integer value on a Likert item is an aggregate that has been
        # mistaken for a response, not a response -- astype(int) below would
        # truncate it into a plausible one, which is how #1965 stayed hidden.
        frac = long.loc[long["resp"] % 1 != 0]
        assert frac.empty, (f"{out_name}: {len(frac)} non-integer response(s) in "
                            f"{sorted(frac['item'].unique())}")
        long["resp"] = long["resp"].astype(int)

        out_cols = ["id", "item", "resp"] + cov_cols
        long = long[out_cols].sort_values(["id", "item"]).reset_index(drop=True)

        fname = f"{out_name}.csv"
        long.to_csv(os.path.join(OUT_DIR, fname), index=False)
        print(f"{fname}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
