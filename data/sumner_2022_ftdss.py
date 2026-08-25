"""Sumner et al. (2022), PLOS ONE -- Revised Formal Thought Disorder Self-report Scale.

Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0278841
DOI: 10.1371/journal.pone.0278841
Data: S1 Dataset (journal.pone.0278841.s002)
License: CC BY 4.0

934 respondents across four recruitment samples, each completing the same
six self-report instruments. The paper assesses the dimensionality of the
Revised Formal Thought Disorder Self-report Scale (FTD-SS); the other five
instruments were administered alongside it for convergent validity.

Why this needed a hand
----------------------
Two separate reasons the automated pass could not use this candidate:
1. The triage picked the article's *first* tabular-looking Supporting
   Information file, `.s001`, which is captioned as a dataset but is
   actually a Word document. The real data is `.s002`.
2. `.s002` is tab-delimited with a `.csv` name, so a comma-delimited read
   returns a single column and the item columns are unidentifiable.

Tables written
--------------
sumner_2022_ftdss        29 FTD-SS items,                     1-4
sumner_2022_olife       104 O-LIFE items,                     1-2
sumner_2022_spq          74 Schizotypal Personality Q. items,  1-2
sumner_2022_asi          29 Aberrant Salience Inventory items, 1-2
sumner_2022_lshs         16 Launay-Slade Hallucination items,  1-5
sumner_2022_ipip_neo     48 IPIP-NEO N/E facet items,          1-5

Coding notes
------------
* The four samples answered identical instruments with identical response
  options, so each instrument ships as one file with a `cov_study` column
  rather than as four files (see the IRW convention on collapsing
  same-instrument samples).
* O-LIFE, the SPQ and the ASI are the yes/no instruments; the file stores
  them as 1/2, which is kept as stored rather than recoded to 0/1 so the
  exported values match the source exactly.
* The FTD-SS was administered in a fixed order to some respondents and a
  randomised order to others. That is a property of the administration, not
  of the item, so it is carried as `cov_item_order` on the FTD-SS table only.
* Every derived column is excluded: the scale and subscale totals
  (`Total TD Score`, `* Scale Score`) and the per-instrument
  `nItemsMissing_*` counts.
* Source item labels ("FTD-SS Item 1", ...) are kept verbatim so item text
  can join back to them.
"""

import os
import re
import pandas as pd

RAW = "https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0278841.s002"
OUTDIR = "irw_output"

# prefix in the source header -> (output table suffix, expected item count,
#                                 expected response range)
SCALES = {
    "FTD-SS": ("ftdss",    29, (1, 4)),
    "OLIFE":  ("olife",   104, (1, 2)),
    "SPQ":    ("spq",      74, (1, 2)),
    "ASI":    ("asi",      29, (1, 2)),
    "LSHS":   ("lshs",     16, (1, 5)),
    "IPIP":   ("ipip_neo", 48, (1, 5)),
}


def main():
    d = pd.read_csv(RAW, sep="\t")
    d = d.rename(columns={"'ID'": "id"}).copy()
    d["cov_study"] = d["Sample Type"]
    d["cov_item_order"] = d["FTD-SS Item Order"]
    assert d["id"].is_unique

    os.makedirs(OUTDIR, exist_ok=True)
    for prefix, (suffix, n_expected, (lo, hi)) in SCALES.items():
        items = [c for c in d.columns
                 if re.match(rf"^{re.escape(prefix)} Item \d+", c)]
        assert len(items) == n_expected, (prefix, len(items))

        covs = ["cov_study"] + (["cov_item_order"] if prefix == "FTD-SS" else [])
        long = d.melt(id_vars=["id"] + covs, value_vars=items,
                      var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"])
        long["resp"] = long["resp"].astype(int)
        long = long[["id", "item", "resp"] + covs]

        assert long["resp"].between(lo, hi).all(), (
            prefix, long["resp"].min(), long["resp"].max())
        assert long.groupby("item")["resp"].nunique().min() > 1, f"{prefix}: constant item"
        assert not long.duplicated(["id", "item"]).any()

        path = os.path.join(OUTDIR, f"sumner_2022_{suffix}.csv")
        long.to_csv(path, index=False)
        n_id, n_it = long["id"].nunique(), long["item"].nunique()
        print(f"{path}: {n_id} ids x {n_it} items = {len(long)} responses, "
              f"resp {long['resp'].min()}-{long['resp'].max()}, "
              f"density {len(long)/(n_id*n_it):.3f}")


if __name__ == "__main__":
    main()
