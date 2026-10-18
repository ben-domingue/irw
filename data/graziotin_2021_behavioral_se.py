"""Behavioral Software Engineering: psychometric evaluation example.

Source: https://zenodo.org/records/4911906
DOI: 10.5281/zenodo.4911906
Data: graziotin_et_al-bse_psychometrics_example.csv (142 respondents x 31 columns)
License: CC BY 4.0 (Zenodo record, licence id cc-by-4.0)
Item text: not shipped -- the companion data for a methods paper; the columns are factor-and-position codes (F1_1 .. F5_31) with no stem in the file and no codebook deposited.

The deposit accompanies Graziotin, Lenberg, Feldt & Wagner's psychometrics tutorial and holds one 31-item instrument already grouped into five factors by its column names. Shipped as five tables, one per factor, since the source's own naming asserts that grouping. All 1-5.
"""
import glob
import os

import pandas as pd

RAWDIR = os.environ.get(
    "GRAZIOTIN_RAWDIR",
    "/tmp/claude-1000/-home-ben-Dropbox-projects-irw-src-automated-finding/5eef9b18-8b21-4d62-a15f-a632f0def6f5/scratchpad/bC/raw/zenodo.4911906")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

SCALES = {'f1': ['F1_1', 'F1_2', 'F1_3', 'F1_4', 'F1_5', 'F1_6', 'F1_7'], 'f2': ['F2_8', 'F2_9', 'F2_10', 'F2_11'], 'f3': ['F3_12', 'F3_13', 'F3_14', 'F3_15', 'F3_16', 'F3_17', 'F3_18', 'F3_19', 'F3_20'], 'f4': ['F4_21', 'F4_22', 'F4_23', 'F4_24'], 'f5': ['F5_25', 'F5_26', 'F5_27', 'F5_28', 'F5_29', 'F5_30', 'F5_31']}
SCALE = {1, 2, 3, 4, 5}
COVS = {}


def read():
    p = glob.glob(os.path.join(RAWDIR, "*.csv"))
    assert p, "raw file not found in " + RAWDIR
    path = sorted(p)[0]
    if path.lower().endswith((".xlsx", ".xls")):
        d = pd.read_excel(path)
    else:
        d = pd.read_csv(path)
    d.columns = [str(c).strip() for c in d.columns]
    return d, os.path.basename(path)


def main():
    d, fname = read()
    print(f"read {fname}: {d.shape[0]} rows x {d.shape[1]} cols")
    used = set(COVS)
    for cols in SCALES.values():
        used |= set(cols)
    for c in d.columns:
        if c not in used:
            print(f"  skip {c!r}: not an item of a shipped scale")
            used.add(c)
    assert not [c for c in d.columns if c not in used]

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    os.makedirs(OUT, exist_ok=True)
    written = set()
    for name, cols in SCALES.items():
        missing = [c for c in cols if c not in d.columns]
        assert not missing, f"{name}: missing {missing}"
        long = d.melt(id_vars=["id"] + list(COVS), value_vars=cols,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        # Per item, not pooled: an out-of-range value isolated to one item is a
        # data-entry fault even when the merged range looks fine.
        for it, g in long.groupby("item"):
            bad = set(g["resp"].unique()) - SCALE
            assert not bad, f"{name}/{it}: {sorted(bad)} outside {sorted(SCALE)}"
        assert long["id"].nunique() >= 100, (name, long["id"].nunique())
        assert long["item"].nunique() > 1, name
        long = long.rename(columns=COVS)
        table = "graziotin_2021_" + name
        assert table not in written, table
        written.add(table)
        cols_out = ["id", "item", "resp"] + [COVS[c] for c in COVS]
        long[cols_out].to_csv(os.path.join(OUT, table + ".csv"), index=False)
        print(f"  {table}: {long['id'].nunique()} ids x "
              f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    main()
