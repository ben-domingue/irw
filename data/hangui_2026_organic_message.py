#!/usr/bin/env python3
# Source: https://zenodo.org/records/23516480
# DOI: 10.5281/zenodo.23516480 (data)
#   Hangui S (2026). Data and R Code for "Motive Attributions in Organic Food Communication: Message Framing, Premium
#   Presentation, Skepticism, and Purchase Intention" (Int J Consumer Studies, accepted) [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: organic_message_public_data.tsv, 6,500 Japanese online-panel respondents in a 2 x 2 between-subjects message
#   experiment; respondent_id is the depositor's new sequential id (the panel id was removed). README_public_release.txt
#   documents every variable; organic_message_reproducibility.R gives the item-to-construct mapping used here
#   (items_att, items_ego, items_val, items_str, items_stk, items_S, items_pi). All items are 1-7 (seven-point).
# Tables, item = the deposit's code: _attitude (Q1_1-6), the four motive-attribution subscales _motive_egoistic
#   (Q5_1-3), _motive_values (Q5_4-7), _motive_strategic (Q5_8-11), _motive_stakeholder (Q5_12-15), _skepticism
#   (Q6_1-4), _purchase_intention (Q7_1-3).
#   Q6_1-4 are shipped as stored: the README says they are worded in the favourable direction and the R script scores
#   skepticism as 8 - Q6_i; IRW ships the response as given, so higher = LESS skeptical in this table.
# Covariates: cov_message (QBD_GR: values_oriented / business_oriented), cov_premium (GapType: gap / gapless).
#   Q4, the labelled choice-task outcome, is a single choice rather than a scale item; not carried.
# PII: none (the depositor removed exact age, prefecture and the panel id; one text column, GapType, is a condition).
# Item text: not shipped -- the deposit carries codes only; the wording is in the article.
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
URL = 'https://zenodo.org/api/records/23516480/files/organic_message_public_data.tsv/content'
N_ROWS = 6500
ID_COL = 'respondent_id'
COVS = {'QBD_GR': 'cov_message', 'GapType': 'cov_premium'}
COV_MAPS = {'cov_message': {1: 'values_oriented', 2: 'business_oriented'}, 'cov_premium': {'Gapless': 'gapless', 'Gap': 'gap'}}
RENAME = {}
BLOCKS = {'hangui_2026_attitude': ['Q1_1', 'Q1_2', 'Q1_3', 'Q1_4', 'Q1_5', 'Q1_6'],
 'hangui_2026_motive_egoistic': ['Q5_1', 'Q5_2', 'Q5_3'],
 'hangui_2026_motive_values': ['Q5_4', 'Q5_5', 'Q5_6', 'Q5_7'],
 'hangui_2026_motive_strategic': ['Q5_8', 'Q5_9', 'Q5_10', 'Q5_11'],
 'hangui_2026_motive_stakeholder': ['Q5_12', 'Q5_13', 'Q5_14', 'Q5_15'],
 'hangui_2026_skepticism': ['Q6_1', 'Q6_2', 'Q6_3', 'Q6_4'],
 'hangui_2026_purchase_intention': ['Q7_1', 'Q7_2', 'Q7_3']}
# (lo, hi) response range per table
RANGES = {'hangui_2026_attitude': (1, 7),
 'hangui_2026_motive_egoistic': (1, 7),
 'hangui_2026_motive_values': (1, 7),
 'hangui_2026_motive_strategic': (1, 7),
 'hangui_2026_motive_stakeholder': (1, 7),
 'hangui_2026_skepticism': (1, 7),
 'hangui_2026_purchase_intention': (1, 7)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Q4': 'choice-task outcome, not a scale item'}


def load(content):
    return pd.read_csv(io.BytesIO(content), sep="\t")


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
