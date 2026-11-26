#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Dataset_of_Questionnaire_Result_from_the_respondents_of_Awareness_to_Register_Halal_Certification/17078381
# DOI: 10.6084/m9.figshare.17078381 (data)
#   Oemar H, Prasetyaningsih E, Abu Bakar SZ, Djamaludin D, Septiani A (2022). Dataset of Questionnaire Result of
#   Awareness to Register Halal Certification [Data set]. figshare.
# License: CC BY 4.0 (figshare record metadata)
# Data: one CSV with a two-row header (construct groups above, item headers below), 100 food micro/small-enterprise
#   owners in West Java without a halal certificate. Every item is observed on 1-5, so 1-5 (five-point) is the range.
# Tables, one per construct named in the header's group row, item = the code that opens each item header (e.g.
#   "KH1 Halal animals are slaughtered ..." -> KH1): _knowledge (KH1-4, knowledge of halal), _benefits (PB1-4,
#   perception of benefits), _procedures (PP1-4, perception of procedures), _awareness (HA1-4, halal awareness),
#   _attitude (AHC1-4, attitude to produce halal products), _intention (IHC1-4, intention to register).
#   The deposit's own No column is the id.
# Covariates: cov_gender, cov_age_group, cov_religion, cov_product_type, cov_business_scale. Business location
#   (Bandung vs elsewhere in West Java) dropped under the geographic rule; the consent tick, the constant
#   certification screener and the empty follow-up question are not carried.
# PII: none (8 text columns screened; all are categorical).
# Item text: not shipped -- the headers are the English stems, but no response anchors are given in the deposit, and
#   the instrument is unidentified.
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
URL = 'https://ndownloader.figshare.com/files/33902969'
N_ROWS = 100
ID_COL = 'No'
COVS = {'Gender': 'cov_gender',
 'Age': 'cov_age_group',
 'Religion': 'cov_religion',
 'Business product type': 'cov_product_type',
 'Business Scale (before 2020)': 'cov_business_scale'}
COV_MAPS = {'cov_gender': {'Female': 'female', 'Male': 'male'},
 'cov_age_group': {'> 40 Years': '41+',
                   '26-40 Years': '26-40',
                   '21-25 Years': '21-25',
                   '17 - 20 Years': '17-20',
                   '< 17 Years': 'under_17'},
 'cov_religion': {'Islam': 'islam', 'Katolik': 'catholic', 'Protestan': 'protestant'},
 'cov_product_type': {'Archipelago food': 'archipelago_food',
                      'Snack': 'snack',
                      'Bread / cake': 'bread_cake',
                      'Chinese/Korean/Japanese food': 'east_asian_food'},
 'cov_business_scale': {'Micro (Income/turnover < 25 million/month or < 300 million/year)': 'micro',
                        'Small ( Income/turnover 25 million - 200 million/month or 300 million -2.5 billion/year)': 'small'}}
RENAME = {'KH1 Halal animals are slaughtered not following Islamic Sharia is non-halal (haram)': 'KH1',
 'KH2 Products containing alcohol used in the production process are non-halal (haram)': 'KH2',
 'KH3 Pork and its derivation used in the production process are non-halal (haram)': 'KH3',
 'KH4 Equipment used to produce halal food must be kept separate from equipment used to produce non-halal  food': 'KH4',
 'PB1 Halal certificate can be used as a promotional tool': 'PB1',
 'PB2 The ownership of Halal certificate increases consumer trust in MSE products.': 'PB2',
 'PB3 The Halal certificate contributes in the development of MSE performance': 'PB3',
 'PB4 Halal certificate will make MSEs more competitive': 'PB4',
 'PP1 The MSE has sufficient information of the halal certification process': 'PP1',
 'PP2 Halal Certification is a relatively simple process': 'PP2',
 'PP3 The cost of maintaining halal certification is cheap for MSE': 'PP3',
 'PP4 The time of obtaining halal certification is relatively quick': 'PP4',
 'HA1 The MSE is aware of the importance of producing halal food': 'HA1',
 'HA2 The MSE is aware of the importance of using halal raw materials': 'HA2',
 'HA3 The MSE is aware of the importance of a halal certificate': 'HA3',
 'HA4 The MSE is aware of the rigorous certification process.': 'HA4',
 "AHC1 The MSE is always concerned about a product's halal issue": 'AHC1',
 'AHC2 As a food producer, the MSE always concerned that their customers purchase products that following  Islamic Sharia.': 'AHC2',
 'AHC3 The MSE is always concerned with producing halal products.': 'AHC3',
 'AHC4 The MSE ensures that the raw materials are halal at all times.': 'AHC4',
 'IHC1 Although the MSE ensured that halal materials were used, the MSE is still in charge of halal certification': 'IHC1',
 'IHC2 The MSE must try to comply halal quality standards to obtain halal certification': 'IHC2',
 'IHC3 The MSE will apply the Halal assurance system in their business': 'IHC3',
 'IHC4 The MSE will register the products of MSEs to obtain halal certification': 'IHC4'}
BLOCKS = {'oemar_2022_halal_knowledge': ['KH1', 'KH2', 'KH3', 'KH4'],
 'oemar_2022_halal_benefits': ['PB1', 'PB2', 'PB3', 'PB4'],
 'oemar_2022_halal_procedures': ['PP1', 'PP2', 'PP3', 'PP4'],
 'oemar_2022_halal_awareness': ['HA1', 'HA2', 'HA3', 'HA4'],
 'oemar_2022_halal_attitude': ['AHC1', 'AHC2', 'AHC3', 'AHC4'],
 'oemar_2022_halal_intention': ['IHC1', 'IHC2', 'IHC3', 'IHC4']}
# (lo, hi) response range per table
RANGES = {'oemar_2022_halal_knowledge': (1, 5),
 'oemar_2022_halal_benefits': (1, 5),
 'oemar_2022_halal_procedures': (1, 5),
 'oemar_2022_halal_awareness': (1, 5),
 'oemar_2022_halal_attitude': (1, 5),
 'oemar_2022_halal_intention': (1, 5)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Unnamed: 1': 'consent tick',
 'Business Location': 'geographic, dropped',
 'Food/beverage products that I produce': 'constant screener',
 '(Additional question, for those whose products have ever had a halal certificate)My product has already received halal certification and is currently not/has not extended the halal certification, because:': 'empty '
                                                                                                                                                                                                                 'follow-up'}


def load(content):
    d = pd.read_csv(io.BytesIO(content), header=1)
    return d.rename(columns={"Unnamed: 0": "No"})


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
