#!/usr/bin/env python3
# Source: https://doi.org/10.1371/journal.pone.0352933.s001
# DOI: 10.1371/journal.pone.0352933.s001 (data); paper 10.1371/journal.pone.0352933
#   Ng'unda NA, Ghaimo FE, Kiwango F, Chacha S, Mmbaga BT, Mushi D (2026). Depressive symptoms among people living with HIV in Northern Tanzania: the role of family history, social support, and maladaptive coping. PLOS ONE. https://doi.org/10.1371/journal.pone.0352933 (S1 Data, https://doi.org/10.1371/journal.pone.0352933.s001)
# License: CC BY 4.0 (record metadata)
# Data: S1 Data (pone.0352933.s001.dta), 598 adults living with HIV at clinics in Northern Tanzania; id = row order. Stata
#   variable labels name each item (FSSQ1-14, BCS1-28, PHQ1-9, HS1a-3d); value labels on the demographics.
# Covariates: site, age, sex, marital, education, occupation, HIV and ART duration, diabetes, alcohol, BMI, HbA1c, blood pressure.
# Dropped: record_id, the short free-text chronic-illness name (clinical free text), phq10 (difficulty item), totals and recodes.
# FSSQ: one cell coded 0 on the 1-5 scale set missing.
# PII: none.
# Item text: item variable names abbreviate the English stems (i_get_visits_from_friends ...); published instruments.
import io
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://ndownloader.figshare.com/files/71140630'
N_ROWS = 598
ID_COL = None
COVS = {'site': 'cov_site',
 'how_old_are_you_age_in_yea': 'cov_age',
 'sex': 'cov_sex',
 'marital': 'cov_marital',
 'education': 'cov_education',
 'occupation': 'cov_occupation',
 'how_long_have_you_been_dia': 'cov_hiv_duration',
 'how_long_have_you_been_on': 'cov_art_duration',
 'have_you_diagnos_diab': 'cov_diabetes_dx',
 'alcohol_use': 'cov_alcohol',
 'bmi': 'cov_bmi',
 'x_hbaic_measurements': 'cov_hba1c',
 'blood_pressure_systolic': 'cov_sbp',
 'blood_pressure_diastolic': 'cov_dbp'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'ngunda_2026_fssq': ['i_get_visits_from_friends',
                      'i_get_help_around_the_hous',
                      'i_get_help_with_money_in_a',
                      'i_get_praise_for_a_good_jo',
                      'i_have_people_who_care_wha',
                      'i_feel_love_and_affection',
                      'i_get_telephone_calls_from',
                      'i_get_chances_to_talk_to_s',
                      'trust_about_my_personal',
                      'talk_about_money',
                      'i_get_invitations_to_go_ou',
                      'i_get_useful_advice_about',
                      'i_get_help_when_i_need_tra',
                      'i_get_help_when_i_am_sick'],
 'ngunda_2026_brief_cope': ['take_my_mind_off',
                            'concentrating_my_efforts',
                            'saying_to_myself',
                            'using_alcohol_or',
                            'getting_emotiona',
                            'giving_up_trying',
                            'taking_action_to',
                            'refusing_to_beli',
                            'saying_things_to',
                            'getting_help_and',
                            'alcohol_or_other_drugs',
                            'trying_to_see_it',
                            'criticizing_myse',
                            'trying_to_come_u',
                            'getting_comfort',
                            'giving_up_attempt_cope',
                            'looking_for_some',
                            'making_jokes_abo',
                            'doing_something',
                            'accepting_the_reality_re',
                            'expressing_my_ne',
                            'trying_to_find_c',
                            'trying_to_get_ad',
                            'learning_to_live',
                            'thinking_hard_ab',
                            'blaming_myself_f',
                            'praying_or_medit',
                            'making_fun_of_th'],
 'ngunda_2026_phq9': ['feeling_down_depressed_irr',
                      'little_interest_or_pleasur',
                      'trouble_falling_asleep_sta',
                      'poor_appetite_weight_loss',
                      'feeling_tired_or_having_li',
                      'feeling_bad_about_yourself',
                      'trouble_concentrating_on_t',
                      'moving_or_speaking_so_slow',
                      'thoughts_that_you_would_be'],
 'ngunda_2026_hiv_stigma': ['a_some_people_avoid_touchi',
                            'a_people_i_care_about_stop',
                            'a_i_have_lost_friends_by_t',
                            'b_telling_someone_i_have_h',
                            'b_most_people_believe_a_pe',
                            'b_i_am_very_careful_who_i',
                            'c_people_with_hiv_are_trea',
                            'c_most_people_believe_a_pe',
                            'c_most_people_are_uncomfor',
                            'd_i_feel_guilty_because_i',
                            'd_i_feel_like_i_am_a_bad_p',
                            'd_i_feel_i_m_not_as_good_a']}
# (lo, hi) response range per table
RANGES = {'ngunda_2026_fssq': (1, 5),
 'ngunda_2026_brief_cope': (1, 4),
 'ngunda_2026_phq9': (0, 3),
 'ngunda_2026_hiv_stigma': (1, 4)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {'ngunda_2026_fssq': [0]}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'site1': 'other clinical/demographic detail, recode, score or category',
 'record_id': 'record id',
 'Height_cm': 'other clinical/demographic detail, recode, score or category',
 'body_weight_kg': 'other clinical/demographic detail, recode, score or category',
 'marital1': 'other clinical/demographic detail, recode, score or category',
 'education1': 'other clinical/demographic detail, recode, score or category',
 'occupation1': 'other clinical/demographic detail, recode, score or category',
 'for_how_long_have_you_been': 'other clinical/demographic detail, recode, score or category',
 'fh_mi': 'other clinical/demographic detail, recode, score or category',
 'chroI': 'other clinical/demographic detail, recode, score or category',
 'chronic_illness': 'short free-text chronic-illness name (dropped per the 2026-10-21 clinical free-text ruling)',
 'if_you_are_experiencing_an': 'other clinical/demographic detail, recode, score or category',
 'dukeunc_complete': 'other clinical/demographic detail, recode, score or category',
 'Agegroup1': 'other clinical/demographic detail, recode, score or category',
 'FSSQSc': 'other clinical/demographic detail, recode, score or category',
 'FSSQScCat': 'other clinical/demographic detail, recode, score or category',
 'PHQ': 'other clinical/demographic detail, recode, score or category',
 'hbaicCat': 'other clinical/demographic detail, recode, score or category',
 'HS': 'other clinical/demographic detail, recode, score or category',
 'HSCat': 'other clinical/demographic detail, recode, score or category',
 'bmiCat': 'other clinical/demographic detail, recode, score or category',
 'BSCadapt': 'other clinical/demographic detail, recode, score or category',
 'BSCmaladapt': 'other clinical/demographic detail, recode, score or category',
 'BSCmaladaptCat1': 'other clinical/demographic detail, recode, score or category',
 'BSCadaptCat1': 'other clinical/demographic detail, recode, score or category',
 'PHQCat': 'other clinical/demographic detail, recode, score or category',
 'BSCadaptCat': 'other clinical/demographic detail, recode, score or category',
 'BSCmaladaptCat': 'other clinical/demographic detail, recode, score or category',
 'PHQCat1': 'other clinical/demographic detail, recode, score or category',
 'Agegroup': 'other clinical/demographic detail, recode, score or category',
 'FSSQScCat1': 'other clinical/demographic detail, recode, score or category',
 'htnBoth': 'other clinical/demographic detail, recode, score or category',
 'htn': 'other clinical/demographic detail, recode, score or category',
 'diabetes': 'other clinical/demographic detail, recode, score or category'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_stata(io.BytesIO(content), convert_categoricals=False)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    return d


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    d = prep(d)
    assert len(d) == N_ROWS, len(d)
    if ID_COL:
        assert (d[[ID_COL, "wave"]] if "wave" in d else d[ID_COL]).duplicated().sum() == 0, "duplicate ids"
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        if cov in COV_MAPS:
            d[src] = d[src].map(lambda v: v.strip() if isinstance(v, str) else v)
            d[cov] = d[src].map(COV_MAPS[cov])
            assert d[cov].notna().sum() == d[src].notna().sum(), (cov, set(d[src].dropna()) - set(COV_MAPS[cov]))
        else:
            d[cov] = d[src]
    covs = list(dict.fromkeys(COVS.values()))
    items_all = [c for v in BLOCKS.values() for c in v]
    assert len(items_all) == len(set(items_all)), "item in two tables"
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id", "wave"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        wv = ["wave"] if name in WAVE_TABLES else []
        src = d if (wv or "wave" not in d) else d[d["wave"] == WAVE_BASE]
        t = src[["id"] + wv + covs + items].melt(id_vars=["id"] + wv + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + wv + covs].sort_values(["id"] + wv + ["item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
