"""Acceptance of Meta AI in messaging apps (UTAUT2-shaped).

Source: https://zenodo.org/records/17176589
DOI: 10.5281/zenodo.17176589
Data: Meta AI Chatting Apps_Cleaned.csv (127 respondents x 42 columns)
License: CC BY 4.0 (Zenodo record, licence id cc-by-4.0)
Item text: not shipped -- the export carries positional codes only (PE1 .. UB6) with no stem and no codebook, and the constructs are UTAUT2's, whose wording the 2026-10-15 silence rule makes a hold.

Eight UTAUT2 constructs plus trust and a concern block, all 1-6, one table each. RIGHTS: the register's UTAUT2 `hold` row is scoped to another deposit (family Chen2026-GenAI), so no row covers this one; the silence rule (Ben, 2026-10-15) makes a named third-party instrument with no located grant a hold. Response tables ship on positional codes with no item text -- BATCH_LOG 2026-10-18i's ProQOL reasoning. The record title notes sensitive information was removed by the depositors.
"""
import glob
import os

import pandas as pd

RAWDIR = os.environ.get(
    "CAHYADI_RAWDIR",
    "/tmp/claude-1000/-home-ben-Dropbox-projects-irw-src-automated-finding/5eef9b18-8b21-4d62-a15f-a632f0def6f5/scratchpad/bC/raw/zenodo.17176589")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

SCALES = {'performance_expectancy': ['PE1', 'PE2', 'PE3', 'PE4'], 'effort_expectancy': ['EE1', 'EE2', 'EE3', 'EE4', 'EE5'], 'facilitating_conditions': ['FC1', 'FC2', 'FC3', 'FC4', 'FC5'], 'hedonic_motivation': ['HM1', 'HM2', 'HM3', 'HM4'], 'social_influence': ['SI1', 'SI2', 'SI3', 'SI4'], 'trust': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7'], 'concern': ['C1', 'C2', 'C3', 'C4'], 'behavioural_intention': ['BI1', 'BI2', 'BI3'], 'use_behaviour': ['UB1', 'UB2', 'UB3', 'UB4', 'UB5', 'UB6']}
SCALE = {1, 2, 3, 4, 5, 6}
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
        table = "cahyadi_2025_" + name
        assert table not in written, table
        written.add(table)
        cols_out = ["id", "item", "resp"] + [COVS[c] for c in COVS]
        long[cols_out].to_csv(os.path.join(OUT, table + ".csv"), index=False)
        print(f"  {table}: {long['id'].nunique()} ids x "
              f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    main()
