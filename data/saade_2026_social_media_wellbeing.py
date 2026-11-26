#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.35107570.v1
# DOI: 10.6084/m9.figshare.35107570.v1 (data)
#   Saade D, Al-Hajje A, Sacre H, Abbas Z, Haddad C, Mourad N (2026). Psychological Well-Being and Social Media Data [Data set]. figshare. https://doi.org/10.6084/m9.figshare.35107570.v1
# License: CC BY 4.0 (record metadata)
# Data: Social_media_MH.xlsx (Google Forms export, recoded), 511 Lebanese university students (2025), the file's Serial_Nbre.
#   No codebook; instruments read from the column names, ranges as observed. Reverse-keyed copies (*_rev) are the
#   authors' recodes and are not shipped; the items are as answered.
# Tables: ATTARI-12, SPAI (26), SMD (9, yes/no), FOMO (4 x 5), Rosenberg (10), WHO-5.
# Covariates: age, gender, nationality, marital, university type, school, study year, substance use, income, employment (codes).
# Dropped: timestamp, area of residence (geographic), university name code, device/platform/sleep single items, all
#   totals, categorisations, factor scores, reverse-coded copies and filter.
# PII: none.
# Item text: codes only in the deposit.
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
URL = 'https://ndownloader.figshare.com/files/71839498'
N_ROWS = 511
ID_COL = 'Serial_Nbre'
COVS = {'Age': 'cov_age',
 'Gender': 'cov_gender',
 'Nationality': 'cov_nationality',
 'Maritalstatus': 'cov_marital',
 'Type_university': 'cov_university_type',
 'School': 'cov_school',
 'Yearofstudy': 'cov_year',
 'Doyoudrinkalcohol': 'cov_alcohol',
 'Doyousmokecigarettes': 'cov_cigarettes',
 'Doyousmokenargileh': 'cov_narghile',
 'Doyouuseecigarettesvapingdevices': 'cov_vaping',
 'Householdmonthlyincome': 'cov_income',
 'EmploymentStatus': 'cov_employment'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'saade_2026_attari12': ['ATTARI_1',
                         'ATTARI_2',
                         'ATTARI_3',
                         'ATTARI_4',
                         'ATTARI_5',
                         'ATTARI_6',
                         'ATTARI_7',
                         'ATTARI_8',
                         'ATTARI_9',
                         'ATTARI_10',
                         'ATTARI_11',
                         'ATTARI_12'],
 'saade_2026_spai': ['SPAI_1',
                     'SPAI_2',
                     'SPAI_3',
                     'SPAI_4',
                     'SPAI_5',
                     'SPAI_6',
                     'SPAI_7',
                     'SPAI_8',
                     'SPAI_9',
                     'SPAI_10',
                     'SPAI_11',
                     'SPAI_12',
                     'SPAI_13',
                     'SPAI_14',
                     'SPAI_15',
                     'SPAI_16',
                     'SPAI_17',
                     'SPAI_18',
                     'SPAI_19',
                     'SPAI_20',
                     'SPAI_21',
                     'SPAI_22',
                     'SPAI_23',
                     'SPAI_24',
                     'SPAI_25',
                     'SPAI_26'],
 'saade_2026_smd9': ['SMD_1', 'SMD_2', 'SMD_3', 'SMD_4', 'SMD_5', 'SMD_6', 'SMD_7', 'SMD_8', 'SMD_9'],
 'saade_2026_rses': ['Rosenberg_1',
                     'Rosenberg_2',
                     'Rosenberg_3',
                     'Rosenberg_4',
                     'Rosenberg_5',
                     'Rosenberg_6',
                     'Rosenberg_7',
                     'Rosenberg_8',
                     'Rosenberg_9',
                     'Rosenberg_10'],
 'saade_2026_who5': ['WHO_1', 'WHO_2', 'WHO_3', 'WHO_4', 'WHO_5'],
 'saade_2026_fomo': ['NeedtoBelong1',
                     'NeedtoBelong2',
                     'NeedtoBelong3',
                     'NeedtoBelong4',
                     'NeedtoBelong5',
                     'NeedforPopularity1',
                     'NeedforPopularity2',
                     'NeedforPopularity3',
                     'NeedforPopularity4',
                     'NeedforPopularity5',
                     'Anxiety1',
                     'Anxiety2',
                     'Anxiety3',
                     'Anxiety4',
                     'Anxiety5',
                     'Addiction1',
                     'Addiction2',
                     'Addiction3',
                     'Addiction4',
                     'Addiction5']}
# (lo, hi) response range per table
RANGES = {'saade_2026_attari12': (1, 5),
 'saade_2026_spai': (1, 4),
 'saade_2026_smd9': (0, 1),
 'saade_2026_rses': (1, 4),
 'saade_2026_who5': (0, 5),
 'saade_2026_fomo': (1, 4)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Serial_Nbre': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Timestamp': 'timestamp',
 'Areaofresidence': 'area of residence (geographic)',
 'Nameoftheuniversity': 'university name code',
 'CurrentGPAoraverage20': 'single-question usage / device / platform / sleep item or derived score, recode, factor '
                          'or filter',
 'Howmanyindividualsliveinyourhouseholdincludingyourself': 'single-question usage / device / platform / sleep item '
                                                           'or derived score, recode, factor or filter',
 'Whatisthenumberofrooms': 'single-question usage / device / platform / sleep item or derived score, recode, factor '
                           'or filter',
 'Doyouhaveanyhealthcoverage': 'single-question usage / device / platform / sleep item or derived score, recode, '
                               'factor or filter',
 'CurrentLivingSituation': 'single-question usage / device / platform / sleep item or derived score, recode, factor '
                           'or filter',
 'Smartphone': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Tablet': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Laptop': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Desktop_computer': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                     'filter',
 'Smart_watch': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Other': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Averagedailysmartphoneuseمتوسطاستخدامالهاتفا': 'single-question usage / device / platform / sleep item or derived '
                                                 'score, recode, factor or filter',
 'Numberofactivesocialmediaaccountsعددحساباتوسائلا': 'single-question usage / device / platform / sleep item or '
                                                     'derived score, recode, factor or filter',
 'Insta': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Facebook': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Twitter': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Tiktok': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Snapchat': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Linkedin': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Whatsapp': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Youtube': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Other_platforms': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                    'filter',
 'Entertainment': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Communication': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Academic_network': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                     'filter',
 'Professional_network': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                         'filter',
 'News': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Content_creation': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                     'filter',
 'Dating_meetingpeople': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                         'filter',
 'Other_purpose': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Averagebedtime': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                   'filter',
 'Averagewakeuptime': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                      'filter',
 'Doyouuseyoursmartphoneinbed': 'single-question usage / device / platform / sleep item or derived score, recode, '
                                'factor or filter',
 'Doyouuseyoursmartphoneduringlectures': 'single-question usage / device / platform / sleep item or derived score, '
                                         'recode, factor or filter',
 'Doyouuseyoursmartphoneduringstudysessions': 'single-question usage / device / platform / sleep item or derived '
                                              'score, recode, factor or filter',
 'Doyouuseyoursmartphoneduringgroupwork': 'single-question usage / device / platform / sleep item or derived score, '
                                          'recode, factor or filter',
 'socialmediahasaffectedyourstudytiming': 'single-question usage / device / platform / sleep item or derived score, '
                                          'recode, factor or filter',
 'Doyoufeelmoreattractedtowardssocialmedia': 'single-question usage / device / platform / sleep item or derived '
                                             'score, recode, factor or filter',
 'selfaddictedtosocialmedia': 'single-question usage / device / platform / sleep item or derived score, recode, '
                              'factor or filter',
 'ATTARI_2_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'ATTARI_4_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'ATTARI_7_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'ATTARI_8_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'ATTARI_10_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'ATTARI_12_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'ATTARI_total_scale': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                       'filter',
 'SPAI_total_scale': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                     'filter',
 'SMD_scale': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'SMD_cat': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'FOMO_need_belong': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                     'filter',
 'FOMO_need_popularity': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                         'filter',
 'FOMO_anxiety': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'FOMO_addiction': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                   'filter',
 'FOMO_total_scale': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                     'filter',
 'Household_income_cat': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                         'filter',
 'health_coverage': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                    'filter',
 'Employment_2cat': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                    'filter',
 'Marital_2cat': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Factor_1': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Factor_2': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Anxiety3_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Anxiety5_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Anxiety4_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Anxiety2_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Anxiety1_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'SMD_3_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'SMD_2_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'SMD_1_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Factor_3': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'LSMDS': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Factor_3_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'LSMDS_rev': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'filter_$': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Health_coverage_2cat': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                         'filter',
 'Drink_alcohol_2cat': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                       'filter',
 'Cigarette_smoke_2cat': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                         'filter',
 'WHO_total': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'WHO_2cat': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Bedtime': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Wakeuptime': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter',
 'Use_smartphone_bed': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                       'filter',
 'Use_smartphone_lecture': 'single-question usage / device / platform / sleep item or derived score, recode, factor '
                           'or filter',
 'Use_smartphone_study_session': 'single-question usage / device / platform / sleep item or derived score, recode, '
                                 'factor or filter',
 'Use_smartphone_work': 'single-question usage / device / platform / sleep item or derived score, recode, factor or '
                        'filter',
 'SMD_2cat': 'single-question usage / device / platform / sleep item or derived score, recode, factor or filter'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d.columns = [c.replace("\u200e", "").strip() for c in d.columns]
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
