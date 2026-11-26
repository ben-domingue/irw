#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/THE_EFFECT_OF_BRAND_EXPERIENCE_ADVERTISEMENT_AND_BRAND_BENEFITS_ON_BRAND_LOYALTY_OF_KOREAN_SKINCARE_PRODUCTS_AMONG_GENERATION_Z_IN_INDONESIA/33255801
# DOI: 10.6084/m9.figshare.33255801 (data)
#   Maydeline G, Tambunan D, Sebayang TE (2026). The effect of brand experience, advertisement, and brand benefits on
#   brand loyalty of Korean skincare products among Generation Z in Indonesia [Data set]. figshare.
# License: CC BY 4.0 (figshare record metadata)
# Data: Raw Survey Respondent Data.xlsx, a Google Forms export of 261 rows; 8 rows stop at the screeners (7 never used
#   Korean skincare, 1 blank), leaving 253 Indonesian Gen Z respondents (record: 240 targeted). 24 English statements,
#   every one observed on 1-5 (five-point agreement), so 1-5 is taken as the range.
# Tables: the record names four constructs (brand experience, advertisement, brand benefits, brand loyalty) but the
#   deposit does not say which statement belongs to which. The grouping is IRW's reading of the stems, in questionnaire
#   order: statements 1-7 (interest, impression, enjoyment, online shopping for the products) -> _brand_experience;
#   8-14 (ad familiarity, celebrity endorsers, models in ads) -> _advertisement; 15-21 (benefits, quality, design, environment, confidence)
#   -> _brand_benefits; 22-24 (loyal, choose, recommend) -> _brand_loyalty. The headers are the full statements, so
#   item = construct code + position within the block (be1-be7, ad1-ad7, bb1-bb7, bl1-bl3), assigned from the
#   header order; RENAME below holds the exact statement for every code. No respondent id, so id = row order.
# Covariates: cov_age_group, cov_gender, cov_occupation, cov_education. Domicile (city) dropped under the geographic
#   rule; the timestamp, the constant age screener, the screeners and the consent tick are not carried.
# PII: none (no name, email or phone columns; 9 text columns screened).
# Item text: not shipped -- the headers are the English stems, but no response anchors are given anywhere in the
#   deposit, and the instruments are unidentified.
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
URL = 'https://ndownloader.figshare.com/files/67547631'
N_ROWS = 261
ID_COL = None
COVS = {'Age': 'cov_age_group', 'Gender': 'cov_gender', 'Occupation': 'cov_occupation', 'Education Level': 'cov_education'}
COV_MAPS = {'cov_age_group': {'14-15': '14-15',
                   '16-17': '16-17',
                   '18-19': '18-19',
                   '20-21': '20-21',
                   '22-23': '22-23',
                   '24-25': '24-25',
                   '26-27': '26-27',
                   '28-29': '28-29'},
 'cov_gender': {'Female': 'female', 'Male': 'male'},
 'cov_occupation': {'University Student': 'university_student',
                    'Private-Sector Employee': 'private_employee',
                    'Entrepreneur': 'entrepreneur'},
 'cov_education': {'Bachelor': 'bachelor',
                   'Senior High School (SHS)': 'senior_high',
                   'Vocational High School': 'vocational_high',
                   'Magister': 'master',
                   'Diploma': 'diploma',
                   'Junior High School (SHS)': 'junior_high',
                   'Diploma (D1-D3)': 'diploma'}}
RENAME = {'I am interested in Korean skincare products': 'be1',
 'I have a positive impression of Korean skincare products': 'be2',
 'I enjoy using Korean skincare products': 'be3',
 'I am more interested in shopping online because of Korean skincare products': 'be4',
 'I am considering shopping online because of Korean skincare products': 'be5',
 'I find shopping for Korean skincare products on online or e-commerce platforms more convenient': 'be6',
 'I feel more confident shopping for Korean skincare products through online platforms or e-commerce sites.': 'be7',
 'I’ve become more familiar with Korean skincare products after seeing their ads repeatedly in various places': 'ad1',
 'I feel that Korean skincare products promoted by celebrities are of good quality': 'ad2',
 'I feel that celebrity endorsements increase my loyalty to Korean skincare products': 'ad3',
 'I feel that the use of celebrities in ads increases my interest in purchasing Korean skincare products': 'ad4',
 'I become more interested in Korean skincare products if the models in the ads are attractive': 'ad5',
 'I’m willing to pay more for Korean skincare products if the models in the ads are attractive': 'ad6',
 'I feel more confident after using Korean skincare products if the models in the ads are attractive': 'ad7',
 'I feel that Korean skincare products provide benefits that meet my needs': 'bb1',
 'I feel that Korean skincare products are of good quality': 'bb2',
 'I feel that Korean skincare products have an aesthetically appealing design': 'bb3',
 'I buy Korean skincare products because I find them appealing': 'bb4',
 'I’m happy to own Korean skincare products': 'bb5',
 'I feel that Korean skincare products reflect my concern for the environment': 'bb6',
 'I feel more confident when using Korean skincare products': 'bb7',
 'I am a loyal customer of Korean skincare products': 'bl1',
 'I tend to choose Korean skincare products when they’re available': 'bl2',
 'I would recommend Korean skincare products to others': 'bl3'}
BLOCKS = {'maydeline_2026_brand_experience': ['be1', 'be2', 'be3', 'be4', 'be5', 'be6', 'be7'],
 'maydeline_2026_advertisement': ['ad1', 'ad2', 'ad3', 'ad4', 'ad5', 'ad6', 'ad7'],
 'maydeline_2026_brand_benefits': ['bb1', 'bb2', 'bb3', 'bb4', 'bb5', 'bb6', 'bb7'],
 'maydeline_2026_brand_loyalty': ['bl1', 'bl2', 'bl3']}
# (lo, hi) response range per table
RANGES = {'maydeline_2026_brand_experience': (1, 5),
 'maydeline_2026_advertisement': (1, 5),
 'maydeline_2026_brand_benefits': (1, 5),
 'maydeline_2026_brand_loyalty': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Timestamp': 'not a covariate',
 'How old are you?': 'constant screener',
 'Have you ever purchased or used Korean skincare products?': 'screener',
 'Have you ever used digital/e-commerce platforms (e.g., Shopee, Tokopedia, TikTok Shop, Lazada, etc.) to search for information and purchase skincare products?': 'screener',
 'Domicile': 'geographic, dropped',
 'hereby state that I agree to voluntarily participate and consent to providing the information or answers required for research purposes.': 'consent '
                                                                                                                                             'tick'}


def load(content):
    return pd.read_excel(io.BytesIO(content))


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d = d[d[[c for v in BLOCKS.values() for c in v]].notna().any(axis=1)].copy()
    assert len(d) == 253, len(d)
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
