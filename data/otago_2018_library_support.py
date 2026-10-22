"""
How 564 postgraduate students at the University of Otago would most like the
University Library to support them: eight support formats, each rated 1 (most
preferred) to 5 (least preferred), from a 2018 review of academic support
services run by the Library's Research Support Unit.

Source: Research Support Unit Library, University of Otago (2018).
        Postgraduate Support at Otago: Student Questionnaire Answers.
        figshare.
DOI: 10.6084/m9.figshare.7464938.v1
Data: https://figshare.com/articles/dataset/_/7464938 --
        "2018 Student Questionnaire Data_Tidy_Final.csv", with
        "Transcript of questions asked.docx" as the deposit's own
        questionnaire
License: CC BY 4.0 (verified on the figshare record, license.name
        "CC BY 4.0")
Item text: shipped. The deposit's own "Transcript of questions asked.docx" is
        the questionnaire as fielded, and it numbers the eight Q22 options
        (1)-(8) against exactly the Q22_1..Q22_8 column names in the data, so
        code and wording are tied by the source. instrument: the stems match
        no published scale (searched verbatim); they are the Research Support
        Unit's own list of Library support formats, written for this review.
        rights: study-authored, under the deposit's own CC BY 4.0.

Q22 is worded as a ranking -- "rank with 1 being the most preferred and 5 the
least preferred" -- but it was fielded as a Qualtrics matrix of eight rows
against five columns, which cannot be a ranking of eight things. The responses
confirm it functioned as a RATING: only 7 of 386 respondents used each value
at most once, while 437 repeated some value three or more times. So the eight
rows are eight independent 1-5 preference ratings, not an ipsative ranking,
and `resp` is the rating as given. 1 is the preferred end for every item, so
the direction is consistent within and across items and nothing is recoded.

Only Q22 ships. The questionnaire's other closed blocks are below the 3-item
floor on their own and are on their own formats: Q13 is two items on a
very-easy..very-difficult scale, Q23 two items on a more-than-once-a-week..
never scale. Everything else is a single multi-select "select all that apply"
checklist (Q10, Q11, Q12, Q24), a single-answer pick (Q15, Q25), a demographic,
or a free-text box.

`id` is the row index. The deposit's file carries no respondent identifier at
all -- not a platform ID, not a case number -- so the row is the only handle
there is, and it links a respondent's eight ratings to their own covariates.

PII: none. 37 of the 39 columns are text, and five of them are free-text
comment boxes (Q9, Q16, Q29, Q32, Q35) plus six "Other (please state)"
follow-ups. A values-level scan for email addresses and phone numbers across
all 37 found nothing. None of the free text is carried into the output in any
case: the output is id/item/resp plus closed-category covariates. The coarsest
geography in the file is "distance or on-campus".

Output: one table.
  otago_2018_library_support  8 items, 1-5, 386 ids, 3014 responses
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path("2018 Student Questionnaire Data_Tidy_Final.csv")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

TABLE = "otago_2018_library_support"
ITEMS = [f"Q22_{i}" for i in range(1, 9)]

# "1 (most preferred)" .. "5 (least preferred)", verbatim from the data.
SCALE = {"1 (most preferred)": 1, "2": 2, "3": 3, "4": 4,
         "5 (least preferred)": 5}

COV_MAP = {"Q1": "cov_division",
           "Q2": "cov_degree",
           "Q3": "cov_degree_stage",
           "Q34": "cov_enrolment",
           "Q4": "cov_study_mode",
           "Q6": "cov_student_origin",
           "Q31": "cov_ethnic_group"}

# Below the 3-item floor and each on its own response format.
SHORT_BLOCKS = {
    "Q13_1": "one of two items on a very-easy..very-difficult scale "
             "(learn about PG academic support) -- two items is below the "
             "3-item floor",
    "Q13_2": "one of two items on a very-easy..very-difficult scale (use PG "
             "academic support) -- below the 3-item floor",
    "Q23_1": "one of two items on a more-than-once-a-week..never scale (seek "
             "Library assistance) -- below the 3-item floor",
    "Q23_2": "one of two items on a more-than-once-a-week..never scale "
             "(contact Subject Librarian) -- below the 3-item floor",
}

SINGLE_QUESTIONS = {
    "Q10": "one multi-select 'select all you are aware of' checklist over 15 "
           "support areas -- one question's options, not an item battery",
    "Q11": "one multi-select 'select all you use' checklist, same 15 options",
    "Q12": "one multi-select 'most effective ways to inform PG students' "
           "checklist over 11 options",
    "Q15": "single-answer pick of the most effective way to inform students",
    "Q24": "one multi-select 'main reasons you do not use Library support' "
           "checklist over 9 options",
    "Q25": "single-answer pick of the most significant barrier",
}

FREE_TEXT = {
    "Q9": "free-text: list the academic support activities you can think of",
    "Q16": "free-text: what would help postgraduates find and use support",
    "Q29": "free-text: what would make Library support easier to find/use",
    "Q32": "free-text: your ideal Library academic support service",
    "Q35": "free-text: other ways the Library can support you",
}


def pii_screen(df: pd.DataFrame) -> None:
    """Values-level scan over every text column, with the denominator printed."""
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} text column(s) of "
          f"{len(df.columns)}")
    assert len(text_cols) > 0, "screen selected no columns"
    pat = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\b\d{3}[ -]?\d{3}[ -]?\d{4}\b")
    hits = {c: [v for v in df[c].dropna().astype(str) if pat.search(v)]
            for c in text_cols}
    hits = {c: v for c, v in hits.items() if v}
    print(f"  email/phone-shaped values found in {len(hits)} column(s): "
          f"{sorted(hits)}")
    assert not hits, f"PII-shaped values: {sorted(hits)}"


def main() -> None:
    df = pd.read_csv(SRC)
    print("raw shape", df.shape)
    pii_screen(df)

    for c in ITEMS:
        assert c in df.columns, c
        bad = set(df[c].dropna().unique()) - set(SCALE)
        assert not bad, (c, bad)

    out = pd.DataFrame({"id": range(1, len(df) + 1)})
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        out[dst] = df[src].values
    covs = list(COV_MAP.values())

    # A ranking would use each value at most once; this does not.
    num = df[ITEMS].replace(SCALE)
    answered = num.notna().any(axis=1)
    strict = num[answered].apply(
        lambda r: r.dropna().duplicated().sum() == 0, axis=1)
    print(f"  of {int(answered.sum())} respondents who answered Q22, "
          f"{int(strict.sum())} used each value at most once and "
          f"{int((~strict).sum())} repeated a value -- a rating, not a ranking")
    assert strict.sum() < 0.1 * answered.sum(), \
        "Q22 looks like a genuine ranking after all; reconsider shipping it"

    other_text = [c for c in df.columns if c.endswith("_TEXT")]
    skipped = dict(SHORT_BLOCKS)
    skipped.update(SINGLE_QUESTIONS)
    skipped.update(FREE_TEXT)
    skipped.update({c: "free-text 'Other (please state)' follow-up to "
                       f"{c.split('_')[0]}" for c in other_text})
    skipped["Q36"] = ("the participant information and consent block, not a "
                      "question") if "Q36" in df.columns else None
    skipped = {k: v for k, v in skipped.items() if v is not None}
    used = set(COV_MAP) | set(ITEMS)
    leftover = [c for c in df.columns if c not in used | set(skipped)]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in sorted(skipped.items()):
        print(f"  skipped column {c}: {why}")

    wide = pd.concat([out, num], axis=1)
    long = wide.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    long = long.dropna(subset=["resp"]).copy()
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
    assert long["id"].nunique() >= 100, long["id"].nunique()
    assert long["item"].nunique() == 8

    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (TABLE, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {TABLE} {c.name}: {c.detail[:180]}")
    long.to_csv(OUT / f"{TABLE}.csv", index=False)
    print(f"{TABLE}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
