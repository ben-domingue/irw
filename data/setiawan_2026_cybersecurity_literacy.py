"""
Cybersecurity literacy of 233 in-service Indonesian schoolteachers in Riau and
West Java, measured at three levels across the same nine security focus areas:
what they understand (knowledge), what they hold to be unethical conduct
(ethics), and what they report doing (behaviour). Every focus area appears in
all three subscales, so a content domain is measured three times over.

Source: Setiawan, Y., Abdullah, A. G., & Salam, H. (2026). Cybersecurity
        literacy of Indonesian schoolteachers: a 60-item, three-dimension
        questionnaire dataset (N = 233) [Data set]. Mendeley Data.
DOI: 10.17632/8mvkw9kjvp
Data: https://data.mendeley.com/datasets/8mvkw9kjvp --
        CSLE_teacher_dataset_233.csv, with CSLE_codebook.csv and
        CSLE_instrument_ID-EN.csv as the deposit's own codebook and
        instrument, and README.md
License: CC BY 4.0 (verified on the Mendeley record's data_licence and
        restated in the deposit's own README)
Item text: shipped, all three tables, from CSLE_instrument_ID-EN.csv, which
        gives every item in the administered Indonesian and in the authors'
        English translation and NAMES the data column (`variable`) beside
        each -- so code and wording are tied by the source itself, not by
        position. instrument: the stems match no published scale (ET01
        searched verbatim; the deposit's README states a purpose-built
        instrument and no canonical cybersecurity-literacy scale was
        located); rights: study-authored, under the deposit's own CC BY 4.0.

The triage read CSLE_codebook.csv -- one of the two documentation files --
rather than the data, which is why this landed in worth_retrying with
"2 column(s) look like text-coded Likert items (e.g. ['subscale',
'focus_area'])". Those are the codebook's own columns. The data file was never
opened.

PII: none. The depositors removed the names and email addresses the Google
Form collected before processing, `participant_id` is a sequential P001-P233
with no link to that export, and the coarsest geography is one of two
provinces. Two re-identification guards the depositors applied are visible in
the codebook and are preserved here as they stand: two Banten respondents are
recoded to West Java, and four respondents with unique multi-subject
combinations to "Multiple subjects".

Anchor direction, which the README puts in bold and is the thing to get right:
the three blocks do NOT run the same way. Knowledge is 1 = strongly disagree
.. 5 = strongly agree (higher = more), ETHICS IS REVERSE-ANCHORED at 1 =
strongly agree .. 4 = strongly disagree (lower = stronger ethical
endorsement), and behaviour is 1 = never .. 4 = always. The ethics block is
shipped exactly as administered and is NOT reflected -- `resp` keeps a
consistent direction within each item, and recoding would silently disagree
with every published analysis of the deposit. The direction is recorded in the
item text's option_text instead, where it belongs.

`itemcov_focus_area` carries the item's security domain (one of nine), which
the instrument file supplies per item. It is a property of the probe, not of
the respondent, hence the `itemcov_` prefix.

Output: three tables, one per subscale. They are not one scale -- two
different response formats and three different anchor directions.
  setiawan_2026_cybersecurity_knowledge  20 items, 1-5, 233 ids
  setiawan_2026_cybersecurity_ethics     20 items, 1-4, 233 ids (reversed)
  setiawan_2026_cybersecurity_behaviour  20 items, 1-4, 233 ids
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("CSLE_teacher_dataset_233.csv")
INSTR = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("CSLE_instrument_ID-EN.csv")
OUT = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

BLOCKS = [
    ("knowledge", "KN", 20, (1, 5)),
    ("ethics",    "ET", 20, (1, 4)),
    ("behaviour", "BH", 20, (1, 4)),
]

COV_MAP = {
    "sex": "cov_sex",
    "marital_status": "cov_marital_status",
    "highest_qualification": "cov_highest_qualification",
    "school_level": "cov_school_level",
    "subject_taught": "cov_subject_taught",
    "school_location": "cov_school_location",
    "home_location": "cov_home_location",
    "school_management": "cov_school_management",
    "province": "cov_province",
    "ict_training": "cov_ict_training",
    "ict_training_level": "cov_ict_training_level",
    "cyber_training": "cov_cyber_training",
    "cyber_training_provider": "cov_cyber_training_provider",
    "school_wifi": "cov_school_wifi",
}

COMPOSITES = {
    "CSK_mean": "mean of the 20 knowledge items -- a composite, not a response",
    "CSE_mean_raw": "mean of the 20 ethics items -- a composite",
    "CSE_mean_reflected": "mean of 5 - ET, i.e. a recoded composite",
    "CSB_mean": "mean of the 20 behaviour items -- a composite",
}

# Per-person data-quality indicators the depositors derived FROM the responses
# and supplied so users can screen for themselves. They are not background
# covariates, and nothing is lost by leaving them out: each is exactly
# recomputable from the responses shipped here -- longstring_X is "all twenty
# X items identical", anchor_flag is "raw ethics mean >= 3.5". The script
# verifies both reconstructions before dropping them.
QUALITY = {
    "anchor_flag": "depositor-derived flag: raw ethics mean >= 3.5, for 14 "
                   "respondents whose ethics block looks answered in the "
                   "preceding block's direction",
    "longstring_ET": "depositor-derived flag: all 20 ethics items identical",
    "longstring_KN": "depositor-derived flag: all 20 knowledge items identical",
    "longstring_BH": "depositor-derived flag: all 20 behaviour items identical",
}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} text column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0, "nothing to screen"
    expected = {"participant_id"} | set(COV_MAP)
    assert set(text_cols) == expected, sorted(set(text_cols) ^ expected)
    assert df["participant_id"].str.fullmatch(r"P\d{3}").all(), \
        "participant_id is not the deposit's sequential P001-P233 form"
    # Nothing free-text: every one of the 13 remaining text columns is a
    # closed demographic category, enumerated in CSLE_codebook.csv.
    for c in COV_MAP:
        assert df[c].nunique() <= 10, (c, df[c].nunique())


def verify_quality_flags(df: pd.DataFrame, items: dict) -> None:
    """The dropped indicators are recomputable -- show it, don't assert it."""
    for block, prefix in (("ET", "ET"), ("KN", "KN"), ("BH", "BH")):
        cols = items[prefix]
        recomputed = (df[cols].nunique(axis=1) == 1).astype(int)
        agree = (recomputed == df[f"longstring_{block}"]).all()
        print(f"  longstring_{block} recomputed from the shipped items: "
              f"{'identical' if agree else 'DIFFERS'} "
              f"({int(recomputed.sum())} respondents)")
        assert agree, f"longstring_{block} is not recomputable"
    recomputed = (df[items["ET"]].mean(axis=1) >= 3.5).astype(int)
    agree = (recomputed == df["anchor_flag"]).all()
    print(f"  anchor_flag recomputed from the shipped items: "
          f"{'identical' if agree else 'DIFFERS'} "
          f"({int(recomputed.sum())} respondents)")
    assert agree, "anchor_flag is not recomputable"


def main() -> None:
    df = pd.read_csv(DATA)
    print("raw shape", df.shape)
    pii_screen(df)

    instr = pd.read_csv(INSTR)
    assert len(instr) == 60, len(instr)
    focus = dict(zip(instr["variable"], instr["focus_area"]))

    items = {prefix: [f"{prefix}{i:02d}" for i in range(1, n + 1)]
             for _, prefix, n, _ in BLOCKS}
    all_items = [c for cols in items.values() for c in cols]
    for c in all_items:
        assert c in df.columns, c
        assert c in focus, f"{c} is not in the instrument file"

    verify_quality_flags(df, items)

    assert df["participant_id"].is_unique, "participant_id repeats"
    assert len(df) == 233, len(df)
    out = pd.DataFrame({"id": df["participant_id"]})
    for src, dst in COV_MAP.items():
        out[dst] = df[src]
    covs = list(COV_MAP.values())

    skipped = dict(COMPOSITES)
    skipped.update({c: f"{why} -- exactly recomputable from the shipped "
                       "responses, verified above"
                    for c, why in QUALITY.items()})
    used = {"participant_id"} | set(COV_MAP) | set(all_items)
    leftover = [c for c in df.columns if c not in used | set(skipped)]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in skipped.items():
        print(f"  skipped column {c}: {why}")

    wide = pd.concat([out, df[all_items]], axis=1)
    for name, prefix, _, (lo, hi) in BLOCKS:
        cols = items[prefix]
        long = wide[["id"] + covs + cols].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).copy()
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(lo, hi).all(), \
            (name, sorted(long["resp"].unique()))
        long["itemcov_focus_area"] = long["item"].map(focus)
        assert long["itemcov_focus_area"].notna().all()
        order = ["id", "item", "resp", "itemcov_focus_area"] + covs
        long = long[order].sort_values(["id", "item"])
        table = f"setiawan_2026_cybersecurity_{name}"
        assert long["id"].nunique() >= 100 and long["item"].nunique() >= 3
        checks = run_qc(long)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (table, fails)
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")
        long.to_csv(OUT / f"{table}.csv", index=False)
        print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
