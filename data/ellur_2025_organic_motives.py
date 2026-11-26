#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/xpdr55sbw6
# DOI: 10.17632/xpdr55sbw6 (data)
#   Ellur A (2025). Organic Food Consumers Dataset [Data set]. Mendeley Data.
# License: CC BY 4.0 (Mendeley record metadata)
# Data: "OrganicFood for Factor Analysis Mendeley.xlsx", Sheet1: 401 Indian organic-food consumers (the deposit's
#   Customer No.), each answer stored twice, as the text the respondent chose and as a code. The "metadata" sheet
#   gives the codes; for the battery shipped here the code equals the agreement position (1 = Strongly disagree ...
#   5 = Strongly agree), checked against the text columns. The other two files (527 rows for logistic regression,
#   401 for clustering) are subsets/recodes of the same survey and are not read.
# Tables: _organic_motives, one table of the 8 statements that every respondent answered on the same agreement
#   scale ("I intend to buy organic food for long term health benefits", "... because my peers buy them",
#   "... as a status symbol", ...), item = the deposit's own short column name (Purchase_regularity ... Fashion_trend), except three
#   renamed so the covariate lint does not read them as demographics: Health_benefits -> Longterm_benefits,
#   Environment_friendly -> Eco_friendly, Status_symbol -> Prestige_symbol.
#   The rest of the questionnaire is single questions with their own response sets or skip-routed loyalty items
#   (code 6 = not asked); not shipped.
# Covariates: cov_age_group, cov_gender, cov_education, cov_occupation, cov_living_status, cov_household_income, from
#   the text columns. City of residence dropped under the geographic rule. The handful of free-text "Other (Please
#   specify)" occupations are collapsed to "other".
# PII: none (39 text columns screened; the free-text occupations name jobs, not people).
# Item text: not shipped -- the stems are the text column headers, but the instrument is unidentified and the 8
#   statements are a subset of a longer questionnaire.
import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://data.mendeley.com/public-files/datasets/xpdr55sbw6/files/139aa97a-262c-4f6b-a19e-bbb341e1d307/file_downloaded'
N_ROWS = 401
ID_COL = 'Customer No.'
COVS = {'Age of the Respondent': 'cov_age_group',
 'Gender of Respondent': 'cov_gender',
 'Highest Education': 'cov_education',
 'Occupation1': 'cov_occupation',
 'Living Status': 'cov_living_status',
 'Household income per month: (household includes all members of your immediate family)': 'cov_household_income'}
COV_MAPS = {'cov_age_group': {'30 or below': '30_or_below',
                   '31-40': '31-40',
                   '41-50': '41-50',
                   '51-60': '51-60',
                   'Above 60': 'over_60'},
 'cov_gender': {'Female': 'female', 'Male': 'male', 'Other': 'other'},
 'cov_education': {'Post-graduate (Degree or Diploma)': 'postgraduate',
                   'Graduate (Degree or Diploma)': 'graduate',
                   'Professional (CA, MBBS, LLB, etc.)': 'professional',
                   'Doctorate (PhD)': 'doctorate',
                   'Completed senior secondary school (class 12th)': 'senior_secondary',
                   'Others': 'other'},
 'cov_occupation': {'Salaried': 'salaried',
                    'Self-employed - business owner': 'business_owner',
                    'Student': 'student',
                    'Self-employed - others': 'self_employed_other',
                    'Homemaker': 'homemaker',
                    'Retired': 'retired',
                    'Other': 'other'},
 'cov_living_status': {'Live in a joint family': 'joint_family',
                       'Living with spouse': 'with_spouse',
                       'Living alone': 'alone',
                       'Living with others (Friends etc.)': 'with_others'},
 'cov_household_income': {'INR 50000 - 1,00,000 (one lac)': '50k-100k',
                          'INR 1,00,001 - 1,50,000 ( or one lac fifty thousand)': '100k-150k',
                          'INR 1,50,001 - 3,00,000 (three lac)': '150k-300k',
                          'INR 3,00,001 - 5,00,000 (five lac)': '300k-500k',
                          'INR 5,00,001 - 10,00,000 (ten lac)': '500k-1m',
                          'Above 10,00,000 per month': 'over_1m'}}
RENAME = {'Health_benefits': 'Longterm_benefits', 'Environment_friendly': 'Eco_friendly', 'Status_symbol': 'Prestige_symbol'}
BLOCKS = {'ellur_2025_organic_motives': ['Longterm_benefits',
                                'Purchase_regularity',
                                'Premium_willingness',
                                'Certified_willingness',
                                'Eco_friendly',
                                'Peer_influence',
                                'Prestige_symbol',
                                'Fashion_trend']}
# (lo, hi) response range per table
RANGES = {'ellur_2025_organic_motives': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Age': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, multi-select or '
        'skip-routed loyalty items)',
 'Gender': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, multi-select '
           'or skip-routed loyalty items)',
 'Household_income': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                     'multi-select or skip-routed loyalty items)',
 'Highest_education': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                      'multi-select or skip-routed loyalty items)',
 'Occupation': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
               'multi-select or skip-routed loyalty items)',
 'Living_status': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                  'multi-select or skip-routed loyalty items)',
 'City currently residing in': 'geographic, dropped',
 'Do you buy Organic food?': 'outside the 8-item purchase-motive battery (single questions, coded twins of text '
                             'columns, multi-select or skip-routed loyalty items)',
 'Which of the following is a reason for not buying organic food? You can select more than one option.': 'outside '
                                                                                                         'the 8-item '
                                                                                                         'purchase-motive '
                                                                                                         'battery '
                                                                                                         '(single '
                                                                                                         'questions, '
                                                                                                         'coded '
                                                                                                         'twins of '
                                                                                                         'text '
                                                                                                         'columns, '
                                                                                                         'multi-select '
                                                                                                         'or '
                                                                                                         'skip-routed '
                                                                                                         'loyalty '
                                                                                                         'items)',
 'For which of the following organic food categories, do you generally purchase organic? You can select more than one option': 'outside '
                                                                                                                               'the '
                                                                                                                               '8-item '
                                                                                                                               'purchase-motive '
                                                                                                                               'battery '
                                                                                                                               '(single '
                                                                                                                               'questions, '
                                                                                                                               'coded '
                                                                                                                               'twins '
                                                                                                                               'of '
                                                                                                                               'text '
                                                                                                                               'columns, '
                                                                                                                               'multi-select '
                                                                                                                               'or '
                                                                                                                               'skip-routed '
                                                                                                                               'loyalty '
                                                                                                                               'items)',
 'How long have you been buying organic food?': 'outside the 8-item purchase-motive battery (single questions, coded '
                                                'twins of text columns, multi-select or skip-routed loyalty items)',
 'Num_years': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
              'multi-select or skip-routed loyalty items)',
 'How regularly do you purchase organic food?': 'outside the 8-item purchase-motive battery (single questions, coded '
                                                'twins of text columns, multi-select or skip-routed loyalty items)',
 'Purchase_frequency': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                       'multi-select or skip-routed loyalty items)',
 'Are you aware of the existence of organic certification labels? (Normally displayed on a product)': 'outside the '
                                                                                                      '8-item '
                                                                                                      'purchase-motive '
                                                                                                      'battery '
                                                                                                      '(single '
                                                                                                      'questions, '
                                                                                                      'coded twins '
                                                                                                      'of text '
                                                                                                      'columns, '
                                                                                                      'multi-select '
                                                                                                      'or '
                                                                                                      'skip-routed '
                                                                                                      'loyalty '
                                                                                                      'items)',
 'Certification_awareness': 'outside the 8-item purchase-motive battery (single questions, coded twins of text '
                            'columns, multi-select or skip-routed loyalty items)',
 'I look for organic certification labels on the packaging while buying organic food': 'outside the 8-item '
                                                                                       'purchase-motive battery '
                                                                                       '(single questions, coded '
                                                                                       'twins of text columns, '
                                                                                       'multi-select or skip-routed '
                                                                                       'loyalty items)',
 'Certification_cautious': 'outside the 8-item purchase-motive battery (single questions, coded twins of text '
                           'columns, multi-select or skip-routed loyalty items)',
 'For which of the following products do you look for certification labels? You can tick more than option': 'outside '
                                                                                                            'the '
                                                                                                            '8-item '
                                                                                                            'purchase-motive '
                                                                                                            'battery '
                                                                                                            '(single '
                                                                                                            'questions, '
                                                                                                            'coded '
                                                                                                            'twins '
                                                                                                            'of text '
                                                                                                            'columns, '
                                                                                                            'multi-select '
                                                                                                            'or '
                                                                                                            'skip-routed '
                                                                                                            'loyalty '
                                                                                                            'items)',
 'Do you look for multiple certification labels when buying organic food?': 'outside the 8-item purchase-motive '
                                                                            'battery (single questions, coded twins '
                                                                            'of text columns, multi-select or '
                                                                            'skip-routed loyalty items)',
 'Multiple_certification1': 'outside the 8-item purchase-motive battery (single questions, coded twins of text '
                            'columns, multi-select or skip-routed loyalty items)',
 'Have you visited the website of any organic certifying agency?': 'outside the 8-item purchase-motive battery '
                                                                   '(single questions, coded twins of text columns, '
                                                                   'multi-select or skip-routed loyalty items)',
 'Certifyingagency_website': 'outside the 8-item purchase-motive battery (single questions, coded twins of text '
                             'columns, multi-select or skip-routed loyalty items)',
 'Are you aware of Organic brands?': 'outside the 8-item purchase-motive battery (single questions, coded twins of '
                                     'text columns, multi-select or skip-routed loyalty items)',
 'Brand_awareness': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                    'multi-select or skip-routed loyalty items)',
 'Do you look for the brand name when buying Organic Food?': 'outside the 8-item purchase-motive battery (single '
                                                             'questions, coded twins of text columns, multi-select '
                                                             'or skip-routed loyalty items)',
 'Brand_cautious': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                   'multi-select or skip-routed loyalty items)',
 'I always buy from one brand when going for organic purchase': 'outside the 8-item purchase-motive battery (single '
                                                                'questions, coded twins of text columns, '
                                                                'multi-select or skip-routed loyalty items)',
 'Brand_loyalty': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                  'multi-select or skip-routed loyalty items)',
 'Do you buy non-organic foods from the same brand?': 'outside the 8-item purchase-motive battery (single questions, '
                                                      'coded twins of text columns, multi-select or skip-routed '
                                                      'loyalty items)',
 'Nonorganicbrand': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                    'multi-select or skip-routed loyalty items)',
 'Since how long have you been buying from this Brand?': 'outside the 8-item purchase-motive battery (single '
                                                         'questions, coded twins of text columns, multi-select or '
                                                         'skip-routed loyalty items)',
 'Num_of_years_brand': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                       'multi-select or skip-routed loyalty items)',
 'I will recommend this brand to someone who seeks my advice for organic food.': 'outside the 8-item purchase-motive '
                                                                                 'battery (single questions, coded '
                                                                                 'twins of text columns, '
                                                                                 'multi-select or skip-routed '
                                                                                 'loyalty items)',
 'Brand_recommendation': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                         'multi-select or skip-routed loyalty items)',
 'Is the brand that you are buying from certified by organic certification labels?': 'outside the 8-item '
                                                                                     'purchase-motive battery '
                                                                                     '(single questions, coded twins '
                                                                                     'of text columns, multi-select '
                                                                                     'or skip-routed loyalty items)',
 'Brand_certification': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                        'multi-select or skip-routed loyalty items)',
 'For which of the following information are you willing to pay a price premium? You can select more than one option.': 'outside '
                                                                                                                        'the '
                                                                                                                        '8-item '
                                                                                                                        'purchase-motive '
                                                                                                                        'battery '
                                                                                                                        '(single '
                                                                                                                        'questions, '
                                                                                                                        'coded '
                                                                                                                        'twins '
                                                                                                                        'of '
                                                                                                                        'text '
                                                                                                                        'columns, '
                                                                                                                        'multi-select '
                                                                                                                        'or '
                                                                                                                        'skip-routed '
                                                                                                                        'loyalty '
                                                                                                                        'items)',
 'I intend to buy organic food for long term health benefits': 'outside the 8-item purchase-motive battery (single '
                                                               'questions, coded twins of text columns, multi-select '
                                                               'or skip-routed loyalty items)',
 'I will regularly purchase organic food.': 'outside the 8-item purchase-motive battery (single questions, coded '
                                            'twins of text columns, multi-select or skip-routed loyalty items)',
 'I am willing to pay a higher price for organic food relative to non-organic food.': 'outside the 8-item '
                                                                                      'purchase-motive battery '
                                                                                      '(single questions, coded '
                                                                                      'twins of text columns, '
                                                                                      'multi-select or skip-routed '
                                                                                      'loyalty items)',
 'I am willing to buy organic food if they are certified.': 'outside the 8-item purchase-motive battery (single '
                                                            'questions, coded twins of text columns, multi-select or '
                                                            'skip-routed loyalty items)',
 'I am willing to buy organic food because they are environmentally friendly': 'outside the 8-item purchase-motive '
                                                                               'battery (single questions, coded '
                                                                               'twins of text columns, multi-select '
                                                                               'or skip-routed loyalty items)',
 'I am willing to buy organic food because my peers buy them': 'outside the 8-item purchase-motive battery (single '
                                                               'questions, coded twins of text columns, multi-select '
                                                               'or skip-routed loyalty items)',
 'I intend to buy organic food as a status symbol.': 'outside the 8-item purchase-motive battery (single questions, '
                                                     'coded twins of text columns, multi-select or skip-routed '
                                                     'loyalty items)',
 'I intend to buy organic food because it is fashionable': 'outside the 8-item purchase-motive battery (single '
                                                           'questions, coded twins of text columns, multi-select or '
                                                           'skip-routed loyalty items)',
 'Which is your preferred mode to buy organic food. You can tick more than one option.': 'outside the 8-item '
                                                                                         'purchase-motive battery '
                                                                                         '(single questions, coded '
                                                                                         'twins of text columns, '
                                                                                         'multi-select or '
                                                                                         'skip-routed loyalty items)',
 'I always buy from this store when going for organic food purchase (For instance, from Natureâ€™s Basket, More, BigBazar etc.)': 'outside '
                                                                                                                                  'the '
                                                                                                                                  '8-item '
                                                                                                                                  'purchase-motive '
                                                                                                                                  'battery '
                                                                                                                                  '(single '
                                                                                                                                  'questions, '
                                                                                                                                  'coded '
                                                                                                                                  'twins '
                                                                                                                                  'of '
                                                                                                                                  'text '
                                                                                                                                  'columns, '
                                                                                                                                  'multi-select '
                                                                                                                                  'or '
                                                                                                                                  'skip-routed '
                                                                                                                                  'loyalty '
                                                                                                                                  'items)',
 'Outlet_loyalty1': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                    'multi-select or skip-routed loyalty items)',
 'I rarely consider switching to another physical store when buying organic food.': 'outside the 8-item '
                                                                                    'purchase-motive battery (single '
                                                                                    'questions, coded twins of text '
                                                                                    'columns, multi-select or '
                                                                                    'skip-routed loyalty items)',
 'Outlet_loyalty2': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                    'multi-select or skip-routed loyalty items)',
 'I will recommend this store to other people': 'outside the 8-item purchase-motive battery (single questions, coded '
                                                'twins of text columns, multi-select or skip-routed loyalty items)',
 'Store_recommendation': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                         'multi-select or skip-routed loyalty items)',
 'I always buy from this website/app when going for organic food purchase (For instance, from Big Basket, Grofers, Amazon, Flipkart, Jio Mart, TATA Starquik etc.)Â·': 'outside '
                                                                                                                                                                       'the '
                                                                                                                                                                       '8-item '
                                                                                                                                                                       'purchase-motive '
                                                                                                                                                                       'battery '
                                                                                                                                                                       '(single '
                                                                                                                                                                       'questions, '
                                                                                                                                                                       'coded '
                                                                                                                                                                       'twins '
                                                                                                                                                                       'of '
                                                                                                                                                                       'text '
                                                                                                                                                                       'columns, '
                                                                                                                                                                       'multi-select '
                                                                                                                                                                       'or '
                                                                                                                                                                       'skip-routed '
                                                                                                                                                                       'loyalty '
                                                                                                                                                                       'items)',
 'Website_loyalty1': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                     'multi-select or skip-routed loyalty items)',
 'I rarely consider switching to another platform when buying organic food.': 'outside the 8-item purchase-motive '
                                                                              'battery (single questions, coded '
                                                                              'twins of text columns, multi-select '
                                                                              'or skip-routed loyalty items)',
 'Website_loyalty2': 'outside the 8-item purchase-motive battery (single questions, coded twins of text columns, '
                     'multi-select or skip-routed loyalty items)',
 'I will recommend this platform to other people': 'outside the 8-item purchase-motive battery (single questions, '
                                                   'coded twins of text columns, multi-select or skip-routed loyalty '
                                                   'items)',
 'Website_recommendation': 'outside the 8-item purchase-motive battery (single questions, coded twins of text '
                           'columns, multi-select or skip-routed loyalty items)'}


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name="Sheet1")


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    occ = d["Occupation1"].astype("string")
    d["Occupation1"] = occ.where(~occ.str.startswith("Other (Please specify)"), "Other").str.replace("â€“", "-", regex=False)
    return d


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == N_ROWS, len(d)
    d = d.rename(columns=RENAME)
    d = prep(d)
    if ID_COL:
        assert d[ID_COL].is_unique, "duplicate ids"
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
    covs = list(COVS.values())
    items_all = [c for v in BLOCKS.values() for c in v]
    assert len(items_all) == len(set(items_all)), "item in two tables"
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
