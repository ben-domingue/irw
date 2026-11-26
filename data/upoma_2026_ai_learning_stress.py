#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/f26fhdpw23
# DOI: 10.17632/f26fhdpw23 (data)
#   Upoma IB, Oikya UA (2026). Generative AI, Learning Readiness, and Wellbeing: Survey Data from 412 Law Students in
#   Bangladesh [Data set]. Mendeley Data. (Consolidates the two earlier component releases 10.17632/khd668z4vr.2 and
#   10.17632/gvrcgf2rz5.1, same 412 participants; neither is in IRW.)
# License: CC BY 4.0 (Mendeley record metadata)
# Data: ai_learning_stress_clean.csv, 412 law students at a private Bangladeshi university, the deposit's NewID
#   (R0001...). README.md and AI_Learning_Stress_Master_Codebook.xlsx document every item, code and scoring rule.
# Tables, one per section/subscale in the README, item = the deposit's question number:
#   0-2 (Disagree / Neutral / Agree, or Never-Rarely / Sometimes / Often), as stored: _tam_usefulness (Q6-11),
#     _tam_ease_of_use (Q12-17), _ai_literacy_ethics (Q18-21, study-specific), _aaius (Q22-45), _gads (Q46-56),
#     _gaies_interaction (Q58-71), _gaies_frequency (Q72-81).
#     The GADS items are independence-framed and stored in their natural agreement direction; the deposit reverses
#     them only when it builds GADS_score. Shipped as stored, so higher = more independence here.
#   1-5 (Strongly disagree ... Strongly agree): _sdlrs_self_management (Q82-94), _sdlrs_self_control (Q95-109),
#     _sdlrs_desire_learning (Q110-121). Stored 0-4; the README says the administered metric is 1-5 and to add 1,
#     which this script does.
#   0-4 (Never ... Very often): _pss (Q122-131, the adapted PSS-10 with the four positive items reworded in the stress
#     direction before administration, per the README) and _ai_stressors (Q132-133, study-specific).
#   Q57 (one study-specific help-seeking item) is a single item; not shipped. The README stresses that every set is an
#   adapted administration (3-point formats for TAM/AAIUS/GADS/GAIES, reworded SDLRS and PSS items), not the
#   validated source instrument.
# Covariates: cov_age_group (Q1), cov_gender (Q2), cov_relationship (Q3), cov_semester (Q4), decoded from the codebook.
#   The AI-tool indicators are not carried.
# PII: none (the clean file has one text column, NewID; open-ended answers were withheld by the depositors).
# Item text: shipped 2026-11-25c for the two study-specific blocks (ai_literacy_ethics, ai_stressors; codebook Source
#   Question); the TAM/AAIUS/GADS/GAIES/SDLRS/PSS-derived tables held 2026-11-25
#   (automated_finding/itemtext_hold_2026-11-25.csv);
#   automated_finding/itemtext_verification/make_itemtext_repos_2026-11-25c.py
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
URL = 'https://data.mendeley.com/public-files/datasets/f26fhdpw23/files/f010d5e7-0c91-4563-ad4f-bdf52ac0b653/file_downloaded'
N_ROWS = 412
ID_COL = 'NewID'
COVS = {'Q1': 'cov_age_group', 'Q2': 'cov_gender', 'Q3': 'cov_relationship', 'Q4': 'cov_semester'}
COV_MAPS = {'cov_age_group': {0: '18-19', 1: '19-20', 2: '20-21', 3: '21-22', 4: '22-23', 5: '23-24', 6: '24-25', 7: '25+'},
 'cov_gender': {0: 'male', 1: 'female'},
 'cov_relationship': {0: 'single', 1: 'married', 2: 'in_a_relationship', 3: 'complicated'},
 'cov_semester': {0: '1',
                  1: '2',
                  2: '3',
                  3: '4',
                  4: '5',
                  5: '6',
                  6: '7',
                  7: '8',
                  8: '9',
                  9: '10',
                  10: '11',
                  11: '12',
                  12: 'other'}}
RENAME = {}
BLOCKS = {'upoma_2026_tam_usefulness': ['Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'Q11'],
 'upoma_2026_tam_ease_of_use': ['Q12', 'Q13', 'Q14', 'Q15', 'Q16', 'Q17'],
 'upoma_2026_ai_literacy_ethics': ['Q18', 'Q19', 'Q20', 'Q21'],
 'upoma_2026_aaius': ['Q22',
                      'Q23',
                      'Q24',
                      'Q25',
                      'Q26',
                      'Q27',
                      'Q28',
                      'Q29',
                      'Q30',
                      'Q31',
                      'Q32',
                      'Q33',
                      'Q34',
                      'Q35',
                      'Q36',
                      'Q37',
                      'Q38',
                      'Q39',
                      'Q40',
                      'Q41',
                      'Q42',
                      'Q43',
                      'Q44',
                      'Q45'],
 'upoma_2026_gads': ['Q46', 'Q47', 'Q48', 'Q49', 'Q50', 'Q51', 'Q52', 'Q53', 'Q54', 'Q55', 'Q56'],
 'upoma_2026_gaies_interaction': ['Q58',
                                  'Q59',
                                  'Q60',
                                  'Q61',
                                  'Q62',
                                  'Q63',
                                  'Q64',
                                  'Q65',
                                  'Q66',
                                  'Q67',
                                  'Q68',
                                  'Q69',
                                  'Q70',
                                  'Q71'],
 'upoma_2026_gaies_frequency': ['Q72', 'Q73', 'Q74', 'Q75', 'Q76', 'Q77', 'Q78', 'Q79', 'Q80', 'Q81'],
 'upoma_2026_sdlrs_self_management': ['Q82',
                                      'Q83',
                                      'Q84',
                                      'Q85',
                                      'Q86',
                                      'Q87',
                                      'Q88',
                                      'Q89',
                                      'Q90',
                                      'Q91',
                                      'Q92',
                                      'Q93',
                                      'Q94'],
 'upoma_2026_sdlrs_self_control': ['Q95',
                                   'Q96',
                                   'Q97',
                                   'Q98',
                                   'Q99',
                                   'Q100',
                                   'Q101',
                                   'Q102',
                                   'Q103',
                                   'Q104',
                                   'Q105',
                                   'Q106',
                                   'Q107',
                                   'Q108',
                                   'Q109'],
 'upoma_2026_sdlrs_desire_learning': ['Q110',
                                      'Q111',
                                      'Q112',
                                      'Q113',
                                      'Q114',
                                      'Q115',
                                      'Q116',
                                      'Q117',
                                      'Q118',
                                      'Q119',
                                      'Q120',
                                      'Q121'],
 'upoma_2026_pss': ['Q122', 'Q123', 'Q124', 'Q125', 'Q126', 'Q127', 'Q128', 'Q129', 'Q130', 'Q131'],
 'upoma_2026_ai_stressors': ['Q132', 'Q133']}
# (lo, hi) response range per table
RANGES = {'upoma_2026_tam_usefulness': (0, 2),
 'upoma_2026_tam_ease_of_use': (0, 2),
 'upoma_2026_ai_literacy_ethics': (0, 2),
 'upoma_2026_aaius': (0, 2),
 'upoma_2026_gads': (0, 2),
 'upoma_2026_gaies_interaction': (0, 2),
 'upoma_2026_gaies_frequency': (0, 2),
 'upoma_2026_sdlrs_self_management': (1, 5),
 'upoma_2026_sdlrs_self_control': (1, 5),
 'upoma_2026_sdlrs_desire_learning': (1, 5),
 'upoma_2026_pss': (0, 4),
 'upoma_2026_ai_stressors': (0, 4)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Q57': 'single study-specific item',
 'AI_Tool_ChatGPT': 'AI-tool indicator',
 'AI_Tool_Claude': 'AI-tool indicator',
 'AI_Tool_Gemini': 'AI-tool indicator',
 'AI_Tool_CoPilot': 'AI-tool indicator',
 'AI_Tool_Other': 'AI-tool indicator',
 'AI_Tool_Count': 'AI-tool indicator'}


def load(content):
    return pd.read_csv(io.BytesIO(content))


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    sd = [f"Q{i}" for i in range(82, 122)]
    assert d[sd].isin(range(0, 5)).all().all()
    d[sd] = d[sd] + 1
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
