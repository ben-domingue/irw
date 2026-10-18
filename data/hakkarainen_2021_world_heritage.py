"""Place attachment and governance, High Coast/Kvarken World Heritage Site.

Source: https://zenodo.org/records/5243244
DOI: 10.5281/zenodo.5243244
Data: RECOMS_ESR8_worldheritage_database.xlsx (333 respondents x 117 columns)
License: CC BY 4.0 (Zenodo record, licence id cc-by-4.0)
Item text: not shipped. The stems ARE in the deposit -- the workbook's row 2 is
  the item wording and row 1 the section prompt, in English -- but the response
  ANCHORS are nowhere in it: every Likert section says only "To what extent do
  you agree or disagree", and the five scale points carry no labels. Shipping
  stems with an entirely invented or entirely blank option set is not the cheap
  case, so this is one deliberate pass away rather than a bolt-on. The wording
  is in this same workbook's header rows, which is where a later pass starts.

HEADER. The workbook has a two-row header: row 1 holds the section prompt once
per section (merged across its columns), row 2 the per-item stem. Read with
`header=1` and the section recovered by forward-filling row 1.

Seven study-authored sections ship as one table each (the project is RECOMS
ESR8; nothing here is a published third-party instrument, so no rights block
applies):

  use_types      27 items, 0/1   "I use the site for ..." multi-select
  attachment     26 items, 1-5   place attachment, identity and knowledge
  landscape      11 items, 1-5   "... because it has/provides ..."
  management     12 items, 1-5   management and protection attitudes
  trust          11 items, 1-5   trust in the managing agency
  fairness        6 items, 1-5   fairness of decision-making
  knowledge      12 items, 1-5   whose knowledge counts

The 27 `use_types` items are a check-all-that-apply block, so each is a genuine
binary item rather than one categorical question -- two response categories
belong in core, not nominal (BATCH_LOG 2026-08-26).

COVARIATES. `K Your gender` arrives dummy-expanded over six columns; the index
of whichever is 1 is recovered into one `cov_gender` (BATCH_LOG 2026-08-26 --
"demographics deposited as regression dummies are recoverable"), with no row
set taken as the omitted/undisclosed category. Year of birth is kept as a year,
not a birthdate, and one impossible value (46) is dropped to missing. The
single free-text column ("Other Open text answers") is NOT shipped -- an open
text field is where a name or a place of residence turns up.
"""
import os

import numpy as np
import pandas as pd

RAW = os.environ.get(
    "HAKKARAINEN_RAW",
    "/tmp/claude-1000/-home-ben-Dropbox-projects-irw-src-automated-finding/"
    "5eef9b18-8b21-4d62-a15f-a632f0def6f5/scratchpad/bC/raw/zenodo.5243244/"
    "RECOMS_ESR8_worldheritage_database.xlsx")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "automated_finding", "irw_output")

# Column index ranges, from the workbook's own section rows.
SECTIONS = {
    "use_types":  (range(1, 28), {0, 1}),
    "attachment": (range(29, 55), {1, 2, 3, 4, 5}),
    "landscape":  (range(55, 66), {1, 2, 3, 4, 5}),
    "management": (range(66, 78), {1, 2, 3, 4, 5}),
    "trust":      (range(78, 89), {1, 2, 3, 4, 5}),
    "fairness":   (range(90, 96), {1, 2, 3, 4, 5}),
    "knowledge":  (range(96, 108), {1, 2, 3, 4, 5}),
}
GENDER_COLS = range(109, 115)
GENDER_LABELS = ["Woman", "Man", "Female trans-person", "Male trans-person",
                 "Prefer not to say", "Other"]


def main():
    d = pd.read_excel(RAW, header=1)
    print(f"read {d.shape[0]} rows x {d.shape[1]} cols")
    ncol = d.shape[1]

    accounted = set()
    for cols, _ in SECTIONS.values():
        accounted |= set(cols)
    accounted |= set(GENDER_COLS)
    named = {0: "cov_country", 89: "cov_trust_level", 108: "cov_birth_year",
             115: "cov_life_situation", 116: "cov_education"}
    accounted |= set(named)
    print("  skip col 28 'Other Open text answers': free text, not shipped")
    accounted.add(28)
    unaccounted = [i for i in range(ncol) if i not in accounted]
    for i in unaccounted:
        print(f"  UNACCOUNTED col {i}: {d.columns[i]!r}")
    assert not unaccounted, f"{len(unaccounted)} column(s) unaccounted for"

    base = pd.DataFrame({"id": np.arange(1, len(d) + 1)})
    for i, name in named.items():
        base[name] = d.iloc[:, i].values
    # Birth year: a year is a legitimate covariate; 46 is not a year.
    by = pd.to_numeric(base["cov_birth_year"], errors="coerce")
    bad = int(((by < 1900) | (by > 2010)).sum())
    print(f"  cov_birth_year: {bad} impossible value(s) set to missing")
    base["cov_birth_year"] = by.where((by >= 1900) & (by <= 2010))
    # Gender dummies -> one label.
    g = d.iloc[:, list(GENDER_COLS)].apply(pd.to_numeric, errors="coerce")
    idx = g.values.argmax(axis=1)
    any1 = (g.values == 1).any(axis=1)
    base["cov_gender"] = [GENDER_LABELS[j] if ok else np.nan
                          for j, ok in zip(idx, any1)]
    print(f"  cov_gender recovered from {len(GENDER_LABELS)} dummy columns; "
          f"{int((~any1).sum())} row(s) had none set")

    os.makedirs(OUT, exist_ok=True)
    covs = [c for c in base.columns if c.startswith("cov_")]
    written = set()
    for name, (cols, scale) in SECTIONS.items():
        block = d.iloc[:, list(cols)].apply(pd.to_numeric, errors="coerce")
        block.columns = [f"{name}_{k + 1}" for k in range(block.shape[1])]
        wide = pd.concat([base, block], axis=1)
        long = wide.melt(id_vars=["id"] + covs, value_vars=list(block.columns),
                         var_name="item", value_name="resp").dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        for it, grp in long.groupby("item"):
            b = set(grp["resp"].unique()) - scale
            assert not b, f"{name}/{it}: {sorted(b)} outside {sorted(scale)}"
        assert long["id"].nunique() >= 100 and long["item"].nunique() > 1
        table = f"hakkarainen_2021_{name}"
        assert table not in written
        written.add(table)
        long[["id", "item", "resp"] + covs].to_csv(
            os.path.join(OUT, f"{table}.csv"), index=False)
        print(f"  {table}: {long['id'].nunique()} ids x "
              f"{long['item'].nunique()} items = {len(long)} responses")


if __name__ == "__main__":
    main()
