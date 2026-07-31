from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0128876
# DOI: 10.1371/journal.pone.0128876
# 76 parent-child dyads (152 rows total: `Protocol` 101-181 = parents,
# 201-281 = children) on disability-representation measures. Item
# structure and scale ranges below come directly from the paper's own
# S2 File codebook ("Details of Measures, Procedures, and Coding"), read
# in full this session (converted from legacy .doc via LibreOffice).
#
# Parents and children complete the Disability Explanation measures
# (open- and closed-ended) using the same stimuli/statements but
# different response modalities (parents: numeric scale; children: a
# smiley-face card) -- kept as separate per-population files rather than
# merged, since cross-population scale equivalence for a numeric-vs-
# pictorial response format isn't something to assume.
#
# DEQ_OE (Disability Explanation, Open-Ended) columns are NOT a simple
# presence/absence (0/1) flag despite the codebook's description of the
# final published scoring table -- the actual raw values in this file
# range 0-8 (a count of coded mentions of that disability-model category
# for that stimulus, before the paper's own presence/absence collapse).
# Shipped as raw counts; no re-derivation of the paper's own binary
# collapse is attempted here.
#
# All other rating-scale blocks (DEQ_CE, PE, HK, IA) use a documented
# 1-4 or 1-5 range with "intermediate points" (half-point ratings)
# allowed -- confirmed genuine in the data. A `0` value appears at a
# low, consistent rate (~0.3-1.5%) across every one of these blocks,
# below each scale's documented floor -- treated as a missing-response
# sentinel used throughout the file, not a real scale point, and
# filtered.
#
# Child's Interests and Activities has two response dimensions per the
# same 20 activities: a preference ranking (`IA*`) and how often the
# child engages in it (`IA*_TIME` -- despite the name, this is the
# codebook's own 1-5 frequency scale "1=never...5=once or more a week",
# not a response-time column). Shipped as two separate files.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0128876.s001")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

SHARED_COV_MAP = {"ANA1_SEX": "cov_sex", "ANA2_AGE": "cov_age"}
PARENT_COV_MAP = {
    "ANA3_SATUS": "cov_marital_status",
    "ANA4_EDUCAT_RE": "cov_education_respondent",
    "ANA5_EDUCAT_FA": "cov_education_father",
    "ANA5BIS_EDUCAT_PA": "cov_education_partner",
    "ANA6_JOB_RE": "cov_job_respondent",
    "ANA7_JOB_FA": "cov_job_father",
    "ANA8_SONS": "cov_num_children",
    "ANA9_COUNTRY_OR": "cov_country_origin",
    "ANA10_COUNTRY_RE": "cov_country_residence",
    "ANA11_COUNTRY_TI": "cov_years_in_country",
    "ANA12_POLITICAL": "cov_political_orientation",
    "ANA13_RELIGIO": "cov_religiosity",
    "ANA14_DISABILITY": "cov_disability_self",
    "ANA15_DISAB_FAM": "cov_disability_family",
    "ANA16_DISAB_FRI": "cov_disability_friend",
}
CHILD_COV_MAP = {
    "ANA17_GRADE": "cov_school_grade",
    "ANA18_SCHOOL": "cov_school",
    "ANA19_INTEGR": "cov_classroom_integration",
    "ANA20_DISAB_MATE": "cov_classmate_disability",
    "ANA20BIS_DISAB_SINO": "cov_classmate_disability_yn",
}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="Dataset_S1")
    df = df.rename(columns={"Protocol": "id", **SHARED_COV_MAP, **PARENT_COV_MAP, **CHILD_COV_MAP})
    return df


def _write(long: pd.DataFrame, cov_cols: list[str], out_name: str, itemcov_cols=None):
    cols = ["id", "item", "resp"] + (itemcov_cols or []) + cov_cols
    long = long[cols]
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def _melt(df, item_cols, cov_cols, valid_min=None, valid_max=None, drop_zero=False):
    long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                    var_name="item", value_name="resp")
    long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
    long = long.dropna(subset=["resp"])
    if drop_zero:
        long = long[long["resp"] != 0]
    if valid_min is not None:
        long = long[(long["resp"] >= valid_min) & (long["resp"] <= valid_max)]
    return long.reset_index(drop=True)


def convert():
    df = fetch()
    assert df["id"].nunique() == len(df)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    parent_cov = list(SHARED_COV_MAP.values()) + list(PARENT_COV_MAP.values())
    child_cov = list(SHARED_COV_MAP.values()) + list(CHILD_COV_MAP.values())
    is_parent = df["id"].between(101, 199)
    is_child = df["id"].between(200, 299)

    deq_oe_cols = [c for c in df.columns if c.startswith("DEQ_OE")]
    deq_ce_cols = [c for c in df.columns if c.startswith("DEQ") and "_CE_" in c]
    pe_cols = [c for c in df.columns if c.startswith("PE")]
    chia_cols = [c for c in df.columns if c.startswith("CHIA")]
    hk_cols = [c for c in df.columns if c.startswith("HK")]
    ia_cols = [c for c in df.columns if c.startswith("IA") and "_TIME" not in c]
    ia_time_cols = [c for c in df.columns if c.startswith("IA") and "_TIME" in c]

    dfp = df[is_parent]
    dfc = df[is_child]

    # Disability Explanation, Open-Ended (raw coded-mention counts, no sentinel)
    long = _melt(dfp, deq_oe_cols, parent_cov)
    _write(long, parent_cov, "meloni_2015_deq_oe_parent")
    long = _melt(dfc, deq_oe_cols, child_cov)
    _write(long, child_cov, "meloni_2015_deq_oe_child")

    # Disability Explanation, Closed-Ended (1-4 Likert w/ half-points, 0=missing)
    long = _melt(dfp, deq_ce_cols, parent_cov, valid_min=1, valid_max=4, drop_zero=True)
    _write(long, parent_cov, "meloni_2015_deq_ce_parent")
    long = _melt(dfc, deq_ce_cols, child_cov, valid_min=1, valid_max=4, drop_zero=True)
    _write(long, child_cov, "meloni_2015_deq_ce_child")

    # Parent's Education about Diversity (1-5, 0=missing)
    long = _melt(dfp, pe_cols, parent_cov, valid_min=1, valid_max=5, drop_zero=True)
    _write(long, parent_cov, "meloni_2015_parent_divers_ed")

    # Parent's Interests and Activities Encouraged (1-5, 0=missing)
    long = _melt(dfp, chia_cols, parent_cov, valid_min=1, valid_max=5, drop_zero=True)
    _write(long, parent_cov, "meloni_2015_parent_interests")

    # Child's Disability Knowledge (1-4 w/ half-points, 0=missing).
    # itemcov marks whether the statement is true-keyed ("knowledge") or
    # false-keyed ("stereotype") per the codebook -- raw agreement is
    # shipped either way, no correct/incorrect recode.
    long = _melt(dfc, hk_cols, child_cov, valid_min=1, valid_max=4, drop_zero=True)
    long["itemcov_keyed_true"] = long["item"].str.endswith("_T").astype(int)
    _write(long, child_cov, "meloni_2015_child_disab_knowledge", ["itemcov_keyed_true"])

    # Child's Interests and Activities: preference ranking (1-5, 0=missing)
    long = _melt(dfc, ia_cols, child_cov, valid_min=1, valid_max=5, drop_zero=True)
    _write(long, child_cov, "meloni_2015_child_ia_satisfaction")

    # Child's Interests and Activities: frequency of engagement (1-5, 0=missing)
    long = _melt(dfc, ia_time_cols, child_cov, valid_min=1, valid_max=5, drop_zero=True)
    long["item"] = long["item"].str.removesuffix("_TIME")
    _write(long, child_cov, "meloni_2015_child_ia_frequency")


if __name__ == "__main__":
    convert()
