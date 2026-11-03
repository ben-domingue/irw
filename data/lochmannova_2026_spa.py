#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/38ZOKO
# DOI: 10.7910/DVN/38ZOKO (dataset; the record names no published paper)
# Deposit: Lochmannova, A., Huseynli, A., Spisak, L., Marek, P., Olecka, I., &
#   Simbartl, P. (2026). Perception of Therapeutic Landscapes and
#   Restorativeness of Spa Environments among Residents and Its Association
#   with Subjective Well-Being [Data set]. Harvard Dataverse.
# Data: data-matrix-en.xlsx (918 rows x 129 columns; English variable names --
#   the deposit's readme says data-matice-cz.xlsx holds identical data under
#   Czech names, so only the English file is read). Dataverse file id 14386747.
#   sha256 8fe0bd46d08bb32181865be7a09fa9c284e9d19978e38de01489be7df917f7e7
# Codebook: master_codebook.xlsx (Dataverse file id 14386746): one row per
#   variable with instrument, Czech and English question text, scale and
#   response options. readme-en.pdf (file id 14386749) documents sampling and
#   QC.
#   sha256 c9504924763d028d0f79910b6aa2dbf63d5e5e1cdd70f51cfa7768e7a1d94d61
# License: CC BY 4.0 (resolved from the Dataverse dataset's license field, and
#   stated in readme-en.pdf). The respondents were surveyed by the depositors
#   (CAWI, first half of 2026); not a relabelled third-party survey.
#
# Found by the repos monthly sweep of 2026-11-02 (recoverable_format).
#
# 918 adult residents (18+; one recorded age is 17) of five spa towns in the
# Karlovy Vary Region, Czech Republic, quota-sampled by sex, age and town.
# Questionnaire in Czech. `respondent_id` (1-918, "artificially generated
# identifier" per the codebook) is the id and is the same in all tables.
#
# EIGHT output tables, one per instrument (items are the questionnaire's item
# numbers, O28 = item 28, so they map straight onto the codebook rows):
#   lochmannova_2026_restorativeness     O28-O38  11 items, 0-10
#       Perceived Restorativeness Scale, PRS-11 (codebook); 0 Not at all,
#       6 Quite a lot, 10 Completely.
#   lochmannova_2026_nature_relatedness  O39-O44   6 items, 1-5
#       Nature Relatedness Scale NR-6; 1 Disagree strongly .. 5 Agree strongly.
#   lochmannova_2026_spa_environment     O45-O52   8 items, 1-5
#       Study-specific spa environment items ("Non-standardized items" in the
#       codebook); 1 Strongly disagree .. 5 Strongly agree. O51 (tourism makes
#       the spa environment hard to use) is negatively worded and NOT
#       reversed; shipped as recorded.
#   lochmannova_2026_place_attachment    O53-O64  12 items, 1-5
#       Place Attachment Scale (place identity + dependence); 1 Strongly
#       disagree .. 5 Strongly agree. O64 (would enjoy the same things just as
#       much elsewhere) is negatively keyed and NOT reversed.
#   lochmannova_2026_sense_of_community  O66-O89  24 items, 1-4
#       Sense of Community Index 2 (SCI-2), adapted to the spa town; 1 Not at
#       all, 2 Somewhat, 3 To a large extent, 4 Completely. SCI-2's lead
#       question O65 ("how important is it to feel a sense of belonging", 1-6)
#       is a separate single item on another scale and is NOT shipped. The
#       source column for O68 carries a Czech editing note in its name ("check
#       this is not a duplicate name or other wording"); its codebook question
#       ("...successful in helping meet the needs of its members") differs from
#       O66's ("...helps me meet important needs"), which is SCI-2's wording
#       for two distinct items, so O68 is kept.
#   lochmannova_2026_health_literacy     O90-O105 16 items, 1-4
#       HLS-EU-Q16; 1 Very difficult, 2 Difficult, 3 Easy, 4 Very easy.
#   lochmannova_2026_wellbeing           O106-O110 5 items, 0-5
#       WHO-5 Well-Being Index (past two weeks); 0 At no time .. 5 All of the
#       time.
#   lochmannova_2026_self_efficacy       O111-O120 10 items, 1-4
#       General Self-Efficacy Scale (GSE); 1 Disagree .. 4 Agree.
# One cell is missing in the whole item set (O65, not shipped, a blank ' ').
#
# NOT shipped as items:
#   O18-O27, the short ALPHA environment checklist (yes/no presence of
#     neighbourhood features -- detached houses, shops, a park, a bus stop;
#     O26/O27 add a "not applicable" code). A formative inventory of the
#     neighbourhood, not a person-trait battery: its items are near-
#     uncorrelated (mean r .03).
#   O13-O16, four single 1-10 ratings; O13/O14 (self-rated physical/mental
#     health) are carried as covariates, O15/O16 (how far the spa environment
#     supports physical/psychological health) are not.
#   age_weight (derived weight), O2_age_category (derived from age).
#
# Plausibility check (2026-11-02): within-scale inter-item r is clearly
#   positive everywhere -- PRS mean .56 (min .42), NR-6 .43 (.25), place .45
#   (.04, the negatively keyed O64), SCI-2 .57 (.43), HLS .36 (.18), WHO-5 .56
#   (.50), GSE .39 (.31), spa items .42 (.08, O51). Read as real survey data.
#
# Covariates (codes as in the codebook): cov_spa_town (1 Karlovy Vary,
#   2 Marianske Lazne, 3 Frantiskovy Lazne, 4 Jachymov, 5 Lazne Kynzvart),
#   cov_age (years), cov_sex (female/male), cov_education (1 primary .. 5
#   university), cov_economic_activity (1 employee, 2 self-employed,
#   3 student, 4 parental leave, 5 unemployed, 6 old-age pension, 7 disability
#   pension, 8 long-term sick leave, 9 other), cov_marital_status (1 single,
#   2 married, 3 divorced, 4 widowed, 5 living with partner, 6 other),
#   cov_spa_sector_work (works in spa/health/tourism: 1 yes, 2 no),
#   cov_work_schedule (1-7), cov_children (child under 18 at home: 1 yes,
#   2 no), cov_housing (1 apartment, 2 house, 3 other), cov_financial_situation
#   (1 very good .. 5 very difficult), cov_residence_length (1 since birth,
#   2 <1 yr, 3 1-5, 4 6-10, 5 11-20, 6 >20 years), cov_physical_health and
#   cov_mental_health (1 very poor .. 10 excellent), cov_spa_visits (spa
#   treatments in past 12 months: 1 never .. 6 more than 20 times).
#
# Item text: NOT shipped. Extraction is solved -- master_codebook.xlsx gives
#   the Czech (as administered) and English wording of every item, tied by
#   variable name rather than position. Held on rights and cost: seven of the
#   eight tables are named third-party instruments. In the rights register on
#   2026-11-02 WHO-5 and HLS-EU-Q16 are BLOCK rows, GSE is a SHIP row, Williams
#   & Vaske place attachment has a SHIP row only for one adaptation; PRS-11,
#   NR-6 and SCI-2 have no row (silence holds). The eight spa items are
#   study-authored under the deposit's CC BY and could ship on their own; not
#   done in this pass.
#
# PII: none. Five free-text "Other -- specify" columns (economic activity,
#   marital status, employment sector, work schedule, housing type; 1-8
#   distinct short answers each, no names, emails or addresses) are DROPPED,
#   not carried. The other two text columns are O65 (codes 1-6, one blank
#   cell) and O7a_employment_sector (codes 1-5, blank when O7 = no; not
#   carried). Asserted below.

import hashlib
import os
import sys

import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = os.path.join(REPO_ROOT, "automated_finding", "irw_output")
RAW = os.environ.get("LOCHMANNOVA_RAW", "data-matrix-en.xlsx")
SHA256 = "8fe0bd46d08bb32181865be7a09fa9c284e9d19978e38de01489be7df917f7e7"

TABLES = {
    "lochmannova_2026_restorativeness": (range(28, 39), list(range(0, 11))),
    "lochmannova_2026_nature_relatedness": (range(39, 45), [1, 2, 3, 4, 5]),
    "lochmannova_2026_spa_environment": (range(45, 53), [1, 2, 3, 4, 5]),
    "lochmannova_2026_place_attachment": (range(53, 65), [1, 2, 3, 4, 5]),
    "lochmannova_2026_sense_of_community": (range(66, 90), [1, 2, 3, 4]),
    "lochmannova_2026_health_literacy": (range(90, 106), [1, 2, 3, 4]),
    "lochmannova_2026_wellbeing": (range(106, 111), [0, 1, 2, 3, 4, 5]),
    "lochmannova_2026_self_efficacy": (range(111, 121), [1, 2, 3, 4]),
}
COVS = {
    "O1_spa_town": "cov_spa_town", "O2_age": "cov_age", "O3_sex": "cov_sex",
    "O4_education": "cov_education",
    "O5_economic_activity": "cov_economic_activity",
    "O6_marital_status": "cov_marital_status",
    "O7_field_of_employment": "cov_spa_sector_work",
    "O8_work_schedule": "cov_work_schedule", "O9_children": "cov_children",
    "O10_housing_type": "cov_housing",
    "O11_financial_situation": "cov_financial_situation",
    "O12_length_of_residence": "cov_residence_length",
    "O13_physical_health": "cov_physical_health",
    "O14_mental_health": "cov_mental_health",
    "O17_spa_visits_past_12_months": "cov_spa_visits",
}
FREE_TEXT = ["O5_economic_activity_other", "O6_marital_status_other",
             "O7a_employment_sector_other", "O8_work_schedule_other",
             "O10_housing_type_other"]


def _qnum(col):
    head = col.split("_")[0]
    return int(head[1:]) if head[0] == "O" and head[1:].isdigit() else None


def convert():
    with open(RAW, "rb") as fh:
        assert hashlib.sha256(fh.read()).hexdigest() == SHA256, "file changed"
    df = pd.read_excel(RAW)
    assert df.shape == (918, 129), df.shape
    assert df["respondent_id"].is_unique
    text = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])
            or df[c].dtype == object]
    print(f"PII screen: {len(text)} text column(s) of {df.shape[1]}: {text}")
    assert set(text) == set(FREE_TEXT) | {"O65_community_belonging",
                                          "O7a_employment_sector"}, text
    df = df.drop(columns=FREE_TEXT)

    bynum = {_qnum(c): c for c in df.columns if _qnum(c) is not None}
    df = df.rename(columns={"respondent_id": "id", **COVS})
    df["cov_sex"] = df["cov_sex"].map({1: "female", 2: "male"})
    assert df["cov_sex"].notna().all()
    covs = list(COVS.values())
    assert df[covs].notna().all().all()

    os.makedirs(OUT_DIR, exist_ok=True)
    for table, (nums, scale) in TABLES.items():
        ren = {bynum[n]: f"O{n}" for n in nums}
        cols = list(ren.values())
        wide = df.rename(columns=ren)
        assert all(pd.api.types.is_integer_dtype(wide[c]) for c in cols), table
        long = wide.melt(id_vars=["id"] + covs, value_vars=cols,
                         var_name="item", value_name="resp")
        long = long[["id", "item", "resp"] + covs]
        long["_n"] = long["item"].str[1:].astype(int)
        long = long.sort_values(["id", "_n"]).drop(columns="_n")
        long = long.reset_index(drop=True)
        assert long["resp"].notna().all()
        assert long["resp"].isin(scale).all(), table
        assert long["id"].nunique() >= 100

        checks = run_qc(long, permitted_values={i: scale for i in cols})
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, fails
        for c in checks:
            if c.status == "warn":
                print(f"  [qc warn] {table} {c.name}: {c.detail[:180]}")

        long.to_csv(os.path.join(OUT_DIR, table + ".csv"), index=False)
        print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
              f"items={long['item'].nunique()} "
              f"resp={long['resp'].min()}-{long['resp'].max()}")


if __name__ == "__main__":
    convert()
