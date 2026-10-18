"""Servant leadership, organizational justice, OCB and job performance.

Two Zenodo deposits that are ONE data collection, built together so the same
respondents are not shipped twice.

Source: https://zenodo.org/records/21522509  (the fuller of the two)
DOI: 10.5281/zenodo.21522509
Data: Dataset_SL and Job Performance_rev1.xlsx (100 respondents x 44 columns)
Source: https://zenodo.org/records/22089166
DOI: 10.5281/zenodo.22089166
Data: Dataset_SL&WE and Job Performance.xlsx (100 respondents x 57 columns)
License: CC BY 4.0 on both records (licence id cc-by-4.0)
Item text: not shipped. Both workbooks are bare Google Forms exports with
  positional codes (SL1 .. KY7) and no stem, no codebook, no questionnaire.

WHY ONE SCRIPT. Both deposits are by Stefanus Rumangkit, both hold exactly 100
rows, and they share 24 columns (SL1-SL7, OCB1-OCB17). On those shared columns
**all 75 distinct response vectors in 22089166 also occur in 21522509** (75 of
75), while no row matches position-for-position -- the same people, reordered.
Shipping both deposits' SL and OCB blocks would put those 100 respondents in
the corpus twice, which is the duplication #1779/#1842 exist to undo.

So each instrument is shipped exactly once, from the deposit that carries it
most completely:

  from 21522509:  sl   13 items   OCB 17 items   kk 7 items   ky 7 items
  from 22089166:  oj   17 items   we   7 items   jp 6 items   eh 3 items

The two groups are given different table prefixes (`rumangkit_2026_*` and
`rumangkit_2026b_*`) deliberately: the row order differs between the files and
the deposits carry no respondent key, so the ids are NOT comparable across the
two groups and must not look as if they are. Within a group they are.

`SL62` is the source's own column name, kept verbatim as an item code; it sits
between SL6 and SL7 and is most likely a mis-typed SL6_2. Renaming it would
invent a code the deposit does not have.

RIGHTS. `sl` is a servant-leadership measure of 13 items. The register blocks
the Servant Leadership Survey (SLS) of van Dierendonck & Nuijten, which has 30
items, so that row does not identify this instrument and the deposit does not
say which scale it used. `oj`, `ocb` and `we` are likewise named third-party
constructs (organizational justice, organizational citizenship behaviour, work
engagement) that no register row matches -- note `we` is 7 items on 1-5, so it
is not the UWES, which is 9 or 17 items on 0-6. All ship as RESPONSE tables
only, on BATCH_LOG 2026-10-18i's ProQOL reasoning: positional codes, no item
text, so no instrument wording is exposed. Flagged in TODO as register-row
requests for servant leadership (non-SLS), organizational justice and OCB.
"""
import os

import pandas as pd

BASE = ("/tmp/claude-1000/-home-ben-Dropbox-projects-irw-src-automated-finding/"
        "5eef9b18-8b21-4d62-a15f-a632f0def6f5/scratchpad/bC/raw")
RAW_B = os.environ.get("RUMANGKIT_B_RAW", os.path.join(
    BASE, "zenodo.21522509", "Dataset_SL and Job Performance_rev1.xlsx"))
RAW_A = os.environ.get("RUMANGKIT_A_RAW", os.path.join(
    BASE, "zenodo.22089166", "Dataset_SL&WE and Job Performance.xlsx"))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

FROM_B = {
    "sl":  ["SL1", "SL2", "SL3", "SL4", "SL5", "SL6", "SL62", "SL7", "SL8",
            "SL9", "SL10", "SL11", "SL12"],
    "ocb": [f"OCB{i}" for i in range(1, 18)],
    "kk":  [f"KK{i}" for i in range(1, 8)],
    "ky":  [f"KY{i}" for i in range(1, 8)],
}
FROM_A = {
    "oj": [f"OJ{i}" for i in range(1, 18)],
    "we": [f"WE{i}" for i in range(1, 8)],
    "jp": [f"JP{i}" for i in range(1, 7)],
    "eh": [f"EH{i}" for i in range(1, 4)],
}
SCALE = {1, 2, 3, 4, 5}


def build(path, scales, prefix, shared_note, written):
    d = pd.read_excel(path)
    d.columns = [str(c).strip() for c in d.columns]
    print(f"read {os.path.basename(path)}: {d.shape[0]} x {d.shape[1]}")
    used = set()
    for cols in scales.values():
        used |= set(cols)
    for c in d.columns:
        if c not in used:
            print(f"  skip {c!r}: {shared_note}")
            used.add(c)
    assert not [c for c in d.columns if c not in used]

    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    for name, cols in scales.items():
        missing = [c for c in cols if c not in d.columns]
        assert not missing, f"{name}: missing {missing}"
        long = d.melt(id_vars=["id"], value_vars=cols,
                      var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        for it, g in long.groupby("item"):
            bad = set(g["resp"].unique()) - SCALE
            assert not bad, f"{name}/{it}: {sorted(bad)}"
        assert long["id"].nunique() >= 100, (name, long["id"].nunique())
        assert long["item"].nunique() > 1
        table = f"{prefix}{name}"
        assert table not in written, f"duplicate output name {table}"
        written.add(table)
        long[["id", "item", "resp"]].to_csv(
            os.path.join(OUT, f"{table}.csv"), index=False)
        print(f"  {table}: {long['id'].nunique()} ids x "
              f"{long['item'].nunique()} items = {len(long)} responses")


def main():
    os.makedirs(OUT, exist_ok=True)
    written = set()
    build(RAW_B, FROM_B, "rumangkit_2026_",
          "not an item of a scale shipped from this deposit", written)
    build(RAW_A, FROM_A, "rumangkit_2026b_",
          "shipped from 21522509 instead -- the same 100 respondents, "
          "so shipping it here too would duplicate them", written)


if __name__ == "__main__":
    main()
