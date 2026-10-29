"""
A 28-item fisheries literacy exam administered to 938 fishers and traders at 37
landing sites on the Kenyan coast, 2020-2024.

Source: Kosgei, J. (2026). Fisheries literacy dataset [Dataset]. Harvard
        Dataverse. The deposit's own description: "The dataset was generated
        between 2020 and 2024 at 37 landing sites in Kenya coastline", covering
        "28 questions on fisheries catch, regulation, economics, science, and
        ecology, answered through a self-assessing literacy questionnaire ...
        Each question is scored 1 if answered correctly and 0 if not."
DOI: 10.7910/DVN/TX683E
Data: https://doi.org/10.7910/DVN/TX683E (Literacy_data.xlsx, sheet "lit_data",
        downloaded with format=original)
License: CC0 1.0 (verified on the Dataverse record)
Item text: NOT shipped -- but it is CLOSE, and this is the cheapest item text
        on the list for a later pass. The column names are abbreviated question
        descriptions rather than wording ("science_determine_cpue",
        "ecology_knows_urchin_predator"), the workbook has no second sheet, and
        the deposit ships no questionnaire file, so the exam's actual phrasing
        is not in hand. What IS established and shipped in the response table is
        that every item is scored 1=correct / 0=incorrect, stated by the deposit
        itself. The five domain prefixes (catch, law, science, economics,
        ecology) are the deposit's own grouping and are carried as `section_id`
        material whenever the wording is recovered.

One header had to be made usable as an item code. The workbook repeats the
header "economics_understand_cost_benefit" THREE times for three different
questions (the three columns hold different values). A duplicate header cannot
be an item code, so the three become economics_cost_benefit_1/_2/_3 in source
column order -- the only derivation available, and the reason the economics
block is the one place in this table where item identity rests on position
rather than on a distinct name.

Geographic columns are dropped, in no form, under the 2026-10-20 ruling:
`latitude`/`longitude` (the landing site's coordinates) and `bmu`/`bmu_new`
(the landing site's NAME, 37 of them over 938 respondents, so roughly 25 people
each). The sampling structure they carry is not lost: `cluster_id` ships an
anonymous 1..37 index of the landing site, which preserves the clustering for
anyone fitting a multilevel model without carrying a place name. The four
`county_*` columns are county-level statistics from the 2019 census rather than
facts about a respondent, and are dropped too.

PII: no name, email, date of birth, phone or identifier column. The screen below
prints its denominator. `interviewee_unique_id` is a per-landing-site serial
("Bur_01") and is replaced by the row index.

ONE table, not five. `run_qc` warns `multi_scale` on the five item-name
prefixes, and the answer is that they are the deposit's own domains WITHIN one
exam, not five instruments: its description calls this "a self-assessing
literacy questionnaire" of "28 questions on fisheries catch, regulation,
economics, science, and ecology" and reports "averages calculated overall and
by category". Same respondents, same 0/1 correctness format, one administration,
one total score -- so the prefixes are design blocks, which the standard says
are not grounds for splitting.

Output: one table, 26,260 responses -- 938 respondents x 28 items, 0/1
(4 unanswered cells dropped).
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("Literacy_data.xlsx")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

TABLE = "kosgei_2026_fisheries_literacy"

ITEM_PREFIXES = ("catch_identify_", "law_", "science_", "economics_", "ecology_")
SCORES = ["catch_score", "law_score", "science_score", "economics_score",
          "ecology_score", "total_score"]

# The three same-named economics questions, in source column order.
ECON_DUPES = {
    "economics_understand_cost_benefit": "economics_cost_benefit_1",
    "economics_understand_cost_benefit.1": "economics_cost_benefit_2",
    "economics_understand_cost_benefit.2": "economics_cost_benefit_3",
}

COV_MAP = {
    "region": "cov_region",
    "gender": "cov_gender",
    "age_interviewee": "cov_age",
    "age_group": "cov_age_group",
    "years_of_formal_education": "cov_years_education",
    "occupation": "cov_occupation",
    "exam_completion_status": "cov_exam_completion",
    "fish_trader": "cov_fish_trader",
    "bmu_leadership": "cov_bmu_leadership",
    "fishersforum_attendance": "cov_fishers_forum_attendance",
    "total_members_hh": "cov_household_members",
    "no._fishers": "cov_site_n_fishers",
    "no._bmu_members": "cov_site_n_bmu_members",
    "estimated_food_expenditure_2weeks": "cov_food_expenditure_2wk_kes",
    "ind_exp_2wks": "cov_individual_expenditure_2wk_kes",
}

DROP = {
    "bmu": "the landing site's NAME -- a geographic identifier, dropped in no "
        "form under the 2026-10-20 ruling; its clustering ships as cluster_id",
    "bmu_new": "the same landing-site name, recoded by the depositor",
    "latitude": "the landing site's coordinates -- geographic, dropped",
    "longitude": "the landing site's coordinates -- geographic, dropped",
    "county_ppltn_2019": "a 2019 census county statistic, not a respondent fact",
    "county_growth_rate_yr": "a census county statistic, not a respondent fact",
    "county_ppltn_density_km2": "a census county statistic, not a respondent fact",
    "county_literacy_score": "a census county statistic, not a respondent fact",
    "county_literacy_score_female": "a census county statistic",
    "county_literacy_score_male": "a census county statistic",
    "county_score": "a depositor-computed county aggregate",
    "interviewee_unique_id": "a per-site serial ('Bur_01'), replaced by the "
        "row index",
}

BLANK = " "


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    for banned in ("name", "email", "mail", "phone", "birth", "dob", "address",
                   "national_id", "idno"):
        bad = [c for c in text_cols if banned in c.lower()]
        assert not bad, f"possible identifier column: {bad}"
    # Every text column but one is a closed category label; check the count of
    # distinct values rather than assuming. The exception is the one identifier
    # column, which is checked to be the per-site serial it claims to be
    # ("Bur_01") rather than anything carrying a person's details, and is
    # dropped either way.
    serial = df["interviewee_unique_id"].astype(str)
    assert serial.str.fullmatch(r"[A-Za-z]{2,10}[-_ ]{1,2}\d{1,3}").all(), \
        sorted(set(serial[~serial.str.fullmatch(r"[A-Za-z]{2,10}[-_ ]{1,2}\d{1,3}")]))[:5]
    for c in text_cols:
        if c == "interviewee_unique_id":
            continue
        k = df[c].nunique()
        assert k <= 40, f"{c} has {k} distinct values -- check it is not free text"


def main() -> None:
    df = pd.read_excel(SRC, sheet_name="lit_data")
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 938, len(df)

    items = [c for c in df.columns
             if c.startswith(ITEM_PREFIXES) and c not in SCORES]
    assert len(items) == 28, (len(items), items)
    codes = {c: ECON_DUPES.get(c, c) for c in items}
    assert len(set(codes.values())) == 28, codes

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    # An anonymous landing-site index, so the clustering survives without the
    # place name. Sorted so the numbering is reproducible.
    sites = {s: i for i, s in enumerate(sorted(df["bmu"].unique()), 1)}
    assert len(sites) == 37, len(sites)
    df["cluster_id"] = df["bmu"].map(sites)

    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        col = df[src].replace(BLANK, pd.NA)
        if src == "exam_completion_status":
            col = col.str.lower()     # 'Self'/'self' are the same answer
        df[dst] = col
    covs = list(COV_MAP.values())

    accounted = (set(COV_MAP) | set(covs) | set(DROP) | set(SCORES)
                 | set(items) | {"id", "cluster_id"})
    leftover = [c for c in df.columns if c not in accounted]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in DROP.items():
        print(f"skipped column {c}: {why}")
    for c in SCORES:
        print(f"skipped column {c}: depositor-computed domain or total score")

    long = df[["id", "cluster_id"] + covs + items].rename(columns=codes)
    long = long.melt(id_vars=["id", "cluster_id"] + covs, var_name="item",
                     value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"].replace(BLANK, pd.NA),
                                 errors="raise")
    before = len(long)
    long = long.dropna(subset=["resp"])
    print(f"dropped {before - len(long)} unanswered item cell(s) of {before}")
    assert set(long["resp"].unique()) == {0, 1}, sorted(long["resp"].unique())
    long["resp"] = long["resp"].astype(int)

    long = long[["id", "item", "resp", "cluster_id"] + covs]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)

    checks = run_qc(long)
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
