#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.31004254.v3
# DOI: 10.6084/m9.figshare.31004254.v3 (data)
#   Nosratabadi S, Atobishi T (2026). Data for "Warmth and Competence in Conversational AI: A Dual-Route Model of Purchase Intention" [Data set]. figshare. https://doi.org/10.6084/m9.figshare.31004254.v3
# License: CC BY 4.0 (record metadata)
# Data: study1_data.csv (198 Prolific US participants, skincare chatbot, competence manipulation) and Study2_data.csv (200,
#   warmth manipulation), items on 1-7. Risk_* and PI_* carry identical names in both studies, so those two tables stack
#   the studies (cov_study); competence is Study 1 only, warmth and engagement Study 2 only. Study 3 is built by
#   data/nosratabadi_2026_chatbot_study3.py.
# Covariates: study, condition, gender, age, AI literacy, product knowledge, dispositional trust (S1), time on task and word count (S2).
# Dropped: the Mean_* composites.
# PII: none (sequential participant numbers).
# Item text: codes with one-word item glosses (e.g. Warmth_1_Sincere); full wording in the paper.
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
URL = 'https://ndownloader.figshare.com/files/69890739'
N_ROWS = 398
ID_COL = 'Participant_ID'
COVS = {'study': 'cov_study',
 'condition': 'cov_condition',
 'Gender': 'cov_gender',
 'Age': 'cov_age',
 'AI_Literacy': 'cov_ai_literacy',
 'Product_Knowledge': 'cov_product_knowledge',
 'Disposition_Trust': 'cov_disposition_trust',
 'Behavioral_Time': 'cov_time_on_task_s',
 'Behavioral_Words': 'cov_word_count'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'nosratabadi_2026_s12_competence': ['Comp_1_Intelligent', 'Comp_2_Competent', 'Comp_3_Confidence'],
 'nosratabadi_2026_s12_warmth': ['Warmth_1_Sincere', 'Warmth_2_GoodNatured', 'Warmth_3_Warm', 'Warmth_4_Tolerant'],
 'nosratabadi_2026_s12_engagement': ['Engage_1_Immersed', 'Engage_2_Enjoyable', 'Engage_3_TimeLoss'],
 'nosratabadi_2026_s12_risk': ['Risk_1_Global', 'Risk_2_Performance', 'Risk_3_Financial'],
 'nosratabadi_2026_s12_purchase_intention': ['PI_1_Purchase', 'PI_2_Rely', 'PI_3_Transact']}
# (lo, hi) response range per table
RANGES = {'nosratabadi_2026_s12_competence': (1, 7),
 'nosratabadi_2026_s12_warmth': (1, 7),
 'nosratabadi_2026_s12_engagement': (1, 7),
 'nosratabadi_2026_s12_risk': (1, 7),
 'nosratabadi_2026_s12_purchase_intention': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Mean_Comp': 'composite mean',
 'Mean_Risk': 'composite mean',
 'Mean_PI': 'composite mean',
 'Mean_Warmth': 'composite mean',
 'Mean_Engage': 'composite mean',
 'Condition': 'carried as cov_condition (prefixed by study)'}
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
    """Study 1 (this URL) and Study 2 share the Risk_* and PI_* items by name; stack them with cov_study.
    Participant_IDs are 1-198 and 201-400, so they stay unique."""
    r = requests.get('https://ndownloader.figshare.com/files/69890745', timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d2 = pd.read_csv(io.BytesIO(r.content))
    d["study"] = 1
    d2["study"] = 2
    d = pd.concat([d, d2], ignore_index=True)
    d["condition"] = "s" + d["study"].astype(str) + "_" + d["Condition"].astype(str)
    d["Gender"] = d["Gender"].map(slug)
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
