#!/usr/bin/env python3
# Source: https://osf.io/xmfn6/
# DOI: osf.io/xmfn6 (no DOI minted) (data)
#   Sorokowska, A., & Chabin, D. (2024). Food neophobia and olfactory perception in young children [Dataset]. OSF.
# License: CC BY 4.0 (OSF node, public)
# Data: 273 Polish children aged 3-9 and their caregivers (Sorokowska & Chabin, food neophobia and olfaction): child
#   self-report Child Food Neophobia Scale (8 items, 1-5) and general neophobia (CNS9-14), a 12-odor identification
#   test (correct = 1) with liking ratings (1-5), and caregiver questionnaires -- child general neophobia (1-7), the
#   caregiver's own general neophobia (1-7), CFNS parent report (1-7), the caregiver's Food Neophobia Scale (1-7),
#   child anxiety (0-4) and the Comprehensive Feeding Practices Questionnaire (48 items as shipped; CFPQ41, marked
#   'removed' by the depositors, is not). Only the raw items are shipped -- the deposit's *R reverse-scored copies
#   and the Odor Sign Awareness items (present only as R copies) are not. Caregiver blocks have ~80 missing where no
#   caregiver data were returned.
# Tables: one per instrument; item = the deposit name (odor items renamed id_<odor> / like_<odor>; GNparent1 -> GN1,
#   the sixth general-neophobia item 'GN' -> GN6).
# Covariates: cov_age (child, years), cov_sex
# PII: none; free-text health, chronic-disease, medication and diet fields dropped (clinical free-text rule)
# Item text: not shipped -- the codebook docx describes the measures; CFNS, FNS and CFPQ are published instruments
# Built by the 2026-11-20 repos leads (lane 2) from a shared template; one self-contained script per deposit.

import io
import os
import sys
import tempfile
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "irw-pipeline/1.0"}

SOURCES = [{'url': 'https://osf.io/download/4yx7c/',
  'kind': 'excel',
  'read_kw': {},
  'n_rows': 273,
  'range': (1, 7),
  'blocks': {'sorokowska_2024_child_food_neophobia': ['CFNS1',
                                                      'CFNS2',
                                                      'CFNS3',
                                                      'CFNS4',
                                                      'CFNS5',
                                                      'CFNS6',
                                                      'CFNS7',
                                                      'CFNS8'],
             'sorokowska_2024_child_general_neophobia': ['CNS9', 'CNS10', 'CNS11', 'CNS12', 'CNS13', 'CNS14'],
             'sorokowska_2024_odor_identification': ['I1_1correct0wrong',
                                                     'I201',
                                                     'I301',
                                                     'I401',
                                                     'I501',
                                                     'I601',
                                                     'I701',
                                                     'I801',
                                                     'I901',
                                                     'I1001',
                                                     'I1101',
                                                     'I1201'],
             'sorokowska_2024_odor_liking': ['I1apple_liking_1to5',
                                             'I2bananaL',
                                             'I3butterL',
                                             'I4coffeeL',
                                             'I5grassL',
                                             'I6fishL',
                                             'I7flowerL',
                                             'I8lemonL',
                                             'I9onionL',
                                             'I10orangeL',
                                             'I11peachL',
                                             'I12strawberryL'],
             'sorokowska_2024_cgn_caregiver': ['CGN1', 'CGN2', 'CGN3', 'CGN4', 'CGN5', 'CGN6'],
             'sorokowska_2024_parent_general_neophobia': ['GNparent1', 'GN2', 'GN3', 'GN4', 'GN5', 'GN'],
             'sorokowska_2024_cfns_parent_report': ['CFNSparent1',
                                                    'CFNSparent2',
                                                    'CFNSparent3',
                                                    'CFNSparent4',
                                                    'CFNSparent5',
                                                    'CFNSparent6',
                                                    'CFNSparent7',
                                                    'CFNSparent8'],
             'sorokowska_2024_fns_parent': ['FNSparent1',
                                            'FNSparent2',
                                            'FNSparent3',
                                            'FNSparent4',
                                            'FNSparent5',
                                            'FNSparent6',
                                            'FNSparent7',
                                            'FNSparent8',
                                            'FNSparent9',
                                            'FNSparent10'],
             'sorokowska_2024_child_anxiety': ['anxiety041',
                                               'anxiety042',
                                               'anxiety043',
                                               'anxiety044',
                                               'anxiety045',
                                               'anxiety046'],
             'sorokowska_2024_cfpq': ['CFPQ1',
                                      'CFPQ2',
                                      'CFPQ3',
                                      'CFPQ4',
                                      'CFPQ5',
                                      'CFPQ6',
                                      'CFPQ7',
                                      'CFPQ8',
                                      'CFPQ9',
                                      'CFPQ10',
                                      'CFPQ11',
                                      'CFPQ12',
                                      'CFPQ13',
                                      'CFPQ14',
                                      'CFPQ15',
                                      'CFPQ16',
                                      'CFPQ17',
                                      'CFPQ18',
                                      'CFPQ19',
                                      'CFPQ20',
                                      'CFPQ21',
                                      'CFPQ22',
                                      'CFPQ23',
                                      'CFPQ24',
                                      'CFPQ25',
                                      'CFPQ26',
                                      'CFPQ27',
                                      'CFPQ28',
                                      'CFPQ29',
                                      'CFPQ30',
                                      'CFPQ31',
                                      'CFPQ32',
                                      'CFPQ33',
                                      'CFPQ34',
                                      'CFPQ35',
                                      'CFPQ36',
                                      'CFPQ37',
                                      'CFPQ38',
                                      'CFPQ39',
                                      'CFPQ40',
                                      'CFPQ42',
                                      'CFPQ43',
                                      'CFPQ44',
                                      'CFPQ45',
                                      'CFPQ46',
                                      'CFPQ47',
                                      'CFPQ48',
                                      'CFPQ49']},
  'covs': {'childage': 'cov_age', 'sexmale0female1': 'cov_sex'},
  'cov_maps': {'cov_sex': {0: 'male', 1: 'female'}},
  'not_shipped': {'parentaldata0no1yes': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                         'background or check (not carried)',
                  'Infection_selfreport0no1yes2unsure': 'reverse-scored copy, section header, composite, threshold, '
                                                        'caregiver background or check (not carried)',
                  'noteshealth': 'free-text health/medication/diet field (clinical free-text rule): dropped',
                  'Health_assessment_caregiver': 'free-text health/medication/diet field (clinical free-text rule): '
                                                 'dropped',
                  'Chronic_diseases': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                      'background or check (not carried)',
                  'Chronic_disease_type': 'free-text health/medication/diet field (clinical free-text rule): dropped',
                  'Smell_dysfunctions': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                        'background or check (not carried)',
                  'Smell_dysfunction_type': 'free-text health/medication/diet field (clinical free-text rule): '
                                            'dropped',
                  'Medication': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                                'check (not carried)',
                  'Medication_type': 'free-text health/medication/diet field (clinical free-text rule): dropped',
                  'Dietary_restraints': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                        'background or check (not carried)',
                  'Dietary_restraints_type': 'free-text health/medication/diet field (clinical free-text rule): '
                                             'dropped',
                  'ChildFoodNeophobiaScale_1to5': 'reverse-scored copy, section header, composite, threshold, '
                                                  'caregiver background or check (not carried)',
                  'CFNS1R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                            'check (not carried)',
                  'CFNS4R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                            'check (not carried)',
                  'CFNS5R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                            'check (not carried)',
                  'CFNS8R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                            'check (not carried)',
                  'CFNS_Mean': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                               'check (not carried)',
                  'ChildGeneralNeophobia': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                           'background or check (not carried)',
                  'CNS_Mean': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                              'check (not carried)',
                  'Odor_Sign_Awareness_Scale_0to2': 'reverse-scored copy, section header, composite, threshold, '
                                                    'caregiver background or check (not carried)',
                  '@11.1R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                            'check (not carried)',
                  '@11.2R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                            'check (not carried)',
                  '@11.3R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                            'check (not carried)',
                  '@11.4R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                            'check (not carried)',
                  '@11.5R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                            'check (not carried)',
                  '@11.7R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                            'check (not carried)',
                  '@11.9R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                            'check (not carried)',
                  '@11.10R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                             'check (not carried)',
                  '@11.11R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                             'check (not carried)',
                  '@11.12R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                             'check (not carried)',
                  'OSA_Mean': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                              'check (not carried)',
                  'Odor_identification': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                         'background or check (not carried)',
                  'Identification_mean': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                         'background or check (not carried)',
                  'Liking_mean': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                                 'check (not carried)',
                  'Thresholds_odor_detection': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                               'background or check (not carried)',
                  'Butanol_threshold': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                       'background or check (not carried)',
                  'Ginger_threshold': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                      'background or check (not carried)',
                  'Caregiver_Survey': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                      'background or check (not carried)',
                  'Sex_caregiver': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                   'or check (not carried)',
                  'Caregiver_age': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                   'or check (not carried)',
                  'Caregiver_education': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                         'background or check (not carried)',
                  'Family_SES': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                                'check (not carried)',
                  'Weight_child': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                  'or check (not carried)',
                  'Height_child': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                  'or check (not carried)',
                  'Height_child_m': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                    'or check (not carried)',
                  'BMI': 'reverse-scored copy, section header, composite, threshold, caregiver background or check '
                         '(not carried)',
                  'Child_Appetite': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                    'or check (not carried)',
                  'Child_general_neophobia_caregiver': 'reverse-scored copy, section header, composite, threshold, '
                                                       'caregiver background or check (not carried)',
                  'CGN_caregiver_mean': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                        'background or check (not carried)',
                  'General_neophobia_parent': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                              'background or check (not carried)',
                  'GNparent_Mean': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                   'or check (not carried)',
                  'Childsfoodneophobiaasassessedbyparent': 'reverse-scored copy, section header, composite, '
                                                           'threshold, caregiver background or check (not carried)',
                  'CFNSparent1R': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                  'or check (not carried)',
                  'CFNSparent4R': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                  'or check (not carried)',
                  'CFNSparent5R': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                  'or check (not carried)',
                  'CFNSparent8R': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                  'or check (not carried)',
                  'meanCFNSparent': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                    'or check (not carried)',
                  'Foodneophobiaparentselfevaluation': 'reverse-scored copy, section header, composite, threshold, '
                                                       'caregiver background or check (not carried)',
                  'FNSparent1R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                                 'check (not carried)',
                  'FNSparent4R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                                 'check (not carried)',
                  'FNSparent6R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                                 'check (not carried)',
                  'FNSparent9R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                                 'check (not carried)',
                  'FNSparent10R': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                  'or check (not carried)',
                  'meanFNSparent': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                   'or check (not carried)',
                  'Childanxiety': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                  'or check (not carried)',
                  'Anxiety_Mean': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                  'or check (not carried)',
                  'ComprehensiveFeedingPracticesQuestionnaire': 'reverse-scored copy, section header, composite, '
                                                                'threshold, caregiver background or check (not '
                                                                'carried)',
                  'CFPQ16R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                             'check (not carried)',
                  'CFPQ37R': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                             'check (not carried)',
                  'CFPQ41removed': 'reverse-scored copy, section header, composite, threshold, caregiver background '
                                   'or check (not carried)',
                  'FactorsCFPQ': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                                 'check (not carried)',
                  'control': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                             'check (not carried)',
                  'regulationofemotions': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                          'background or check (not carried)',
                  'encouraging': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                                 'check (not carried)',
                  'environment': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                                 'check (not carried)',
                  'reward': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                            'check (not carried)',
                  'engagement': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                                'check (not carried)',
                  'modeling': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                              'check (not carried)',
                  'monitoring': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                                'check (not carried)',
                  'pressure': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                              'check (not carried)',
                  'restrictionshealth': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                        'background or check (not carried)',
                  'restrictionsweight': 'reverse-scored copy, section header, composite, threshold, caregiver '
                                        'background or check (not carried)',
                  'education': 'reverse-scored copy, section header, composite, threshold, caregiver background or '
                               'check (not carried)',
                  'FOOD_NEOPHOBIA_CHILD_rescaled': 'reverse-scored copy, section header, composite, threshold, '
                                                   'caregiver background or check (not carried)',
                  'FOOD_NEOPHOBIA_PARENT_rescaled': 'reverse-scored copy, section header, composite, threshold, '
                                                    'caregiver background or check (not carried)'},
  'label': 'sorokowska_2024_child_food_neophobia',
  'ranges': {'sorokowska_2024_child_food_neophobia': (1, 5),
             'sorokowska_2024_child_general_neophobia': (1, 5),
             'sorokowska_2024_odor_identification': (0, 1),
             'sorokowska_2024_odor_liking': (1, 5),
             'sorokowska_2024_child_anxiety': (0, 4),
             'sorokowska_2024_cfpq': (0, 5)},
  'item_names': {'I1_1correct0wrong': 'id_apple',
                 'I201': 'id_banana',
                 'I301': 'id_butter',
                 'I401': 'id_coffee',
                 'I501': 'id_grass',
                 'I601': 'id_fish',
                 'I701': 'id_flower',
                 'I801': 'id_lemon',
                 'I901': 'id_onion',
                 'I1001': 'id_orange',
                 'I1101': 'id_peach',
                 'I1201': 'id_strawberry',
                 'I1apple_liking_1to5': 'like_apple',
                 'I2bananaL': 'like_banana',
                 'I3butterL': 'like_butter',
                 'I4coffeeL': 'like_coffee',
                 'I5grassL': 'like_grass',
                 'I6fishL': 'like_fish',
                 'I7flowerL': 'like_flower',
                 'I8lemonL': 'like_lemon',
                 'I9onionL': 'like_onion',
                 'I10orangeL': 'like_orange',
                 'I11peachL': 'like_peach',
                 'I12strawberryL': 'like_strawberry',
                 'GNparent1': 'GN1',
                 'GN': 'GN6'}}]

# rows written per table (asserted)
EXPECT = {'sorokowska_2024_cfns_parent_report': 2068,
 'sorokowska_2024_cfpq': 12310,
 'sorokowska_2024_cgn_caregiver': 1156,
 'sorokowska_2024_child_anxiety': 1547,
 'sorokowska_2024_child_food_neophobia': 2054,
 'sorokowska_2024_child_general_neophobia': 1162,
 'sorokowska_2024_fns_parent': 2573,
 'sorokowska_2024_odor_identification': 3044,
 'sorokowska_2024_odor_liking': 3059,
 'sorokowska_2024_parent_general_neophobia': 1152}


def load(content, kind, read_kw):
    if kind == "csv":
        return pd.read_csv(io.BytesIO(content), **read_kw)
    if kind == "excel":
        return pd.read_excel(io.BytesIO(content), **read_kw)
    if kind in ("sav", "dta"):
        import pyreadstat
        with tempfile.NamedTemporaryFile(suffix="." + kind, delete=False) as fh:
            fh.write(content)
        try:
            reader = pyreadstat.read_sav if kind == "sav" else pyreadstat.read_dta
            df, _ = reader(fh.name, **read_kw)
        finally:
            os.unlink(fh.name)
        return df
    raise ValueError(kind)


def fetch(url):
    for attempt in range(6):  # Mendeley's public-files endpoint returns transient 502s
        try:
            r = requests.get(url, timeout=300, headers=UA)
        except requests.RequestException:
            time.sleep(15 * (attempt + 1))
            continue
        if r.status_code < 500:
            break
        time.sleep(20 * (attempt + 1))
    r.raise_for_status()
    return r.content


def build_source(src):
    d = load(fetch(src["url"]), src["kind"], src.get("read_kw", {}))
    d.columns = [" ".join(str(c).split()) for c in d.columns]
    d = d.rename(columns=src.get("rename", {}))
    if src.get("drop_empty_rows"):
        d = d.dropna(how="all")
    assert len(d) == src["n_rows"], (src["label"], len(d))
    before = len(d)
    if src.get("keep_col_eq"):
        col, val = src["keep_col_eq"]
        d = d[d[col] == val]
    if src.get("keep_any_item"):
        d = d[d[[c for cols in src["blocks"].values() for c in cols]].notna().any(axis=1)]
    if len(d) != before:
        print(f"{src['label']}: kept {len(d)} of {before} rows ({src.get('keep_reason', '')})")
    # The books: every source column is shipped (item or covariate), the id, or skipped for a stated reason.
    items = [c for cols in src["blocks"].values() for c in cols]
    special = [x["col"] for x in (src.get("wave"), src.get("treat")) if x]
    used = set(items) | set(src.get("covs", {})) | set(src.get("not_shipped", {})) | set(special)
    if src.get("id_col"):
        used.add(src["id_col"])
    unaccounted = [c for c in d.columns if c not in used]
    assert not unaccounted, (src["label"], unaccounted)
    missing = [c for c in used if c not in d.columns]
    assert not missing, (src["label"], missing)
    if src.get("id_col"):
        if src.get("wave"):
            assert not d.duplicated([src["id_col"], src["wave"]["col"]]).any(), "id x wave not unique"
        else:
            assert d[src["id_col"]].notna().all() and d[src["id_col"]].is_unique, "id not unique"
        d["id"] = d[src["id_col"]].astype(str)
    else:
        d["id"] = [str(k) for k in range(1, len(d) + 1)]
    if src.get("id_prefix"):
        d["id"] = src["id_prefix"] + "_" + d["id"]
    for col, bad in src.get("invalid", {}).items():
        # out-of-range codes isolated to one item: data-entry errors, set missing (see header)
        hit = d[col].isin(bad)
        print(f"{src['label']}: {col}: {int(hit.sum())} cell(s) {bad} set missing")
        d.loc[hit, col] = None
    extra = []
    for key in ("wave", "treat"):
        spec = src.get(key)
        if spec:
            m = spec.get("map")
            v = d[spec["col"]]
            if m is not None:
                bad = [x for x in v.dropna().unique() if x not in m]
                assert not bad, (key, bad)
                v = v.map(m)
            d[key] = v
            extra.append(key)
    for k, v in src.get("const", {}).items():
        d[k] = v
        extra.append(k)
    covs = []
    for col, cov in src.get("covs", {}).items():
        m = src.get("cov_maps", {}).get(cov)
        if m is not None:
            vals = d[col].map(lambda v: m.get(v, m.get(str(v).strip())) if pd.notna(v) else None)
            bad = [v for v in d[col].dropna().unique() if v not in m and str(v).strip() not in m]
            assert len(bad) == 0, (cov, bad[:10])
            d[cov] = vals
        else:
            d[cov] = d[col]
        covs.append(cov)
    for k, v in src.get("const_covs", {}).items():
        d[k] = v
        covs.append(k)
    names = src.get("item_names", {})
    out = {}
    for name, cols in src["blocks"].items():
        t = d[["id"] + extra + covs + cols].melt(id_vars=["id"] + extra + covs, var_name="item", value_name="resp")
        rec = src.get("recode", {})
        if rec:
            def _rc(v):
                if pd.isna(v):
                    return v
                k = " ".join(str(v).split())
                assert k in rec or not isinstance(v, str), (name, v)
                return rec.get(k, v)
            t["resp"] = t["resp"].map(_rc)
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        miss = src.get("missing_codes", [])
        if miss:
            t.loc[t["resp"].isin(miss), "resp"] = None
        t = t.dropna(subset=["resp"])
        t["item"] = t["item"].map(lambda c: names.get(c, c))
        lo, hi = src.get("ranges", {}).get(name, src["range"])
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        assert t["resp"].between(lo, hi).all(), (name, t["resp"].min(), t["resp"].max())
        t["resp"] = t["resp"].astype(int)
        out[name] = (t, (lo, hi))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tables = {}
    for src in SOURCES:
        for name, (t, rng) in build_source(src).items():
            tables.setdefault(name, []).append((t, rng))
    for name, parts in tables.items():
        lo = min(r[0] for _, r in parts)
        hi = max(r[1] for _, r in parts)
        t = pd.concat([p for p, _ in parts], ignore_index=True)
        lead = [c for c in ("wave", "treat") if c in t.columns]
        covs = [c for c in t.columns if c.startswith("cov_")]
        t = t[["id", "item", "resp"] + lead + covs].sort_values(["id", "item"] + lead[:1], kind="stable")
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t.columns else [])).any(), name
        assert t["id"].nunique() >= 100, (name, t["id"].nunique())
        assert t["item"].nunique() >= 3, (name, t["item"].nunique())
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        assert len(name) <= 40, name
        if EXPECT:
            assert len(t) == EXPECT[name], (name, len(t), EXPECT[name])
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    if EXPECT:
        assert set(EXPECT) == set(tables), sorted(set(EXPECT) ^ set(tables))


if __name__ == "__main__":
    main()
