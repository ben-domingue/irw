"""
Scam identification ability (SIA) in a Kenyan online sample of 1,000 adults:
12 phone-message vignettes, each classified as a scam or not, each followed by
a five-point confidence rating on the same page.

Source: Kubilay, E., Raiber, E., Spantig, L., Cahlíková, J., & Kaaria, L.
        (2023). Can you spot a scam? Measuring and improving scam
        identification ability. Journal of Development Economics, 165, 103147.
DOI: 10.1016/j.jdeveco.2023.103147
Data: https://doi.org/10.7910/DVN/HUYYQZ (Harvard Dataverse,
        online_survey_labeled.dta -- downloaded with format=original, NOT the
        .tab conversion)
License: CC0 1.0 (verified on the Dataverse record's licence block:
        "CC0 1.0", http://creativecommons.org/publicdomain/zero/1.0)
Item text: shipped. The deposit's own codebook (online_survey_labeled_codebook
        .xlsx) carries the answer and confidence option labels against each
        variable name, and the paper's Appendix holds the vignettes. The
        vignette WORDING itself is not in the deposit, so item_text names the
        vignette slot and the option text is what ships -- see
        automated_finding/itemtext_provenance.csv.

Design, from the paper (section 3, "Our measure consists of two blocks with
four scam vignettes and two official messages each"): the two blocks are FIXED
sets of six vignettes; the blocks are presented in random order and the
messages are randomized within each block; the tips treatment is administered
BETWEEN the two blocks. So the source columns SIA_A_M* and SIA_B_M* identify
stable vignettes -- item identity is safe -- but which block a respondent saw
first is what decides whether their answers to it were pre- or post-treatment.

`wave` and `treat` are therefore deliberately NOT shipped. The deposit's
codebook documents OrderSIA_AB only as "No/Yes" and never says which value
means which block came first, and an empirical check was inconclusive: tips
raise the share of "scam" answers in block A by 0.113 among OrderSIA_AB=0
respondents (consistent with A being their second block) but move block B by
only +0.029 among OrderSIA_AB=1 respondents, which is too weak to read a
direction off. Rather than assert a `treat` that is right for half the sample
and backwards for the other half, both treatment assignment and the order
indicator ship as covariates (cov_treatment, cov_treatment_tips,
cov_treatment_incentives, cov_order_sia_ab) so a user can reconstruct the
design once the direction is established.

PII: none. The PII screen below prints its denominator. There is no name,
email, phone number, national ID or date of birth; `BirthYear` is a year and
is dropped anyway because `Age` carries the same fact. `County` is a Kenyan
county code and is dropped in no form under the 2026-10-20 geographic-code
ruling.

Output: two tables, 12,000 responses each.
  * kubilay_2023_scam_identification -- 12 vignettes, resp 1 = Scam,
        2 = No scam, with per-vignette page time as `rt`
  * kubilay_2023_scam_confidence     -- the same 12 vignettes, resp 1-5

Not shipped: the DFS_2_*/DFS_4_* and ScamExp_3_*/4_*/5_* blocks are
check-all-that-apply indicator expansions that include "None of the above" and
"Other" as their own columns, and the ScamExp blocks are asked only of
respondents who reported being contacted by a scammer. They are behaviour
checklists rather than a measured battery, so they are left out rather than
shipped as pseudo-items.
"""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

SRC = (Path(sys.argv[1]) if len(sys.argv) > 1
       else Path("online_survey_labeled.dta"))
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

BLOCKS = list("AB")
SLOTS = range(1, 7)

# Source column -> cov_* name. Every one of these carries numeric codes the
# deposit's codebook labels (Education 0-3, Income 1-6, Age_groups 1-3, the
# rest 0/1), so the harvest in metadata/covariate_labels/ applies.
COV_MAP = {
    "Female": "cov_female",
    "Age": "cov_age",
    "Age_groups": "cov_age_group",
    "Urban": "cov_urban",
    "Education": "cov_education",
    "Income": "cov_income",
    "FormalEmployment": "cov_formal_employment",
    "PhoneInternet": "cov_phone_internet",
    "PhoneSocialMedia": "cov_phone_social_media",
    "PhoneShare": "cov_phone_shared",
    "PhoneSIMShare": "cov_sim_shared",
    "PhoneSIMRegistered": "cov_sim_registered",
    "Treatment": "cov_treatment",
    "Treatment_Tips": "cov_treatment_tips",
    "Treatment_Incentives": "cov_treatment_incentives",
    "OrderSIA_AB": "cov_order_sia_ab",
    "Attention_Fail": "cov_attention_fail",
    "ScamExp_1": "cov_ever_contacted_by_scammer",
    "ScamExp_8": "cov_ever_scam_victim",
    "ScamExp_10": "cov_knows_scam_victim",
    "DFS_90days": "cov_recent_dfs_use",
}

# Dropped, each for a stated reason -- a column is in exactly one of
# COV_MAP, DROP, or the item/rt blocks, and main() asserts that.
DROP = {
    "id": "the deposit's own observation number; replaced by a row index",
    "StartDate": "survey timestamp, not an item or a covariate",
    "EndDate": "survey timestamp, not an item or a covariate",
    "Durationinseconds": "whole-survey completion time -- NOT an item rt, and "
        "not carried as a covariate either",
    "Duration_minutes": "the same whole-survey duration in minutes",
    "UserLanguage": "Qualtrics interface language, constant-ish metadata",
    "Consent_1": "consent checkbox, not a measured response",
    "Consent_2": "consent checkbox, not a measured response",
    "Consent_3": "consent checkbox, not a measured response",
    "Consent_4": "consent checkbox, not a measured response",
    "BirthYear": "year of birth -- dropped; Age carries the same fact",
    "County": "Kenyan county code -- a geographic identifier, dropped in no "
        "form under the 2026-10-20 ruling",
    "age_group_dum1": "regression dummy for Age_groups, already a covariate",
    "age_group_dum2": "regression dummy for Age_groups, already a covariate",
    "age_group_dum3": "regression dummy for Age_groups, already a covariate",
    "PostSecondaryEducation": "derived from Education, already a covariate",
    "LowIncome": "derived from Income, already a covariate",
    "Treatment_both": "derived from Treatment, already a covariate",
    "DFS_4_all": "count of DFS uses -- an aggregate of a dropped block",
    "DFS_diverse": "above-median DFS use -- an aggregate of a dropped block",
    "dfs_trust_high": "recode of DFS_6, a dropped single question",
    "dfs_trust_med": "recode of DFS_6, a dropped single question",
    "dfs_trust_low": "recode of DFS_6, a dropped single question",
}


def item_cols(kind: str) -> dict:
    """Source column -> item code, for 'Answer' or 'Confidence'.

    The item code is the source column's own vignette slot, lowercased
    (SIA_A_M1_Answer -> sia_a_m1), never a positional index: the two blocks
    are fixed sets, so the slot is the vignette's identity.
    """
    return {f"SIA_{b}_M{i}_{kind}": f"sia_{b.lower()}_m{i}"
            for b in BLOCKS for i in SLOTS}


def rt_cols() -> dict:
    """Source column -> item code for the per-vignette page time.

    Qualtrics' PageSubmit is the time in seconds the respondent spent on the
    vignette's own page. The page carried the classification and, after it was
    answered, the confidence scale, so it is a per-item time covering both
    responses to that vignette -- which is why it ships on the classification
    table only, not duplicated onto the confidence table.
    """
    return {f"T_SIA_{b}_M{i}_PageSubmit": f"sia_{b.lower()}_m{i}"
            for b in BLOCKS for i in SLOTS}


def pii_screen(df: pd.DataFrame) -> None:
    text_cols = [c for c in df.columns if pd.api.types.is_string_dtype(df[c])]
    print(f"PII screen: examined {len(text_cols)} string column(s) of "
          f"{len(df.columns)}: {text_cols}")
    assert len(df.columns) > 0
    for banned in ("name", "email", "mail", "phone_number", "nationalid",
                   "idnumber", "dob", "birthdate"):
        bad = [c for c in text_cols if banned in c.lower()]
        assert not bad, f"possible identifier column: {bad}"


def main() -> None:
    df = pd.read_stata(SRC, convert_categoricals=False)
    print("raw shape", df.shape)
    pii_screen(df)
    assert len(df) == 1000, len(df)

    answers, confids, times = item_cols("Answer"), item_cols("Confidence"), rt_cols()
    for block in (answers, confids, times):
        assert all(c in df.columns for c in block), block

    df = df.reset_index(drop=True)
    df["id"] = range(1, len(df) + 1)
    for src, dst in COV_MAP.items():
        assert src in df.columns, src
        df[dst] = df[src]
    covs = list(COV_MAP.values())

    # Balance the books: every source column is either shipped, an item, an
    # rt, or dropped for a printed reason.
    accounted = (set(COV_MAP) | set(DROP) | set(answers) | set(confids)
                 | set(times) | set(covs) | {"id"})
    leftover = [c for c in df.columns if c not in accounted]
    # the deposit uses ___SECTION___ marker columns as visual separators
    markers = [c for c in leftover if c.startswith("___") and c.endswith("___")]
    leftover = [c for c in leftover if c not in markers]
    # the remaining T_* timers are for pages that are not vignettes (consent,
    # the block intros, the six tips animation pages)
    other_timers = [c for c in leftover if c.startswith("T_")]
    leftover = [c for c in leftover if c not in other_timers]
    # the question-level DFS/ScamExp block, deliberately not shipped
    checklists = [c for c in leftover
                  if c.startswith(("DFS_", "ScamExp_"))]
    leftover = [c for c in leftover if c not in checklists]
    assert not leftover, f"unaccounted source columns: {leftover}"
    for c, why in DROP.items():
        print(f"skipped column {c}: {why}")
    print(f"skipped {len(markers)} ___SECTION___ marker column(s)")
    print(f"skipped {len(other_timers)} non-vignette page timer(s): "
          "consent, block intros and the tips animation pages")
    print(f"skipped {len(checklists)} DFS_*/ScamExp_* checklist column(s) -- "
          "check-all-that-apply indicators including 'None of the above' and "
          "'Other', asked conditionally; see the module docstring")

    rt = df[["id"] + list(times)].rename(columns=times).melt(
        id_vars="id", var_name="item", value_name="rt")
    assert rt["rt"].notna().all()

    write(melt(df, answers, covs).merge(rt, on=["id", "item"], how="left",
                                        validate="one_to_one"),
          "kubilay_2023_scam_identification", covs)
    write(melt(df, confids, covs),
          "kubilay_2023_scam_confidence", covs)


def melt(df: pd.DataFrame, block: dict, covs: list) -> pd.DataFrame:
    long = df[["id"] + covs + list(block)].rename(columns=block)
    return long.melt(id_vars=["id"] + covs, var_name="item", value_name="resp")


def write(long: pd.DataFrame, table: str, covs: list) -> None:
    long = long.dropna(subset=["resp"]).copy()
    assert not (long["resp"] % 1 != 0).any(), "fractional resp values"
    long["resp"] = long["resp"].astype(int)
    order = ["id", "item", "resp"] + [c for c in ("rt",) if c in long.columns] + covs
    long = long[order].sort_values(["id", "item"]).reset_index(drop=True)

    checks = run_qc(long)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, (table, fails)
    for c in checks:
        if c.status == "warn":
            print(f"  [qc warn] {table} {c.name}: {c.detail[:220]}")
    long.to_csv(OUT / f"{table}.csv", index=False)
    print(f"{table}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={sorted(long['resp'].unique())}")


if __name__ == "__main__":
    main()
