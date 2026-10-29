"""
Big Five personality and attitudes towards artificial intelligence in 272
Pakistani university students.

Source: Batool, A., & Khan, A. (2024). SPSS data file and output file for study
        "Relationship Between Big Five Personality Traits and Attitudes Towards
        Artificial Intelligence" [Dataset]. Zenodo.
DOI: 10.5281/zenodo.13760224
Data: https://zenodo.org/records/13760224 ("SPSS file with raw data.sav")
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id
        "cc-by-4.0")
Item text: NOT shipped, and neither is an open question -- both instruments are
        already ruled on. Extraction would be cheap: all 77 variables carry a
        variable label that IS the item's wording ("Is talkative", "Tends to
        find fault with others") and 68 carry value labels giving every anchor.
        But the BFI-44 (John, Donahue & Kentle 1991) is registered **block**
        (2026-09-11, irw#1945 reserve-a-right test: "I hold the copyright to
        the BFI and it is not in the public domain per se"), and the GAAIS
        (Schepman & Rodway 2020) is registered **hold** (2026-10-18, #3077: no
        originator clause quotable). So the wording stays where it is; if
        either ruling changes, this file is all that is needed.

THE RESPONSES ARE UN-REVERSED BACK TO RAW AGREEMENT, and that is the one
substantive decision in this script.

The deposit ships 15 of the 44 BFI items and 8 of the 20 GAAIS items under an
`R_` prefix, already reverse-scored -- `R_BFI_6_E` is "Is reserved" and
correlates **+0.333** with the rest of the extraversion block, which only
happens if the stored value has been flipped. Confirmed independently: the
deposit's own subscale scores (`BFI_O/E/A/N/C`, `GAAIS_P/N`) equal the mean of
these stored columns to four decimal places, so the stored values are exactly
what the depositor averaged.

Shipping that as-is would put two opposite response directions in one table --
5 meaning "agree strongly" on 32 BFI items and "disagree strongly" on the other
12 -- which is the `resp_ambiguous` defect (#1827). Of the two ways to make the
table consistent, un-reversing is the faithful one: it reconstructs what the
respondent actually endorsed, it is exact (`6 - x` on a 1-5 scale), and the
`R_` prefix names precisely which columns to undo. So every item here is
agreement with the statement as worded, one direction throughout, and 5 always
means "agree strongly". Item keying (that agreeing with "Is reserved" scores
LOW on extraversion) is a scoring fact about the instrument, not a property of
the response scale, and belongs to whoever scores it.

**The deposit missed one reversal, and this script does not inherit the error.**
The BFI-44 has sixteen reverse-keyed items. This deposit flipped **fifteen**.
`BFI_31_E` is the sixteenth, and it is "Is sometimes shy, inhibited" -- a reverse-keyed extraversion item
whose two siblings of the same polarity, "Is reserved" (item 6) and "Tends to be
quiet" (item 21), both carry the `R_` prefix. Item 31 does not. It is also the
only one of the eight extraversion items whose corrected item-total correlation
is NEGATIVE (-0.355), flipping to +0.355 if reversed. So it was left raw while
its siblings were flipped, and the depositor's own `BFI_E` score -- which this
file reproduces exactly -- carries that through. Under the raw-agreement
convention above this needs no special handling at all: item 31 is already raw,
so it is simply not touched, and it ends up consistent with everything else for
the first time. The script asserts the diagnosis rather than trusting it.

**Three isolated out-of-range cells are dropped.** `R_BFI_27_A`, `GAAIS_7_P` and
`GAAIS_18_P` each hold exactly ONE response coded 6 on a scale the value labels
define as 1-5. One cell in one item is a data-entry error, not a sixth category
(the real extremes are used hundreds of times), and the depositor summed them --
which is why their subscale means differ from the recomputed ones in the fourth
decimal place while the other five match exactly.

Each instrument is ONE table. The BFI's five factors and the GAAIS's positive
and negative subscales are subscales of one instrument on one response format,
administered in one sitting; the item codes keep the source names, so the
factor letter (`_e`, `_a`, `_c`, `_n`, `_o`) and the GAAIS valence (`_p`, `_n`)
are readable off every row for anyone who wants to split them. The one part of
the source name NOT kept is the `R_` prefix: it records a scoring state this
script has undone, so keeping it would assert something false about the shipped
value. Stripping it leaves `bfi_6_e`, which means "BFI item 6, extraversion"
and is true either way, and it is reversible -- the source file says which
numbers carried the prefix.

PII: none. Every column is numeric, there is no name, email, date of birth,
identifier or geographic column, and the screen below prints its denominator.
`ID` is a 1..272 serial and is replaced by the row index anyway.

Output: two tables, 17,405 responses.
  * batool_2024_big_five      -- 44 items, resp 1-5 (raw agreement)
  * batool_2024_ai_attitudes  -- 20 items, resp 1-5 (raw agreement)
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("SPSS file with raw data.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

BLOCKS = {
    "batool_2024_big_five": (re.compile(r"^(R_)?BFI_\d+_[EACNO]$"), 44),
    "batool_2024_ai_attitudes": (re.compile(r"^(R_)?GAAIS_\d+_[PN]$"), 20),
}

PERMITTED = [1, 2, 3, 4, 5]
SCALE_MAX = 5                      # so the un-reversal is (MAX + 1) - x

COV_MAP = {
    "Age": "cov_age",
    "Gender": "cov_gender",
    "University": "cov_university_type",
    "Education": "cov_year_of_study",
    "Major": "cov_major",
}

DROP = {
    "ID": "the deposit's own 1..272 serial, replaced by the row index",
    "BFI_O": "depositor-computed openness subscale mean",
    "BFI_E": "depositor-computed extraversion subscale mean -- and it carries "
        "the missed reversal of BFI_31_E, see the module docstring",
    "BFI_A": "depositor-computed agreeableness subscale mean",
    "BFI_N": "depositor-computed neuroticism subscale mean",
    "BFI_C": "depositor-computed conscientiousness subscale mean",
    "GAAIS_P": "depositor-computed positive-attitude subscale mean",
    "GAAIS_N": "depositor-computed negative-attitude subscale mean",
}

# The missed reversal, asserted below rather than assumed.
MISSED = "BFI_31_E"
MISSED_LABEL = "Is sometimes shy, inhibited"
MISSED_SIBLINGS = ["R_BFI_6_E", "R_BFI_21_E"]


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}; dtypes present: "
          f"{sorted({str(t) for t in df.dtypes})}")
    assert len(df.columns) > 0
    assert not text_cols, f"unexpected text column(s): {text_cols}"


def corrected_r(frame: pd.DataFrame, col: str) -> float:
    """Correlation of one item with the sum of the others in its block."""
    rest = frame.drop(columns=[col]).sum(axis=1)
    return frame[col].corr(rest)


def main() -> None:
    df, meta = pyreadstat.read_sav(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 272, len(df)

    labelled = sum(1 for c in df.columns
                   if (meta.column_names_to_labels.get(c) or "").strip())
    print(f"variable labels present: {labelled} of {len(df.columns)}; "
          f"value-labelled variables: {len(meta.variable_value_labels)} -- "
          "item text is cheap and is blocked/held by register ruling, not "
          "missing")

    cols = {t: [c for c in df.columns if pat.match(c)]
            for t, (pat, _n) in BLOCKS.items()}
    for t, (_pat, n) in BLOCKS.items():
        assert len(cols[t]) == n, (t, len(cols[t]), n)

    # Out-of-range cells: isolated, so data-entry errors rather than a category.
    for t, cs in cols.items():
        bad = {c: int((df[c] > SCALE_MAX).sum()) for c in cs
               if (df[c] > SCALE_MAX).any()}
        for c, k in bad.items():
            assert k == 1, (c, k, "more than one out-of-range cell -- re-check "
                                  "whether this is really a data-entry error")
            print(f"dropping {k} out-of-range cell in {c} "
                  f"(value {sorted(set(df[c][df[c] > SCALE_MAX]))}, on a "
                  f"documented 1-{SCALE_MAX} scale)")

    # The missed reversal, established before anything is written.
    assert meta.column_names_to_labels[MISSED] == MISSED_LABEL, \
        meta.column_names_to_labels[MISSED]
    e_cols = [c for c in cols["batool_2024_big_five"] if c.endswith("_E")]
    e_frame = df[e_cols].where(df[e_cols] <= SCALE_MAX)
    r_missed = corrected_r(e_frame, MISSED)
    assert r_missed < 0, r_missed
    for sib in MISSED_SIBLINGS:
        assert corrected_r(e_frame, sib) > 0, sib
    print(f"{MISSED} ({MISSED_LABEL!r}): corrected item-total r = "
          f"{r_missed:.3f}, negative, while its same-polarity siblings "
          f"{MISSED_SIBLINGS} are positive -- the deposit reverse-scored them "
          f"and missed this one. Under the raw-agreement convention it needs no "
          f"handling: it is already raw.")

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    accounted = (set(COV_MAP) | set(covs) | set(DROP) | {"id"}
                 | {c for cs in cols.values() for c in cs})
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in DROP.items():
        print(f"skipped column {c}: {why}")

    for table, cs in cols.items():
        block = df[cs].where(df[cs].isin(PERMITTED))
        reversed_cols = [c for c in cs if c.startswith("R_")]
        # Un-reverse back to raw agreement. Exact on a 1-5 scale.
        block[reversed_cols] = (SCALE_MAX + 1) - block[reversed_cols]
        print(f"{table}: un-reversed {len(reversed_cols)} of {len(cs)} "
              f"column(s) back to raw agreement ({SCALE_MAX + 1} - x)")
        # The `R_` prefix records a scoring state this script has just
        # UNDONE, so carrying it into the item code would assert something
        # false. It is stripped, which leaves the code meaning exactly "BFI
        # item N, factor X" / "GAAIS item N, valence X" -- true whatever the
        # scoring. Reversible: the prefix is restored by looking the number up
        # in the source file.
        codes = {c: re.sub(r"^r_", "", c.lower()) for c in cs}
        assert len(set(codes.values())) == len(cs), codes
        long = pd.concat([df[["id"] + covs], block.rename(columns=codes)],
                         axis=1)
        long = long.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
        long = long.dropna(subset=["resp"])
        write(long, table, covs)


def write(long: pd.DataFrame, table: str, covs: list) -> None:
    long = long.copy()
    assert not (long["resp"] % 1 != 0).any(), "fractional resp values"
    long["resp"] = long["resp"].astype(int)
    assert set(long["resp"].unique()) <= set(PERMITTED), \
        sorted(long["resp"].unique())
    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:200]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
