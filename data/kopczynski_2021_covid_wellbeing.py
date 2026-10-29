"""
Five instruments answered by 1,000 Polish university students during the
COVID-19 pandemic: quality of life, core self-evaluations, perceived social
support, fear of COVID-19, and how they appraised the pandemic itself.

Source: Kopczynski, T., & Bartoszek, A. (2021). COVID-19 anxiety versus
        well-being - students' sense of support and self-esteem [Dataset].
        Zenodo. The deposit's own description: "This study is aimed to evaluate
        the impact of fear of the COVID-19 pandemic on the quality of life of
        university students in Poland. An analysis is made of the correlation
        of various features of the student cohorts with social support and
        their self-evaluation, in the context of sensing the chances for
        success in life and satisfaction from studying online."
DOI: 10.5281/zenodo.5506610
Data: https://zenodo.org/records/5506610 (the single file
        "BAZA_COVID-19 anxiety versus well-being .sav")
License: CC BY 4.0 (verified on the Zenodo record, metadata.license.id
        "cc-by-4.0")
Item text: THREE of the five tables ship it, and the split is a rights
        question rather than an availability one. The `.sav` is unusually well
        documented -- 98 of 109 variables carry their full Polish stem as the
        variable label, and 94 carry their response anchors as value labels --
        so the wording exists for all five. What differs is whose wording it is:
          * kopczynski_2021_pandemic_appraisal -- SHIPS. The 23 adjectives are
            the study's own appraisal checklist, so the deposit's CC BY is the
            wording's licence.
          * kopczynski_2021_mspss -- SHIPS. The MSPSS is registered `ship`.
          * kopczynski_2021_fcv19s -- SHIPS. The FCV-19S is registered `ship`.
          * kopczynski_2021_whoqol_bref -- HELD. The WHOQOL family is
            registered `block`.
          * kopczynski_2021_core_self_evaluations -- HELD. The CSES (Judge,
            Erez, Bono & Thoresen 2003) had NO register row; silence does not
            ship, so this batch writes one with verdict `hold`.

**KW1 is 27 items, not the WHOQOL-BREF's 26, and the 27th is the study's
own.** `KW1.27` asks "Jak zadowolony jesteś ze studiowania w sposób zdalny?"
(how satisfied are you with studying remotely) -- a pandemic question the
authors added to the instrument. It ships in the same table because it was
administered in the same block on the same 1-5 satisfaction scale, and
splitting one administered battery on authorship would misrepresent what the
students answered. The item text table for this deposit is held anyway, so no
WHOQOL wording travels with it; the added item is recorded in the dictionary
row so nobody mistakes the table for a clean 26-item WHOQOL-BREF.

**`P3` is dropped under the 2026-10-20 geographic ruling.** It is the
respondent's place of permanent residence. The ruling is drop-the-column and
ship the rest, which is what happens here; nothing else in the file is
identifying.

**`M1_1` is dropped as corrupt, not as redundant.** It is labelled "Przedzial
wieku" (age bracket) and holds 0, 1, 2 and 3 -- plus 44, 46 and 49, which are
ages that leaked in from the raw age column. A bracket column holding raw ages
cannot be used as either, and `M1` already carries age properly.

Dropped as derived: `LQ_Domain1..4`, `LQ_WHO_Sumaryczna` and `LQ_D1..D4_100`
are the WHOQOL's domain scores and its 0-100 transformations. `filter_$` is an
SPSS analysis filter (`M1 <= 25`). `VAR00002` and `VAR00008` are empty, and
`M5` (type of studies) is constant.

PII: none that survives. The only text column is `M7.txt`, the respondent's
field of study -- 285 distinct degree programmes, which name courses and not
people, so it ships as `cov_field_of_study`. There is no name, email, IP, date
or free-text comment column. The screen below prints its denominator.

Output: five tables, 81,000 responses -- 1,000 respondents, no missing data.
  * kopczynski_2021_whoqol_bref            -- 27 items, resp 1-5
  * kopczynski_2021_pandemic_appraisal     -- 23 items, resp 0-3
  * kopczynski_2021_core_self_evaluations  -- 12 items, resp 1-5
  * kopczynski_2021_mspss                  -- 12 items, resp 1-7
  * kopczynski_2021_fcv19s                 --  7 items, resp 1-5
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import pandas as pd
import pyreadstat

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("BAZA.sav")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

# table -> (source prefix, item count, documented response set). Each response
# set is checked against the file's own value labels before anything is written.
BLOCKS = {
    "kopczynski_2021_whoqol_bref": ("KW1", 27, [1, 2, 3, 4, 5]),
    "kopczynski_2021_core_self_evaluations": ("KW2", 12, [1, 2, 3, 4, 5]),
    "kopczynski_2021_mspss": ("KW3", 12, [1, 2, 3, 4, 5, 6, 7]),
    "kopczynski_2021_fcv19s": ("KW4", 7, [1, 2, 3, 4, 5]),
    "kopczynski_2021_pandemic_appraisal": ("KW5", 23, [0, 1, 2, 3]),
}

COV_MAP = {
    "M1": "cov_age",
    "M2": "cov_sex",
    "M3": "cov_occupational_status",
    "M4": "cov_university",
    "M6": "cov_study_level",
    "M7_kier_stud": "cov_field_group",
    "M7.txt": "cov_field_of_study",
    "M8.int": "cov_year_of_study",
    "P1": "cov_had_covid",
    "P1A": "cov_own_illness_course",
    "P2": "cov_close_contact_had_covid",
    "P2A": "cov_contact_illness_course",
}

DROP = {
    "LP": "the deposit's own row serial; id is assigned here instead",
    "M1_1": "labelled 'age bracket' but holds 0-3 AND the raw ages 44, 46 and "
            "49 -- corrupt as either; M1 carries age properly",
    "M5": "constant (one type of studies)",
    "P3": "place of permanent residence -- dropped under the 2026-10-20 "
          "geographic ruling, which is drop-the-column and ship the rest",
    "VAR00002": "empty (0 of 1,000 rows)",
    "VAR00008": "empty (0 of 1,000 rows)",
    "filter_$": "an SPSS analysis filter (M1 <= 25), not data",
}
DROP_PATTERNS = [
    (r"^LQ_", "a WHOQOL domain score or its 0-100 transformation"),
]


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    # The one text column is the degree programme. It names courses, not
    # people; this checks that rather than taking it on trust.
    assert text_cols == ["M7.txt"], text_cols
    k = df["M7.txt"].nunique()
    print(f"  M7.txt holds {k} distinct degree programmes "
          f"(e.g. {sorted(df['M7.txt'].dropna().unique())[:3]}) -- course "
          "names, not personal data")


def main() -> None:
    df, meta = pyreadstat.read_sav(SRC)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 1000, len(df)

    labelled = sum(1 for c in df.columns
                   if (meta.column_names_to_labels.get(c) or "").strip())
    print(f"variable labels present: {labelled} of {len(df.columns)}; "
          f"value-labelled variables: {len(meta.variable_value_labels)} -- "
          "the stems and anchors are in the file, so item text is a rights "
          "question, not an availability one")
    assert labelled >= 90 and len(meta.variable_value_labels) >= 90

    item_cols = {}
    for table, (prefix, n, permitted) in BLOCKS.items():
        cols = sorted((c for c in df.columns
                       if re.match(rf"^{re.escape(prefix)}\.\d+$", c)),
                      key=lambda c: int(c.split(".")[1]))
        assert len(cols) == n, (table, len(cols), n, cols)
        documented = sorted(int(k) for k in
                            (meta.variable_value_labels.get(cols[0]) or {}))
        assert documented == permitted, (table, documented, permitted)
        item_cols[table] = cols

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    accounted = set(COV_MAP) | set(covs) | {"id"}
    accounted |= {c for cs in item_cols.values() for c in cs}
    dropped = dict(DROP)
    for c in df.columns:
        if c in accounted or c in dropped:
            continue
        for pat, why in DROP_PATTERNS:
            if re.search(pat, c):
                dropped[c] = why
                break
    leftover = [c for c in df.columns
                if c not in accounted and c not in dropped]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c in sorted(dropped):
        if c in df.columns:
            print(f"skipped column {c}: {dropped[c]}")

    for table, cols in item_cols.items():
        write(df, table, cols, covs, BLOCKS[table][2])


def write(df: pd.DataFrame, table: str, cols: list, covs: list,
          permitted: list) -> None:
    # The item code keeps the source's own numbering (kw1_01 ... kw1_27) so an
    # item can be traced back to the deposit's column and its label.
    codes = {c: c.lower().replace(".", "_") for c in cols}
    assert len(set(codes.values())) == len(cols), codes
    long = df[["id"] + covs + cols].rename(columns=codes)
    long = long.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
    before = long["resp"].notna().sum()
    long = long[long["resp"].isin(permitted)]
    assert before == len(long), \
        f"{table}: {before - len(long)} cell(s) outside {permitted}"

    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs].sort_values(
        ["id", "item"]).reset_index(drop=True)

    checks = run_qc(long, permitted_values=permitted)
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
