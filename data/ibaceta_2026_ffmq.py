"""
Dispositional mindfulness, mind-wandering, emotion regulation and
psychological well-being in 474 Chilean students (279 secondary, 195
university): five instruments, 139 items.

Source: Ibaceta, M. (2026). Mindfully distracted: How emotional dysregulation
        and mind wandering content relate to mindfulness and psychological
        well-being [Dataset]. Zenodo. The deposit's own description:
        "de-identified data for a cross-sectional study of dispositional
        mindfulness, mind-wandering, emotional regulation and psychological
        well-being in 474 students: 279 secondary-school students and 195
        university students."
DOI: 10.5281/zenodo.23498072
Data: https://zenodo.org/records/23498072 ("Data Sharable.xlsx", sheet "Data",
        with the codebook in its "Coding" sheet)
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id
        "cc-by-4.0")
Item text: NOT shipped -- the codebook maps structure, not wording. Every one
        of the 139 items is mapped to its instrument, its facet, its item
        number within that instrument and its reverse-coding rule, but the
        item WORDING is nowhere in the deposit, and all five instruments are
        published third-party scales (so a `ship` would need a register ruling
        on each). What the codebook does give is shipped as `itemcov_facet`,
        see below. Where the wording is: each instrument's own source --
        Baer et al.'s FFMQ, Gratz & Roemer's DERS, Ryff's scales, the
        Daydreaming Frequency Scale from Singer & Antrobus's Imaginal Processes
        Inventory -- plus whichever Spanish adaptations were administered,
        which the deposit does not name.

**This deposit's "Coding" sheet is the best codebook in the batch, and two
things follow from it.**

1. **The stored values are RAW responses, not scored ones.** The sheet has a
   `reverse_before_scoring` column (Yes for 40 of the 141 rows) and a
   `transformation` column spelling out `6 - raw response` or `7 - raw
   response`. A transformation to be applied *before scoring* is a transformation
   that has NOT been applied to the file, which is exactly the opposite of the
   `batool_2024_*` deposit earlier in this batch, where the reversals had
   already been baked in and had to be undone to stop `resp` carrying two
   directions. Here nothing needs undoing: `resp` is the respondent's own
   answer throughout and the reversal is the scorer's job. The script asserts
   the two transformation strings are the only ones present, so a change in the
   deposit's convention would fail loudly rather than silently invert 40 items.

2. **The facet mapping ships as `itemcov_facet`.** The codebook assigns every
   item to a named facet -- the FFMQ's five (observing, describing, acting with
   awareness, nonjudging, nonreactivity), the DERS's five, Ryff's six, positive
   vs negative mind-wandering -- and that is an item-level covariate in
   `datastandard.md`'s sense. Carrying it means a user gets the subscale
   structure without having to re-find the deposit's codebook, which is the
   whole point of the column.

Five tables, because these are five separate published instruments on three
different response scales (1-5, 1-4, 1-6), not subscales of one battery.

`cov_school_level` is the deposit's `Level`, whose codebook entry reads
"university = Level - 1": so 2 is university and 1 secondary school, matching
the described 195 and 279.

Two instruments ship a subset of their own numbering, which the item codes
preserve rather than renumber: the mind-wandering block runs 3, 4, 7, 8 ... 39
(26 of a longer form) and Ryff's omits 10 and 34 (37 items). Renumbering those
to 1..n would destroy the only link back to the source instrument's item
numbers.

PII: none, and the deposit says its data are de-identified. The screen below
prints its denominator; `participant_id` is a P0001..P0474 study serial and is
replaced by the row index.

Output: five tables, 64,981 responses.
  * ibaceta_2026_ffmq           -- 39 items, resp 1-5
  * ibaceta_2026_ryff_wellbeing -- 37 items, resp 1-6
  * ibaceta_2026_mind_wandering -- 26 items, resp 1-4
  * ibaceta_2026_ders           -- 25 items, resp 1-5
  * ibaceta_2026_daydreaming    -- 12 items, resp 1-5
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Data Sharable.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

# The codebook's own instrument names -> (output table, permitted response set).
# The permitted sets come from the instruments and are corroborated by the
# codebook's reverse transformations: `6 - raw` implies 1-5, `7 - raw` 1-6.
INSTRUMENTS = {
    "Five Facet Mindfulness Questionnaire": ("ibaceta_2026_ffmq",
                                             [1, 2, 3, 4, 5]),
    "Ryff psychological well-being": ("ibaceta_2026_ryff_wellbeing",
                                      [1, 2, 3, 4, 5, 6]),
    "Mind wandering content": ("ibaceta_2026_mind_wandering", [1, 2, 3, 4]),
    "Difficulties in Emotion Regulation Scale": ("ibaceta_2026_ders",
                                                 [1, 2, 3, 4, 5]),
    "Daydreaming Frequency Scale": ("ibaceta_2026_daydreaming",
                                    [1, 2, 3, 4, 5]),
}

# The only transformations the codebook may contain. A new one means the
# deposit's convention changed and the raw-response assumption needs rechecking.
KNOWN_TRANSFORMS = {"6 - raw response", "7 - raw response",
                    "university = Level - 1"}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    assert text_cols == ["participant_id"], text_cols
    serial = df["participant_id"].astype(str)
    assert serial.str.fullmatch(r"P\d{4}").all(), \
        sorted(set(serial[~serial.str.fullmatch(r'P\d{4}')]))[:5]
    print("the one text column is participant_id, every value of the form "
          "P0000 -- a study serial, replaced by the row index")


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="Data")
    cb = pd.read_excel(SRC, sheet_name="Coding")
    cb.columns = [str(c).strip() for c in cb.columns]
    print("raw shape", df.shape, "| codebook", cb.shape)
    pii_screen(df)
    assert len(df) == 474, len(df)

    # The raw-response claim, asserted rather than assumed.
    transforms = set(cb["transformation"].dropna())
    unknown = transforms - KNOWN_TRANSFORMS
    assert not unknown, f"new transformation(s) in the codebook: {unknown}"
    n_rev = int((cb["reverse_before_scoring"] == "Yes").sum())
    print(f"codebook: {n_rev} item(s) flagged reverse_before_scoring, with "
          f"transformations {sorted(transforms - {'university = Level - 1'})} "
          "-- 'before scoring' means NOT applied to the file, so these are raw "
          "responses and nothing needs un-reversing")

    cb = cb.dropna(subset=["instrument"])
    cb = cb[cb["instrument"].isin(INSTRUMENTS)]
    assert set(cb["instrument"]) == set(INSTRUMENTS), set(cb["instrument"])

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    df["cov_school_level"] = df["Level"]
    covs = ["cov_school_level"]

    mapped = set(cb["variable"])
    accounted = mapped | {"participant_id", "Level", "id", "cov_school_level"}
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    print("skipped column participant_id: a P0001..P0474 study serial, "
          "replaced by the row index")
    print("skipped column Level: ships as cov_school_level (the codebook's "
          "'university = Level - 1', so 2 = university, 1 = secondary)")

    for inst, (table, permitted) in INSTRUMENTS.items():
        rows = cb[cb["instrument"] == inst]
        cols = [c for c in rows["variable"]]
        assert all(c in df.columns for c in cols), (table, cols)
        facet = dict(zip(rows["variable"], rows["facet"]))
        assert all(isinstance(v, str) and v.strip() for v in facet.values())
        codes = {c: c.lower() for c in cols}
        assert len(set(codes.values())) == len(cols), codes

        long = df[["id"] + covs + cols].rename(columns=codes)
        long = long.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
        long["itemcov_facet"] = long["item"].map(
            {c.lower(): facet[c] for c in cols})
        assert long["itemcov_facet"].notna().all()
        before = long["resp"].notna().sum()
        long = long[long["resp"].isin(permitted)]
        assert before == len(long), \
            f"{table}: {before - len(long)} cell(s) outside {permitted}"
        nums = sorted(int(n) for n in rows["item_number"])
        print(f"{table}: {len(cols)} items, source numbering "
              f"{nums[0]}..{nums[-1]}"
              + (" (a subset -- codes keep the source numbers)"
                 if nums != list(range(1, len(nums) + 1)) else "")
              + f", facets {sorted(set(facet.values()))}")
        write(long, table, covs, permitted)


def write(long: pd.DataFrame, table: str, covs: list, permitted: list) -> None:
    long = long.copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs + ["itemcov_facet"]].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=permitted)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"  -> rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
