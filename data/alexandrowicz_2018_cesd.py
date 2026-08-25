"""Alexandrowicz (2018), PLOS ONE -- dimensionality of the CES-D.

Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0197908
DOI: 10.1371/journal.pone.0197908
Data: S2 File (journal.pone.0197908.s002)
License: CC BY 4.0

An Austrian general-population sample answering the 20-item Center for
Epidemiologic Studies Depression Scale (CES-D), used in the paper to fit
multi-dimensional multi-level Rasch models.

Why this needed a hand
----------------------
The pipeline's triage recorded this candidate as "Could not confidently
identify item columns", because the S2 File is R `write.table()` output:
space-separated, every label quoted, and the row names written as an unnamed
leading column, so a comma-delimited read collapses the whole file into one
column. Re-read with whitespace separation it is a clean 518 x 22 matrix.

Table written
-------------
alexandrowicz_2018_cesd   20 CES-D items, resp 0-3, 518 respondents

Coding notes
------------
* The CES-D response scale is the standard 0 ("rarely or none of the time,
  less than 1 day") to 3 ("most or all of the time, 5-7 days") frequency
  scale; 0-3 is exactly the range present in the file, on every item.
* Items 4, 8, 12 and 16 are the positively-worded ones and carry an `r` in
  their source column name (`cesr04`, `cesr08`, `cesr12`, `cesr16`). They are
  exported as stored, without further transformation, so the file matches the
  scoring the authors modelled. Source column names are kept as the `item`
  labels so item text can join back to them.
* The unnamed leading column is the R row name (1..518), used as `id`.
* `alter_neu` is age in years (fractional -- it is a computed age at survey
  date, not a typed integer) and `sex` is 1/2; both are carried as covariates.
"""

import os
import pandas as pd

RAW = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0197908.s002"
OUTDIR = "irw_output"

ITEMS = [f"ces_{i:02d}" for i in (1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19, 20)]
ITEMS += [f"cesr{i:02d}" for i in (4, 8, 12, 16)]


def main():
    # index_col=0 picks up the unnamed row-name column R wrote out.
    d = pd.read_csv(RAW, sep=r"\s+", quotechar='"', index_col=0)
    d.index.name = "id"
    d = d.reset_index()

    items = [c for c in d.columns if c.startswith("ces")]
    assert sorted(items) == sorted(ITEMS), sorted(set(items) ^ set(ITEMS))

    long = d.melt(id_vars=["id", "sex", "alter_neu"], value_vars=items,
                  var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    long = long.rename(columns={"sex": "cov_sex", "alter_neu": "cov_age"})
    long = long[["id", "item", "resp", "cov_sex", "cov_age"]]

    # The CES-D frequency scale is 0-3 on every item; anything else would be a
    # sentinel or a coding error, so fail loudly rather than ship it.
    assert long["resp"].between(0, 3).all()
    assert long.groupby("item")["resp"].nunique().min() > 1, "constant item"
    assert not long.duplicated(["id", "item"]).any()

    os.makedirs(OUTDIR, exist_ok=True)
    path = os.path.join(OUTDIR, "alexandrowicz_2018_cesd.csv")
    long.to_csv(path, index=False)
    print(f"{path}: {long['id'].nunique()} ids x {long['item'].nunique()} items "
          f"= {len(long)} responses, resp {long['resp'].min()}-{long['resp'].max()}, "
          f"density {len(long)/(long['id'].nunique()*long['item'].nunique()):.3f}")


if __name__ == "__main__":
    main()
