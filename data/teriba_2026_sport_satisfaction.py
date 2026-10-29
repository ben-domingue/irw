"""
Six instruments administered to 263 US collegiate athletes: sport satisfaction,
WHO-5 well-being, grit, implicit theories of intelligence, emotion regulation
and self-compassion.

Source: Teriba, A. (2026). Psychological Well-Being and Sport Satisfaction
        [Dataset]. Harvard Dataverse. The deposit's own description: "This data
        supports the publication Psychological Well-Being and Sport
        Satisfaction in Collegiate Athletes: The Role of Upbringing, Athletic
        Status, and Adaptive Psychological Attributes".
DOI: 10.7910/DVN/IQSSOU
Data: https://doi.org/10.7910/DVN/IQSSOU ("Dataverse - Well-Being and Sport
        Satisfaction.tab", downloaded with format=original, which returns the
        original SPSS .sav -- the `.tab` name is Dataverse's converted copy and
        is not what this reads)
License: CC0 1.0 (verified on the Dataverse record's licence block)
Item text: ONE of the six ships; the other five are decided by rulings already
        in itemtext/instrument_rights_register.csv, so nothing here is an open
        question except the sport-satisfaction block. Extraction is cheap for
        all six -- every one of the 102 variables carries a variable label that
        IS its full item wording, and all 102 carry value labels giving every
        response anchor:
          * self-compassion -- SHIPPED. The SCS-SF (Raes, Pommier, Neff & Van
            Gucht 2011) is registered `ship`.
          * WHO-5 well-being -- register `block`.
          * grit (Grit-S, Duckworth & Quinn 2009) -- register `block`.
          * emotion regulation (ERQ, Gross & John 2003) -- register `block`.
          * implicit theories of intelligence (Dweck's ITIS) -- register
            `hold`.
          * sport satisfaction -- NO register row, and silence does not ship
            (ben-domingue 2026-10-15). A row is owed; the 16 items read as an
            athlete-satisfaction questionnaire but which published instrument
            was not established.

The mindset block is ONE table, not two. `Fixed1..4` and `Growth1..4` are the
two poles of Dweck's Implicit Theories of Intelligence Scale, administered
together on one 1-6 agree/disagree scale; splitting them would turn one
instrument into two four-item tables and lose the fixed/growth contrast the
scale exists to measure. The item codes keep the source names, so the pole is
still readable off every row.

Geographic and checkbox columns are dropped, each for a stated reason. `Q7`
("Which state is your school in?") is a US state over 263 respondents, i.e. a
geographic code, and goes in no form under the 2026-10-20 ruling. `Q16_1..32`
is a 32-sport "choose all that apply" grid coded 1/blank (two sports have zero
selections), and `Q15_1/Q15_2` the same shape for scholarship type: these are
checkbox grids rather than a measured battery, and reading blank as "not
selected" would be an assumption about missingness, so they are left out.

PII: none. Every column is numeric, there is no name, email, date of birth,
identifier or free-text column, and the screen below prints its denominator.

Output: six tables, 14,471 responses.
  * teriba_2026_sport_satisfaction   -- 16 items, resp 1-7
  * teriba_2026_emotion_regulation   -- 10 items, resp 1-7
  * teriba_2026_self_compassion      -- 12 items, resp 1-5
  * teriba_2026_grit                 --  8 items, resp 1-5
  * teriba_2026_mindset_intelligence --  8 items, resp 1-6
  * teriba_2026_wellbeing_who5       --  5 items, resp 1-6
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import pyreadstat

SRC = (Path(sys.argv[1]) if len(sys.argv) > 1
       else Path("Dataverse - Well-Being and Sport Satisfaction.sav"))
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

BLOCKS = {
    "teriba_2026_sport_satisfaction": (
        [f"Sport_Satisfaction_{i}" for i in range(1, 17)], [1, 2, 3, 4, 5, 6, 7]),
    "teriba_2026_emotion_regulation": (
        [f"EmRegulation{i}" for i in range(1, 11)], [1, 2, 3, 4, 5, 6, 7]),
    "teriba_2026_self_compassion": (
        [f"Self_compassion_{i}" for i in range(1, 13)], [1, 2, 3, 4, 5]),
    "teriba_2026_grit": ([f"Grit{i}" for i in range(1, 9)], [1, 2, 3, 4, 5]),
    "teriba_2026_mindset_intelligence": (
        [f"Fixed{i}" for i in range(1, 5)] + [f"Growth{i}" for i in range(1, 5)],
        [1, 2, 3, 4, 5, 6]),
    "teriba_2026_wellbeing_who5": (
        [f"Well_Being_{i}" for i in range(1, 6)], [1, 2, 3, 4, 5, 6]),
}

COV_MAP = {
    "Q1": "cov_age_band",
    "Q2": "cov_gender",
    "Q3": "cov_race_ethnicity",
    "Q6": "cov_community_type",
    "Q8": "cov_school_type",
    "Q11": "cov_college_year",
    "Q13": "cov_ever_athletic_scholarship",
    "Q14": "cov_current_athletic_scholarship",
}

DROP = {
    "Q7": "'Which state is your school in?' -- a US state over 263 "
        "respondents, i.e. a geographic code, dropped in no form under the "
        "2026-10-20 ruling",
    "Q15_1": "a 'choose all that apply' checkbox coded 1/blank (scholarship "
        "type: full)",
    "Q15_2": "the same checkbox for scholarship type: partial",
}


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
    assert len(df) == 263, len(df)

    labelled = sum(1 for c in df.columns
                   if (meta.column_names_to_labels.get(c) or "").strip())
    print(f"variable labels present: {labelled} of {len(df.columns)}; "
          f"value-labelled variables: {len(meta.variable_value_labels)}")
    assert labelled == len(df.columns)

    sports = [f"Q16_{i}" for i in range(1, 33)]
    assert all(c in df.columns for c in sports)

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    accounted = (set(COV_MAP) | set(covs) | set(DROP) | set(sports) | {"id"}
                 | {c for cols, _p in BLOCKS.values() for c in cols})
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in DROP.items():
        print(f"skipped column {c}: {why}")
    print(f"skipped {len(sports)} Q16_* column(s): a 32-sport 'choose all that "
          "apply' grid coded 1/blank (two sports have zero selections), which "
          "is a checkbox grid rather than a measured battery -- reading blank "
          "as 'not selected' would be an assumption about missingness")

    for table, (cols, permitted) in BLOCKS.items():
        assert all(c in df.columns for c in cols), (table, cols)
        codes = {c: c.lower() for c in cols}
        assert len(set(codes.values())) == len(cols), codes
        long = df[["id"] + covs + cols].rename(columns=codes)
        long = long.melt(id_vars=["id"] + covs, var_name="item",
                         value_name="resp")
        before = long["resp"].notna().sum()
        long = long[long["resp"].isin(permitted)]
        if before != len(long):
            print(f"{table}: dropped {before - len(long)} cell(s) of {before} "
                  f"outside {permitted}")
        write(long, table, covs)


def write(long: pd.DataFrame, table: str, covs: list) -> None:
    long = long.copy()
    long["resp"] = long["resp"].astype(int)
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
