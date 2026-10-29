"""
Local community attitudes to, and satisfaction with, dams: 31 items answered by
316 respondents.

Source: Soressa, T. (2024). Local Community's Satisfaction, Attitude and
        Mitigation Measures Towards Dams [Dataset]. Harvard Dataverse.
DOI: 10.7910/DVN/2BD1HP
Data: https://doi.org/10.7910/DVN/2BD1HP ("Survey data", downloaded with
        format=original, which returns the original SPSS .sav -- the `.tab`
        name is Dataverse's lossy conversion and is not what this reads)
License: CC0 1.0 (verified on the Dataverse record's licence block)
Item text: SHIPPED. Every one of the 31 variables carries a variable label that
        IS its full English wording ("Improves living utilities infrastructure
        (supply of water, electric, and telephone, etc.)", "Lose of grazing and
        agricultural land") and value labels giving all five anchors, identical
        across the 31. The items are the study's own -- they are dam-specific
        and match no published instrument -- so the deposit's CC0 is the
        wording's licence and there is no third-party instrument in play.

ONE table. The nine prefixes are the instrument's own dimensions, not nine
instruments: positive economic/social/land impacts (`PE`, `PS`, `PL`), negative
economic/social/land impacts (`NE`, `NS`, `NL`), service satisfaction (`CDam`),
personal and community benefit (`IPDam`, `CPDam`). Same respondents, one
administration, one 1-5 strongly-disagree-to-strongly-agree scale throughout.
The item codes keep the source names, so a user who wants the dimensions can
take them from the prefix.

**The permitted response set is documented, not inferred.** Observed values
differ by block -- the positive-impact items run 1-4 and the negative-impact
items 3-5 -- which is a real response pattern (this community agrees with the
harms and disagrees with the benefits), not two scales. The value labels define
1-5 for every item, so that complete set goes to `run_qc` as `permitted_values`
rather than letting the observed ranges be read as evidence about the
instrument.

`run_qc` still warns `resp_scale_mixed` ("1-3 (5 items), 1-4 (16 items), 3-5
(10 items)") and `multi_scale` on the seven prefixes. Both are the two
paragraphs above in warning form: one documented 1-5 scale answered in opposite
directions by the benefit and the harm blocks of one instrument.

No covariates: the deposit is 31 item columns and nothing else -- no
demographics, no identifier, no computed scores.

PII: none. Every column is numeric, there is no identifier, name, date,
free-text or geographic column, and the screen below prints its denominator.

Output: one table, 9,796 responses -- 316 respondents x 31 items, 1-5.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Survey data.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

TABLE = "soressa_2024_dam_attitudes"
PERMITTED = [1, 2, 3, 4, 5]


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"


def main() -> None:
    df, meta = pyreadstat.read_sav(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 316, len(df)
    assert len(df.columns) == 31, len(df.columns)

    # Both label levels complete, and one shared anchor set: that is what makes
    # the item text a cheap data_labels extraction, so it is asserted here
    # rather than assumed by the generator.
    labels = {c: (meta.column_names_to_labels.get(c) or "").strip()
              for c in df.columns}
    assert all(labels.values()), [c for c, v in labels.items() if not v]
    assert len(set(labels.values())) == 31, "two items share a label"
    anchors = {tuple(sorted(meta.variable_value_labels.get(c, {}).items()))
               for c in df.columns}
    assert len(anchors) == 1 and len(next(iter(anchors))) == 5, anchors
    print(f"all 31 items carry their full English wording and the same five "
          f"anchors: {[v for _k, v in sorted(next(iter(anchors)))]}")

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    codes = {c: c.lower() for c in df.columns if c != "id"}
    assert len(set(codes.values())) == 31, codes

    long = df[["id"] + list(codes)].rename(columns=codes)
    long = long.melt(id_vars=["id"], var_name="item", value_name="resp")
    before = long["resp"].notna().sum()
    long = long[long["resp"].isin(PERMITTED)]
    assert before == len(long), \
        f"{before - len(long)} cell(s) outside {PERMITTED}"
    print("no covariates: the deposit is 31 item columns and nothing else")

    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"]].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=PERMITTED)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (TABLE, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {TABLE} {c.name}: {c.detail[:200]}")
    long.to_csv(OUT / f"{TABLE}.csv", index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
