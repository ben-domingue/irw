"""
Work engagement and mindfulness, answered by 429 Turkish healthcare workers --
TWO of the deposit's four instruments, because the other two cannot be told
apart item by item.

Source: Karahan Kaplan, M., Bozkurt, G., Aksu, B. C., Bozkurt, S., Gunsel, A.,
        & Gencer Celik, G. (2024). Do emotional demands and exhaustion affect
        work engagement? The mediating role of mindfulness. Frontiers in
        Psychology, 15, 1432328.
DOI: 10.3389/fpsyg.2024.1432328
Data: https://doi.org/10.3389/fpsyg.2024.1432328.s001 (Data_Sheet_1; the
        triage flagged this `recoverable_format`)
License: CC BY 4.0 (verified on the Crossref record for the article, license
        URL creativecommons.org/licenses/by/4.0/; the supplementary data sheet
        carries the article's licence)
Item text: NOT shipped, although every item's FULL TURKISH STEM is the column
        header -- this file needs no label level because the wording IS the
        header ("Isimi yaparken kendimi cok enerjik hissederim."). Two
        different reasons:
          * the 9 engagement items are the Utrecht Work Engagement Scale,
            registered `block`;
          * the mindfulness instrument is NOT CONFIRMED. The article describes
            a 12-item scale with attention, awareness, present-focus and
            acceptance facets -- which matches the CAMS-R (Feldman et al.
            2007) on both the facet structure and the item count -- but the
            article never names it, and no register row is written on a
            resemblance. Identifying it is the one step between this file's Turkish
            wording and an item text table.
        The stems are recorded in `itemtext_provenance.csv` either way, so
        whoever resolves those two questions does not have to re-extract them.

**Two of the four instruments do not ship, and the reason is an ORDER that
cannot be recovered rather than a count that does not add up.** The file holds
34 Likert columns, and the article's Measures section gives exactly 34 items
across four instruments: work engagement 9, emotional exhaustion 7, emotional
demands 6, mindfulness 12. The totals reconcile; what does not is which of the
two middle instruments comes first in the file.

  * columns 0-8 are the UWES-9 item for item (energetic, strong, enthusiasm,
    inspiration, pride, happy working intensely, immersed, carried away), and
    the count agrees at 9. SHIPPED.
  * columns 22-33 are twelve mindfulness items by content -- focusing on what
    one is doing, tolerating distress, accepting what cannot be changed,
    noticing one's feelings without judging them -- and the count agrees at
    12. SHIPPED.
  * columns 9-21 are the thirteen emotional-exhaustion and emotional-demands
    items, which the article splits 7 and 6. The file's block order is NOT the
    article's presentation order (the article introduces emotional demands
    first, the file starts with engagement), so there is no basis for assuming
    the exhaustion seven come before the demands six, and the content does not
    settle it either: "working with patients all day is really demanding" and
    "working with patients puts me under a lot of stress" read as demands but
    sit among items that read as exhaustion. NOT SHIPPED. Any split would
    either cut one instrument in half or put two instruments in one table, and
    `datastandard.md` asks for one file per scale. What would unlock it is
    specific and recorded: the article's measurement-model table (absent from
    the HTML full text fetched on 2026-10-29, which carries no item codes or
    factor loadings) or a word from the authors.

That is 13 items x 429 respondents left on the table, deliberately, and the
docstring says so rather than letting the gap look like an oversight.

**resp is 1-6, and the article says 5-point.** All 34 Likert columns hold
exactly the six values 1-6, with no scale change anywhere in the file, while
the article's Measures section describes "the 5-point Likert-style measures".
The file is what was administered and the file is what ships; the discrepancy
is recorded because it is also a caution about leaning on that article -- its
item counts are used above to assign two blocks, and they reconcile exactly
with the file's 34 columns, but its description of the response format does
not.

**Covariates are the deposit's own bands, kept as strings.** Age arrives as
"18-25".."50+" and tenure as "0-5 yil".."21+ yil"; they are banded in the
source and are not re-coded into invented midpoints.

PII: none. The five demographic columns are closed categories (sex, age band,
education level, marital status, tenure band) and there is no identifier
(`id` is the row index), name, date, free-text or geographic column. The screen
below prints its denominator.

Output: two tables, 9,009 responses -- 429 respondents, 21 items.
  * karahan_kaplan_2024_mindfulness     -- 12 items, resp 1-6
  * karahan_kaplan_2024_uwes9           --  9 items, resp 1-6
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Data_Sheet_1.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

PERMITTED = [1, 2, 3, 4, 5, 6]
N_LIKERT = 34

# table -> (column slice, item code prefix). The slices are the deposit's own
# column order; the assertions below check the block really starts where this
# says before anything is written.
BLOCKS = {
    "karahan_kaplan_2024_uwes9": (slice(0, 9), "uwes"),
    "karahan_kaplan_2024_mindfulness": (slice(22, 34), "mind"),
}
# Columns 9-21: see the module docstring. Not shipped, and the count is
# asserted so that a change in the file is noticed rather than absorbed.
UNASSIGNED = slice(9, 22)

COV_SLICE = slice(34, 39)
COV_NAMES = ["cov_sex", "cov_age_band", "cov_education", "cov_marital_status",
             "cov_tenure_band"]

# A stem from each block, to check the file has not been reordered.
ANCHOR_STEMS = {
    0: "enerjik",
    8: "kendimden",
    9: "soğuduğumu",
    21: "üzüldüğüm",
    22: "odaklanmak",
    33: "dikkatimi",
}


def pii_screen(df: pd.DataFrame, cov_cols: list) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}")
    assert len(df.columns) > 0
    # Every text column must be one of the five demographic bands, and each
    # must be a closed category rather than free text.
    assert set(text_cols) <= set(cov_cols), \
        f"text outside the demographics: {set(text_cols) - set(cov_cols)}"
    for c in text_cols:
        k = df[c].nunique()
        assert k <= 10, f"{c} has {k} distinct values -- check for free text"
        print(f"  {str(c)[:44]!r}: {k} closed categories")


def main() -> None:
    df = pd.read_excel(SRC)
    print("raw shape", df.shape)
    assert len(df) == 429, len(df)
    cols = list(df.columns)
    assert len(cols) == 39, len(cols)

    # The blocks are identified by position, so position is verified.
    for i, needle in ANCHOR_STEMS.items():
        assert needle.lower() in str(cols[i]).lower(), \
            f"column {i} is {cols[i]!r}, expected to contain {needle!r}"
    print(f"column order verified at {len(ANCHOR_STEMS)} anchor stems")

    likert = cols[:N_LIKERT]
    for c in likert:
        vals = sorted(int(v) for v in df[c].dropna().unique())
        assert set(vals) <= set(PERMITTED), (c, vals)
    cov_cols = cols[COV_SLICE]
    assert len(cov_cols) == len(COV_NAMES), cov_cols
    pii_screen(df, cov_cols)

    unassigned = cols[UNASSIGNED]
    assert len(unassigned) == 13, len(unassigned)
    print(f"NOT SHIPPING {len(unassigned)} column(s) -- the emotional-demands "
          "and exhaustion items. The article splits those two instruments 7 "
          "and 6; the boundary cannot be located item by item, and a guess "
          "would either halve one instrument or merge two. First and last: "
          f"{str(unassigned[0])[:46]!r} .. {str(unassigned[-1])[:46]!r}")

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in zip(cov_cols, COV_NAMES):
        df[dst] = df[src]

    accounted = set(likert) | set(cov_cols) | set(COV_NAMES) | {"id"}
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"

    for table, (sl, prefix) in BLOCKS.items():
        write(df, table, cols[sl], prefix)


def write(df: pd.DataFrame, table: str, cols: list, prefix: str) -> None:
    # The item code is the prefix plus the item's position in its own block,
    # which is the deposit's administration order. The full Turkish stem of
    # each is recorded in itemtext_provenance.csv against this code.
    codes = {c: f"{prefix}{i}" for i, c in enumerate(cols, start=1)}
    long = df[["id"] + COV_NAMES + cols].rename(columns=codes)
    long = long.melt(id_vars=["id"] + COV_NAMES, var_name="item",
                     value_name="resp")
    before = long["resp"].notna().sum()
    long = long[long["resp"].isin(PERMITTED)]
    assert before == len(long), \
        f"{table}: {before - len(long)} cell(s) outside {PERMITTED}"

    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + COV_NAMES].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=PERMITTED)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
