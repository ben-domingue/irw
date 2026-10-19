"""SME digital-payment adoption: UTAUT with digital literacy.

Source: https://zenodo.org/records/16760555
DOI: 10.5281/zenodo.16760555
Data: Kuesioner UTAUT.xlsx (141 respondents x 21 columns)
License: CC BY 4.0 (Zenodo record, licence id cc-by-4.0)
Item text: not shipped -- positional codes only (PE1 .. BI3), no stem in the workbook, no codebook; and the constructs are UTAUT's, whose wording the 2026-10-15 silence rule makes a hold.

Five constructs, all 1-5, one table each. RIGHTS: as for the other UTAUT deposits in this batch -- no register row covers it, the silence rule makes the wording a hold, and the response tables ship on positional codes with no item text.
"""
import glob
import os

import pandas as pd

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from irw_validate._checks import run_qc  # noqa: E402
_RAW_BASE = _Path(__file__).resolve().parent.parent / \
    "automated_finding" / "runs" / "raw"

RAWDIR = os.environ.get(
    "TRIANA_RAWDIR",
    str(_RAW_BASE / "zenodo.16760555"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

SCALES = {'performance_expectancy': ['PE1', 'PE2', 'PE3', 'PE4', 'PE5'], 'effort_expectancy': ['EE1', 'EE2', 'EE3'], 'social_influence': ['SI1', 'SI2', 'SI3'], 'facilitating_conditions': ['FC1', 'FC2', 'FC3'], 'digital_literacy': ['DL1', 'DL2', 'DL3', 'DL4'], 'behavioural_intention': ['BI1', 'BI2', 'BI3']}
SCALE = {1, 2, 3, 4, 5}
COVS = {}


def read():
    p = glob.glob(os.path.join(RAWDIR, "*.xlsx"))
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
        table = "triana_2025_" + name
        assert table not in written, table
        written.add(table)
        cols_out = ["id", "item", "resp"] + [COVS[c] for c in COVS]
        # The shared checks, which the script's own assertions are not
        # (irw_validate.contract `no_validator`). Fails block; the
        # warnings here are legitimate and are printed.
        _checks = run_qc(long)
        _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
        assert not _fails, _fails
        for _c in _checks:
            if _c.status == "warn":
                print(f"    [qc warn] {_c.name}: {_c.detail[:160]}")
        long[cols_out].to_csv(os.path.join(OUT, table + ".csv"), index=False)
        print(f"  {table}: {long['id'].nunique()} ids x "
              f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    main()
