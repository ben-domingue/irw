from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"

# Source: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0117423
# DOI: 10.1371/journal.pone.0117423
#
# This is the RAW-ITEM companion to the retracted `teicher_2015_mace` table
# (see automated_finding/BATCH_LOG.md, 2026-07-30 retraction): that table
# shipped MACE "severity scores," which the paper's own text confirms are
# IRT-calibrated exposure weights, not raw responses. S9_File (this file)
# is different -- it is the underlying binary (0/1) checklist of whether
# each maltreatment/neglect/witnessing event ever happened, which the
# paper used to *derive* those severity scores via Rasch/IRT modeling.
# These checklist items are genuine per-event yes/no responses.
#
# Item-to-subscale mapping is taken directly from the "Reference_sheet" of
# the S5_File scoring template (a companion Supporting Information file
# also on this article, id=...s014) which groups the instrument's items
# into 10 named subscales (e.g. "Familial and Non-Familial Sexual Abuse",
# "Parental Verbal Abuse", ...). S9's own columns are more granular than
# that reference (distinguishing parent- vs. other-adult- vs.
# sibling-directed events where the reference collapses them), so S9's own
# column names are used as item labels rather than the reference's
# collapsed names -- the reference is used only to confirm which raw
# columns belong to the same construct.
#
# Columns NOT shipped here (left for a future pass, see TODO.md):
# - `Yelled` (parental verbal item with no match in the reference's 10
#   subscales -- likely a pilot item dropped from the final scale).
# - Peer item `Date_*` columns (binary 0/1, paired with each peer item,
#   meaning not confirmed from the paper text -- possibly a
#   developmental-period flag rather than a real date).
# - Household-structure/context columns not clearly matched to a named
#   subscale in the reference (`Separated`, `Divorced`, `P_died`,
#   `Two_households`, `Foster_care`, `Adult_resposibility`, `Unsuper`,
#   `P_homework`, `Kept_secrets` duplicate check, `M_unavail_good`,
#   `F_unavail_good`, `Felt_close`).
# - All derived/composite columns (`SQ_*`, `DES_SCORE`, `LSCL33`,
#   `ASIQ_tot`, `*vas` severity scores, `CTQ_*`, `ACE_*`, `MACE_*_EVER`,
#   `MACE_SUM_EVER`, `emotional_negl_01`...`w_sib_ab_01`, `ATQ_*`) -- these
#   are exactly the kind of derived index that got the sibling table
#   retracted; excluded on the same grounds.
FILE_URL = ("https://journals.plos.org/plosone/article/file"
            "?type=supplementary&id=10.1371/journal.pone.0117423.s018")
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}

COV_MAP = {
    "Gender": "cov_gender",
    "Age": "cov_age",
    "sibs": "cov_num_siblings",
    "race": "cov_race",
    "ethnicity": "cov_ethnicity",
    "subj_ed_yr": "cov_education_years",
    "f_ed_yr": "cov_father_education_years",
    "m_ed_yr": "cov_mother_education_years",
    "par_ed_yr": "cov_parent_education_years",
    "fin_suf": "cov_financial_sufficiency",
    "Interviewed": "cov_interviewed",
}

SCALES = {
    "teicher_2015_mace_verbal": ["Swore", "Hurtful", "Afraid", "Leave"],
    "teicher_2015_mace_nonverbal": ["Closet", "P_diff_please", "P_no_time",
                                     "Financial_pressure", "Kept_secrets"],
    "teicher_2015_mace_physical": ["Pushed", "Hit", "Hit_med", "Spank_open",
                                    "Spanked_bare", "Spanked_strap"],
    "teicher_2015_mace_sexual": ["Sex_comment", "Fondled", "Touch_them", "Attemp_sex",
                                  "Intercourse", "o_sex_com", "o_fondled", "o_touch_them",
                                  "o_attempt_sex", "o_intercourse", "Peer_forced_sex",
                                  "Peer_sex_not_want"],
    "teicher_2015_mace_witness_parent": ["H_Adults_argue", "O_Adults_argue", "Adults_push_m",
                                          "Adults_hit_m", "Adults_hit_med_m", "Adults_push_f",
                                          "Adults_hit_f", "Adults_hit_med"],
    "teicher_2015_mace_witness_sib": ["Push_sib", "Hit_sib", "Hit_sib_med", "Sex_comment_sib",
                                       "Fondled_sib", "Touch_them_sib", "Attempt_sex_sib",
                                       "Intercourse_sib"],
    "teicher_2015_mace_peer_verbal": ["peer_swore", "Peer_hurtful", "Peer_Rumors",
                                       "Peer_Excluded", "Peer_afraid"],
    "teicher_2015_mace_peer_physical": ["Peer_threat_money", "Peer_forced", "Peer_pushed",
                                         "Peer_hit", "Peer_hit_med"],
    "teicher_2015_mace_emot_neglect": ["M_unavail_poor", "F_unavail_poor", "P_loved_you",
                                        "P_special", "Fam_strength"],
    "teicher_2015_mace_phys_neglect": ["P_protect", "P_ER", "No_food", "Dirty_clothes",
                                        "Looked_out_each_other"],
}

# 35 events with a paired subjective-distress rating (asked as a follow-up
# to the checklist items above, wherever the event was endorsed). Shipped
# as their own two files since this is a different response dimension
# (distress felt) from the checklist items (did it happen), not a new
# instrument -- same treatment as a single rating scale applied across
# many stimuli.
DISTRESS_STEMS = ["Afraid", "Leave", "Closet", "Pushed", "Hit", "Hit_med", "Spank_open",
                  "Spanked_bare", "Spanked_strap", "Sex_comment", "Fondled", "Touch_them",
                  "Attemp_sex", "Intercourse", "Push_sib", "Hit_sib", "Hit_sib_med",
                  "Sex_comment_sib", "Fondled_sib", "Touch_them_sib", "Attempt_sex_sib",
                  "Intercourse_sib", "o_sex_com", "o_fondled", "o_touch_them", "o_attempt_sex",
                  "o_intercourse", "H_Adults_argue", "O_Adults_argue", "Adults_push_m",
                  "Adults_hit_m", "Adults_hit_med_m", "Adults_push_f", "Adults_hit_f",
                  "Adults_hit_med"]

# Distress ratings are stored as a messy mix of numeric and text codes.
DISTRESS_RECODE = {"0": 0, "No": 0, "1": 1, "Yes": 1, "yes": 1}


def fetch() -> pd.DataFrame:
    r = requests.get(FILE_URL, headers=UA, timeout=120)
    r.raise_for_status()
    df = pd.read_csv(io.BytesIO(r.content))
    return df.rename(columns={"Username": "id", **COV_MAP})


def _write(long: pd.DataFrame, cov_cols: list[str], out_name: str):
    long = long[["id", "item", "resp"] + cov_cols]
    out_path = OUT_DIR / f"{out_name}.csv"
    long.to_csv(out_path, index=False)
    print(f"{out_name}: rows={len(long)} ids={long['id'].nunique()} "
          f"items={long['item'].nunique()} resp={long['resp'].min():.0f}-{long['resp'].max():.0f}")


def convert():
    df = fetch()
    assert df["id"].nunique() == len(df)
    cov_cols = list(COV_MAP.values())

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for out_name, item_cols in SCALES.items():
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = pd.to_numeric(long["resp"], errors="coerce")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        _write(long, cov_cols, out_name)

    for suffix, out_name in [("Helpless", "teicher_2015_mace_distress_helpless"),
                              ("Terrified", "teicher_2015_mace_distress_terrified")]:
        item_cols = [f"{stem}_{suffix}" for stem in DISTRESS_STEMS]
        long = df.melt(id_vars=["id"] + cov_cols, value_vars=item_cols,
                        var_name="item", value_name="resp")
        long["resp"] = long["resp"].astype(str).map(DISTRESS_RECODE)
        long["item"] = long["item"].str.removesuffix(f"_{suffix}")
        long = long.dropna(subset=["resp"]).reset_index(drop=True)
        _write(long, cov_cols, out_name)


if __name__ == "__main__":
    convert()
