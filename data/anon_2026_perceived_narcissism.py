#!/usr/bin/env python3
# Source: https://zenodo.org/records/23982003
# DOI: 10.5281/zenodo.23982003 (data)
#   Anonymous (2026). Development and Initial Validation of the Perceived Narcissism Index [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23982003
# License: CC BY 4.0 (record metadata)
# Data: CFAData.sav and EFAData.sav (Qualtrics exports with value labels), 200 Prolific adults each, rating a former close
#   other; the Qualtrics survey PDFs are in the deposit. Item names are the depositor's short labels (selfish, self_absorbed ...).
# One PNI table stacks the two samples (cov_sample); the CFA sample answered the 24 retained items only.
# The single 'This person is a narcissist' item is a covariate (criterion), not a PNI item.
# Not carried: PROLIFIC_PID (platform ID; id = row order instead), ResponseId, free-text "other" answers, race checklist,
#   attention checks, consent/terminate flags.
# Covariates: sample, gender, ethnic background, country, age, target/relationship descriptors.
# Item text: shipped 2026-11-25c -- .sav variable + value labels (EFA/CFA files), the depositors' own inventory;
#   automated_finding/itemtext_verification/make_itemtext_repos_2026-11-25c.py
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
URL = 'https://zenodo.org/api/records/23982003/files/CFAData.sav/content'
N_ROWS = 400
ID_COL = 'pid'
COVS = {'sample': 'cov_sample',
 'Q1': 'cov_gender',
 'Q2': 'cov_ethnic_background',
 'country': 'cov_country',
 'Q4': 'cov_age',
 'Person_Choice': 'cov_target_type',
 'Relationship_Length': 'cov_relationship_length',
 'Ending_person': 'cov_who_ended',
 'Current_Relationship': 'cov_current_relationship',
 'narcissist': 'cov_rated_narcissist'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'anon_2026_pni': ['selfish',
                   'self_absorbed',
                   'own_needs',
                   'others_firstR',
                   'empathy',
                   'consideration',
                   'regard_feelings',
                   'need_considerationR',
                   'admitting_fault',
                   'take_criticism',
                   'accept_consequences',
                   'shift_blame',
                   'take_responsibilityR',
                   'self_concern',
                   'perception',
                   'whole_world',
                   'entitled',
                   'more_important',
                   'better_than_others',
                   'more_capable',
                   'arrogant',
                   'just_as_importantR',
                   'modestR',
                   'hide_insecurity',
                   'need_admiration',
                   'crave_validation',
                   'puts_down',
                   'strong_selfworthR',
                   'center_attention',
                   'constant_admiration',
                   'show_off',
                   'blend_inR',
                   'manipulative',
                   'control',
                   'downplay_opinions',
                   'Charm'],
 'anon_2026_pni_impressions': ['friendly',
                               'warm',
                               'approachable',
                               'trustworthyEX',
                               'similar',
                               'knowledgeable',
                               'likable',
                               'GladEX']}
# (lo, hi) response range per table
RANGES = {'anon_2026_pni': (1, 7), 'anon_2026_pni_impressions': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'AC1': 'attention check',
 'AC2': 'attention check',
 'AC3': 'attention check',
 'Consent': 'consent / terminate flag',
 'Current_Relationship_9_TEXT': 'free-text "other" answer',
 'Ending_person_5_TEXT': 'free-text "other" answer',
 'PROLIFIC_PID': 'Prolific participant ID (replaced by row order)',
 'Q1_8_TEXT': 'free-text "other" answer',
 'Q3_1': 'race multi-select checklist',
 'Q3_10': 'race multi-select checklist',
 'Q3_2': 'race multi-select checklist',
 'Q3_3': 'race multi-select checklist',
 'Q3_5': 'race multi-select checklist',
 'Q3_6': 'race multi-select checklist',
 'Q3_8': 'race multi-select checklist',
 'Q3_8_TEXT': 'free-text "other" answer',
 'Q3_9': 'race multi-select checklist',
 'Q_TerminateFlag': 'consent / terminate flag',
 'ResponseId': 'Qualtrics response ID',
 'country_5_TEXT': 'free-text "other" answer'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    import pyreadstat, tempfile
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(content); f.flush()
        d, _ = pyreadstat.read_sav(f.name, user_missing=False)
    return d


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """CFA sample (this URL) + EFA sample (EFAData.sav), stacked with cov_sample. PROLIFIC_PID is not carried; id = sample + row."""
    import pyreadstat, tempfile
    r = requests.get('https://zenodo.org/api/records/23982003/files/EFAData.sav/content', timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(r.content); f.flush()
        e, _ = pyreadstat.read_sav(f.name)
    d["sample"] = "cfa"
    e["sample"] = "efa"
    d["pid"] = ["cfa_%d" % i for i in range(1, len(d) + 1)]
    e["pid"] = ["efa_%d" % i for i in range(1, len(e) + 1)]
    return pd.concat([d, e], ignore_index=True)


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
