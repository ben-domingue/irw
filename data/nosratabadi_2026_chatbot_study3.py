#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.31004254.v3
# DOI: 10.6084/m9.figshare.31004254.v3 (data)
#   Nosratabadi S, Atobishi T (2026). Data for "Warmth and Competence in Conversational AI: A Dual-Route Model of Purchase Intention" [Data set]. figshare.
# License: CC BY 4.0 (record metadata)
# Data: Study3_data.csv, 400 Prolific (US) participants in a 2 (product) x 2 (competence) x 2 (warmth) design; the 363 who
#   passed the attention check (dv_attention_check == 2, the analysis script's rule and the record's N) are kept; id = row order.
#   Items dv_<construct>_k on 1-7; Study 3 names its items generically, so it is not stacked with Studies 1-2.
# Covariates: product type, competence and warmth condition, age, gender, AI literacy, product knowledge, perceived formality
#   (single item), time on task, word count.
# PII: none.
# Item text: not shipped -- codes only; wording in the paper.
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
URL = 'https://ndownloader.figshare.com/files/69890751'
N_ROWS = 363
ID_COL = None
COVS = {'product_type': 'cov_product',
 'competence_level': 'cov_competence_cond',
 'warmth_level': 'cov_warmth_cond',
 'age': 'cov_age',
 'gender': 'cov_gender',
 'ctrl_ai_literacy': 'cov_ai_literacy',
 'ctrl_product_knowledge': 'cov_product_knowledge',
 'dv_formality': 'cov_perceived_formality',
 'behavioral_time_on_task': 'cov_time_on_task_s',
 'behavioral_word_count': 'cov_word_count'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'nosratabadi_2026_s3_competence': ['dv_comp_1', 'dv_comp_2', 'dv_comp_3'],
 'nosratabadi_2026_s3_warmth': ['dv_warmth_1', 'dv_warmth_2', 'dv_warmth_3', 'dv_warmth_4'],
 'nosratabadi_2026_s3_risk': ['dv_risk_1', 'dv_risk_2', 'dv_risk_3'],
 'nosratabadi_2026_s3_engagement': ['dv_engage_1', 'dv_engage_2', 'dv_engage_3'],
 'nosratabadi_2026_s3_purchase_intention': ['dv_pi_1', 'dv_pi_2', 'dv_pi_3'],
 'nosratabadi_2026_s3_effort': ['dv_effort_1', 'dv_effort_2', 'dv_effort_3'],
 'nosratabadi_2026_s3_humanness': ['dv_human_1', 'dv_human_2', 'dv_human_3'],
 'nosratabadi_2026_s3_fcb': ['dv_fcb_1', 'dv_fcb_2', 'dv_fcb_3', 'dv_fcb_4']}
# (lo, hi) response range per table
RANGES = {'nosratabadi_2026_s3_competence': (1, 7),
 'nosratabadi_2026_s3_warmth': (1, 7),
 'nosratabadi_2026_s3_risk': (1, 7),
 'nosratabadi_2026_s3_engagement': (1, 7),
 'nosratabadi_2026_s3_purchase_intention': (1, 7),
 'nosratabadi_2026_s3_effort': (1, 7),
 'nosratabadi_2026_s3_humanness': (1, 7),
 'nosratabadi_2026_s3_fcb': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'dv_attention_check': 'attention check (rows failing it dropped)'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_csv(io.BytesIO(content), header=0, **{})


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    d = d[d["dv_attention_check"] == 2].reset_index(drop=True)
    d["gender"] = d["gender"].map(slug)
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
