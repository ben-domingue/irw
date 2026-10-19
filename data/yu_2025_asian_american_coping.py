"""Acculturation-based family conflict and mental health, Asian American youth.

Source: https://zenodo.org/records/16879885
DOI: 10.5281/zenodo.16879885
Data: Data entry_v1_11-21-24.sav (SPSS, 127 respondents x 108 columns)
License: CC BY 4.0 (Zenodo record, licence id cc-by-4.0)
Item text: NOT shipped. Both label levels checked: value labels are populated
  for every item (all five AAFCS anchors, all four DASS anchors), but the
  variable labels are positional -- "Likelihood Q1", "Seriousness Q1", "Q1_S" --
  so the file holds the response options and not the questions. Shipping
  option_text alone when the stems are not in the deposit is what irw#1770
  forbids. The AAFCS stems are in Lee et al.'s published scale; the DASS-21
  stems are in Lovibond & Lovibond.

WITHHELD: the 48 `ciss*` items are the Coping Inventory for Stressful
Situations (Endler & Parker). The rights register blocks CISS and its matcher
`CISS` identifies these by their variable labels (CISSQ1_TO ..). Not shipped,
in any form.

Shipped:
  aafcs_likelihood   10 items, 1-5   Asian American Family Conflicts Scale
  aafcs_seriousness  10 items, 1-5   (the same 10 situations, rated twice)
  dass21             21 items, 0-3   DASS-21 -- register verdict `ship`

AAFCS Likelihood and Seriousness rate the same ten situations on two different
anchor sets ("almost never".."almost always" vs "Not at all".."Extremely"), so
they are two administrations, not one 20-item scale.

Note on the deposit's `dass7` column: it is spelled `daas7`. Kept in item order
as DASS item 7; the typo is the source's.
"""
import os

import pandas as pd
import pyreadstat

import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from irw_validate._checks import run_qc  # noqa: E402
_RAW_BASE = _Path(__file__).resolve().parent.parent / \
    "automated_finding" / "runs" / "raw"

RAW = os.environ.get(
    "YU_RAW",
    str(_RAW_BASE / "Data_entry_v1_11-21-24.sav"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

AAFCS_L = [f"AAFCS_L{i}" for i in range(1, 11)]
AAFCS_S = [f"AAFCS_S{i}" for i in range(1, 11)]
DASS = ([f"dass{i}" for i in range(1, 7)] + ["daas7"]
        + [f"dass{i}" for i in range(8, 22)])
COVS = {"Ethnicity": "cov_ethnicity", "Parent": "cov_parent_immigrant",
        "Adolescent": "cov_adolescent_immigrant"}
SCALES = {"aafcs_likelihood": (AAFCS_L, {1, 2, 3, 4, 5}),
          "aafcs_seriousness": (AAFCS_S, {1, 2, 3, 4, 5}),
          "dass21": (DASS, {0, 1, 2, 3})}


def main():
    d, meta = pyreadstat.read_sav(RAW, apply_value_formats=False)
    labels = meta.column_names_to_labels or {}
    print(f"read {d.shape[0]} rows x {d.shape[1]} cols")

    used = set(COVS) | {"ID"}
    for cols, _ in SCALES.values():
        used |= set(cols)
    # Printed skips, so the books balance.
    for c in d.columns:
        if c in used:
            continue
        lab = str(labels.get(c) or "")
        if c.lower().startswith(("ciss", "cisss")):
            print(f"  WITHHELD {c!r}: CISS item ({lab}) -- rights register `block`")
        elif c.lower().startswith("total") or c.lower().startswith("Total"):
            print(f"  skip {c!r}: derived total ({lab})")
        elif c in ("Age", "Sxs_DA"):
            print(f"  skip {c!r}: eligibility flag, single value ({lab})")
        else:
            print(f"  skip {c!r}: not an item of a shipped scale ({lab})")
        used.add(c)
    assert not [c for c in d.columns if c not in used]

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    os.makedirs(OUT, exist_ok=True)
    written = set()

    for name, (cols, scale) in SCALES.items():
        missing = [c for c in cols if c not in d.columns]
        assert not missing, f"{name}: missing {missing}"
        long = d.melt(id_vars=["id"] + list(COVS), value_vars=cols,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"].unique()) - scale
            assert not bad, f"{name}/{it}: resp {sorted(bad)} outside {sorted(scale)}"
        assert long["id"].nunique() >= 100, long["id"].nunique()
        assert long["item"].nunique() > 1
        long = long.rename(columns=COVS)
        out = long[["id", "item", "resp"] + [COVS[c] for c in COVS]]
        table = f"yu_2025_{name}"
        assert table not in written
        written.add(table)
        # The shared checks, which the script's own assertions are not
        # (irw_validate.contract `no_validator`). Fails block; the
        # warnings here are legitimate and are printed.
        _checks = run_qc(out)
        _fails = [(c.name, c.detail) for c in _checks if c.status == "fail"]
        assert not _fails, _fails
        for _c in _checks:
            if _c.status == "warn":
                print(f"    [qc warn] {_c.name}: {_c.detail[:160]}")
        out.to_csv(os.path.join(OUT, f"{table}.csv"), index=False)
        print(f"  {table}: {out['id'].nunique()} ids x {out['item'].nunique()} "
              f"items = {len(out)} responses")


if __name__ == "__main__":
    main()
