"""
Nine self-report instruments from a 250-respondent online study testing
whether intolerance of uncertainty, family accommodation and reassurance
seeking serially mediate the relationship between attachment anxiety and OCD
checking symptoms. Not every respondent reached every instrument -- the
questionnaire was long and partly conditional -- so the per-table N runs from
149 to 206.

Source: Cassidy, Dorothy; Freeston, Mark (2024). Test Hypothesised Mediation
        Model Data - specifically, investigating whether intolerance of
        uncertainty, family accommodation, and reassurance seeking, are
        multiple serial mediators in the relationship between attachment
        anxiety and OCD checking symptoms. Newcastle University.
DOI: 10.25405/data.ncl.27335709.v1
Data: https://outputs.ncl.ac.uk/articles/dataset/_/27335709 --
        "Uncertainty_Attachment_Consented_Eligible 07.24.sav" (250 x 232),
        with README.txt
License: CC BY-NC 4.0 (verified on the figshare record for article 27335709,
        license.name "CC BY-NC 4.0"). NC proceeds per datastandard.md's
        "Before you start"; the restriction propagates into Derived_License
        rather than disappearing.
Item text: NOT shipped, and the extraction itself would be trivially cheap --
        the .sav's own variable labels ARE the item stems, verbatim and
        complete, for all 177 item columns ("I'm afraid that I will lose my
        partner's love.", "Unforeseen events upset me greatly."). RIGHTS is
        what holds it, for nine published instruments at once: the IUS-12's
        family carries a `block` verdict in
        itemtext/instrument_rights_register.csv (2026-10-15 counsel ruling),
        and the ECR-R, OCI-R, PSWQ, FAS, RSS and ReSQ have no register row at
        all, which under the same ruling is a hold rather than a clearance.
        Nine rulings is not a cheap-gate extraction, so it is named as a
        ruling request in automated_finding/TODO.md. The wording is in the
        .sav itself and needs no re-finding: `pyreadstat.read_sav(...)` then
        `meta.column_names_to_labels`.

This deposit arrived as `aggregate_continuous` -- "resp has >50 unique values
after wide-to-long melt" -- twice over, once via figshare and once via
DataCite for the same article. It is not aggregate: the melt pooled 175 item
columns across nine instruments on five different response scales plus the
numeric age and country-code columns, and >50 distinct values is what that
pooling produces. Each block separately is a clean 4-, 5-, 6- or 7-point
ordinal scale.

PII: none, and the depositors de-identified before depositing rather than
leaving it to the reader. Every free-text field in the file -- `Gender_7_TEXT`,
`Ethnicity_`, `Relationship_years`, `Disability__1_TEXT`, `ReSQ_Who`,
`Proficiency_test_1_TEXT` -- holds the literal string "data removed", as do
`ResponseId`, `id` and `ID_Num`. The screen below asserts that rather than
trusting it. `Nationality` is a country code (25 countries over 170
respondents) and is kept: a nationality is standard survey demography, not the
block-to-county locating the 2026-10-20 geographic ruling is about.

`id` is the row index. The source's three identifier columns were already
blanked by the depositors, so there is nothing else to use.

Output: nine tables, one per instrument. Their response formats differ (1-7,
1-6, 1-5) and they measure different constructs, so they are not one scale.
  cassidy_2024_ecr_r         36 items, 1-7, 201 ids, 7179 responses
  cassidy_2024_rss           30 items, 1-5, 203 ids, 6085 responses
  cassidy_2024_oci_r         23 items, 1-5, 206 ids, 4729 responses
  cassidy_2024_ab            23 items, 1-5, 172 ids, 3953 responses
  cassidy_2024_resq_int      16 items, 1-5, 202 ids, 3219 responses
  cassidy_2024_fas           19 items, 1-5, 149 ids, 2702 responses
  cassidy_2024_ius_12        12 items, 1-5, 203 ids, 2436 responses
  cassidy_2024_resq_cons     11 items, 1-6, 199 ids, 2171 responses
  cassidy_2024_pswq3          3 items, 1-5, 181 ids,  543 responses
Skipped: PHQ-2 and GAD-2, two items each, below the 3-item floor.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else \
    Path("Uncertainty_Attachment_Consented_Eligible 07.24.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

# prefix -> (table suffix, n_items, permitted range)
BLOCKS = {
    "ECR": ("ecr_r", 36, (1, 7)),
    "IUS_12": ("ius_12", 12, (1, 5)),
    "ReSQ_Int": ("resq_int", 16, (1, 5)),
    "ReSQ_Cons": ("resq_cons", 11, (1, 6)),
    "RSS": ("rss", 30, (1, 5)),
    "OCI_R": ("oci_r", 23, (1, 5)),
    "FAS": ("fas", 19, (1, 5)),
    "AB": ("ab", 23, (1, 5)),
    "PSWQ3": ("pswq3", 3, (1, 5)),
}
BELOW_FLOOR = {"PHQ_2_": 2, "GAD_2": 2}
ITEM_RE = re.compile(
    r"^(ECR|IUS_12|ReSQ_Int|ReSQ_Cons|RSS|OCI_R|PHQ_2_|GAD_2|FAS|AB|PSWQ3)"
    r"_(\d+)$")

COV_MAP = {"Age": "cov_age",
           "Gender": "cov_gender",
           "Language": "cov_english_first_language",
           "Nationality": "cov_nationality",
           "Ethnicity": "cov_ethnicity",
           "Education_achieve": "cov_education",
           "Relationship_status": "cov_relationship_status",
           "OCD_": "cov_ocd_experience",
           "Anxiety_": "cov_anxiety_experience",
           "Disability_": "cov_disability",
           "Survey_access": "cov_survey_access"}

REDACTED = ["Gender_7_TEXT", "Ethnicity_", "Relationship_years",
            "Disability__1_TEXT", "Disability__2_TEXT", "ReSQ_Who",
            "Proficiency_test_1_TEXT", "ResponseId", "id", "ID_Num"]


def pii_screen(df: pd.DataFrame) -> None:
    """Assert the depositors' redaction rather than trusting the README."""
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} text column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(text_cols) > 0, "screen selected no columns"
    for c in REDACTED:
        assert c in df.columns, c
        vals = {str(v).strip() for v in df[c].dropna().unique()} - {""}
        assert vals <= {"data removed", '"Removed"'}, (c, sorted(vals)[:5])
    print(f"  all {len(REDACTED)} free-text and identifier columns hold only "
          "the depositors' redaction placeholder")
    other = [c for c in text_cols
             if c not in REDACTED and c not in ("DistributionChannel",
                                                "UserLanguage")]
    assert not other, f"unscreened text column(s): {other}"


def main() -> None:
    import pyreadstat
    df, meta = pyreadstat.read_sav(str(SRC), apply_value_formats=False)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 250, len(df)

    items: dict[str, list[str]] = {}
    for c in df.columns:
        m = ITEM_RE.match(c)
        if m:
            items.setdefault(m.group(1), []).append(c)
    for prefix, (_, n, _) in BLOCKS.items():
        got = items.get(prefix, [])
        assert len(got) == n, (prefix, len(got), n)
    for prefix, n in BELOW_FLOOR.items():
        assert len(items.get(prefix, [])) == n, prefix

    # Every item column carries its own stem as a variable label. Not shipped
    # (see the header), but assert it is there so the "in hand" claim in the
    # provenance row is checked rather than remembered.
    unlabelled = [c for cols in items.values() for c in cols
                  if not (meta.column_names_to_labels.get(c) or "").strip()]
    assert not unlabelled, f"item columns with no variable label: {unlabelled}"
    print(f"  all {sum(len(v) for v in items.values())} item columns carry a "
          "variable label holding the item stem (not shipped -- rights)")

    out = pd.DataFrame({"id": range(1, len(df) + 1)})
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        out[dst] = df[src].values
    covs = list(COV_MAP.values())

    all_items = [c for cols in items.values() for c in cols]
    used = set(COV_MAP) | set(all_items)
    skipped: dict[str, str] = {
        c: "free-text or identifier column, redacted to 'data removed' by "
           "the depositors" for c in REDACTED}
    for c in df.columns:
        if c in used or c in skipped:
            continue
        if c.startswith("Consent_Form"):
            skipped[c] = "consent checkbox, constant 1 for every respondent"
        elif c.startswith("Occupation_"):
            skipped[c] = ("one option of a multi-select 'select all that "
                          "apply' occupation question -- several can be 1 at "
                          "once, so it cannot be collapsed to a single "
                          "category")
        elif c.startswith("Ethnicity."):
            skipped[c] = ("conditional ethnicity follow-up, empty for every "
                          "respondent")
        elif c in BELOW_FLOOR or ITEM_RE.match(c):
            skipped[c] = (f"one of {BELOW_FLOOR.get(ITEM_RE.match(c).group(1), 2)} "
                          "items in a block below the 3-item floor")
        else:
            skipped[c] = {
                "StartDate": "survey timestamp",
                "EndDate": "survey timestamp",
                "RecordedDate": "survey timestamp",
                "DistributionChannel": "Qualtrics link type (anonymous / qr)",
                "UserLanguage": "constant 'EN'",
                "Education": "conditional follow-up answered by 20 of 250",
                "Proficiency_test": "conditional follow-up answered by 7 of 250",
                "ReSQ_Trust": "single trust rating for the respondent's main "
                              "source of reassurance -- one item, below the "
                              "3-item floor",
                "FAS___target": "which relative the FAS items refer to; one "
                                "selection, not a response",
                "RealParticipant": "fraud-screening flag",
                "OverrideFraud": "fraud-screening override flag",
                "Consort": "CONSORT flow stage",
                "Consented_Eligible": "constant 1 -- the file is already "
                                      "filtered to consented, eligible cases",
            }.get(c, "UNCLASSIFIED")
    unclassified = [c for c, why in skipped.items() if why == "UNCLASSIFIED"]
    assert not unclassified, f"unaccounted source columns: {unclassified}"
    for c, why in sorted(skipped.items()):
        print(f"  skipped column {c}: {why}")

    wide = pd.concat([out, df[all_items]], axis=1)
    order = sorted(BLOCKS, key=lambda p: -BLOCKS[p][1])
    for prefix in order:
        suffix, _, (lo, hi) = BLOCKS[prefix]
        cols = items[prefix]
        long = wide[["id"] + covs + cols].melt(
            id_vars=["id"] + covs, var_name="item", value_name="resp")
        long = long.dropna(subset=["resp"]).copy()
        assert not (long["resp"] % 1 != 0).any(), f"{prefix}: fractional resp"
        long["resp"] = long["resp"].astype(int)
        assert long["resp"].between(lo, hi).all(), \
            (prefix, sorted(long["resp"].unique()))
        long = long[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        table = f"cassidy_2024_{suffix}"
        assert long["id"].nunique() >= 100, (table, long["id"].nunique())
        assert long["item"].nunique() >= 3, table
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
