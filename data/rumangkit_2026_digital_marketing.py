"""Digital marketing capabilities, platform engagement, orientation.

Source: https://zenodo.org/records/20389375
DOI: 10.5281/zenodo.20389375
Data: Dataset_ICOSBE_2026.xlsx (170 respondents x 20 columns)
License: CC BY 4.0 (Zenodo record, licence id cc-by-4.0)
Item text: not shipped -- positional codes only (DMC_1 .. MMP_4), no stem in the workbook and no codebook deposited.

Six constructs of three to four items each, all 1-5, one table each -- batch B's one-file-per-scale handling of a PLS-SEM battery (the open question for Ben is noted in TODO). RIGHTS: no register row matches; positional codes, no item text.
"""
import glob
import os

import pandas as pd

RAWDIR = os.environ.get(
    "RUMANGKIT_DM_RAWDIR",
    "/tmp/claude-1000/-home-ben-Dropbox-projects-irw-src-automated-finding/5eef9b18-8b21-4d62-a15f-a632f0def6f5/scratchpad/bC/raw/zenodo.20389375")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

SCALES = {'dmc': ['DMC_1', 'DMC_2', 'DMC_3', 'DMC_4'], 'pe': ['PE_1', 'PE_2', 'PE_3'], 'co': ['CO_1', 'CO_2', 'CO_3'], 'pi': ['PI_1', 'PI_2', 'PI_3'], 'eo': ['EO_1', 'EO_2', 'EO_3'], 'mmp': ['MMP_1', 'MMP_2', 'MMP_3', 'MMP_4']}
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
        table = "rumangkit_2026_dm_" + name
        assert table not in written, table
        written.add(table)
        cols_out = ["id", "item", "resp"] + [COVS[c] for c in COVS]
        long[cols_out].to_csv(os.path.join(OUT, table + ".csv"), index=False)
        print(f"  {table}: {long['id'].nunique()} ids x "
              f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    main()
