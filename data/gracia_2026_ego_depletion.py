#!/usr/bin/env python3
# Source: https://zenodo.org/records/24224792
# DOI: 10.5281/zenodo.24224792 (data)
#   Gracia E, Astle M, Akin K, Lowe J, Schmeichel B (2026). Dataset: Aftereffects of Self-Control on Task Performance and Effort Avoidance [Data set]. Zenodo. https://doi.org/10.5281/zenodo.24224792
# License: CC BY 4.0 (record metadata)
# Data: egodepletion_combined.csv (two lab studies, 384 + 384 US undergraduates; the xlsx Codebook sheet describes every column);
#   id = row order (the file's id repeats 342 once). TSC1-13 Brief Self-Control 1-5, BISBAS1-20 1-4, AATQ1-12 1-7, NeedCog1-18 1-5.
# Research Assistant (staff names/initials) is dropped in any form -- staff, not respondents; ruling ben-domingue 2026-11-25.
# NeedCog values stored as quoted strings are read as numbers; one stray text cell ('Complete story') set missing.
# The authors' Exclude flag is carried as a covariate, not used to filter.
# Covariates: study, condition, exclusion flag, gender, age, Hispanic ethnicity, race, birth country.
# Dropped: Qualtrics ids, session details, task-performance summaries, state ratings, scale scores.
# PII: none in what ships.
# Item text: the Codebook sheet carries the block instructions, not item wording; published instruments.
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
URL = 'https://zenodo.org/api/records/24224792/files/egodepletion_combined.csv/content'
N_ROWS = 768
ID_COL = None
COVS = {'study': 'cov_study',
 'Condition Assigned': 'cov_condition',
 'Exclude': 'cov_author_excluded',
 'Gender': 'cov_gender',
 'age': 'cov_age',
 'ethnicity': 'cov_hispanic',
 'race': 'cov_race',
 'birth_country': 'cov_birth_country'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'gracia_2026_brief_self_control': ['TSC1',
                                    'TSC2',
                                    'TSC3',
                                    'TSC4',
                                    'TSC5',
                                    'TSC6',
                                    'TSC7',
                                    'TSC8',
                                    'TSC9',
                                    'TSC10',
                                    'TSC11',
                                    'TSC12',
                                    'TSC13'],
 'gracia_2026_bis_bas': ['BISBAS1',
                         'BISBAS2',
                         'BISBAS3',
                         'BISBAS4',
                         'BISBAS5',
                         'BISBAS6',
                         'BISBAS7',
                         'BISBAS8',
                         'BISBAS9',
                         'BISBAS10',
                         'BISBAS11',
                         'BISBAS12',
                         'BISBAS13',
                         'BISBAS14',
                         'BISBAS15',
                         'BISBAS16',
                         'BISBAS17',
                         'BISBAS18',
                         'BISBAS19',
                         'BISBAS20'],
 'gracia_2026_aatq': ['AATQ1',
                      'AATQ2',
                      'AATQ3',
                      'AATQ4',
                      'AATQ5',
                      'AATQ6',
                      'AATQ7',
                      'AATQ8',
                      'AATQ9',
                      'AATQ10',
                      'AATQ11',
                      'AATQ12'],
 'gracia_2026_need_for_cognition': ['NeedCog1',
                                    'NeedCog2',
                                    'NeedCog3',
                                    'NeedCog4',
                                    'NeedCog5',
                                    'NeedCog6',
                                    'NeedCog7',
                                    'NeedCog8',
                                    'NeedCog9',
                                    'NeedCog10',
                                    'NeedCog11',
                                    'NeedCog12',
                                    'NeedCog13',
                                    'NeedCog14',
                                    'NeedCog15',
                                    'NeedCog16',
                                    'NeedCog17',
                                    'NeedCog18']}
# (lo, hi) response range per table
RANGES = {'gracia_2026_brief_self_control': (1, 5),
 'gracia_2026_bis_bas': (1, 4),
 'gracia_2026_aatq': (1, 7),
 'gracia_2026_need_for_cognition': (1, 5)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'id': 'row id (342 appears twice); id = row order',
 'Date': 'session date / room / consent / condition code / exclusion reason',
 'QualtricsID': 'Qualtrics response id',
 'Exclusion Reason': 'session date / room / consent / condition code / exclusion reason',
 'Room': 'session date / room / consent / condition code / exclusion reason',
 'Research Assistant': 'research-assistant names/initials: staff, not respondents -- dropped in any form '
                       '(ben-domingue 2026-11-25)',
 'Condition Qualtrics': 'session date / room / consent / condition code / exclusion reason',
 'Consent': 'session date / room / consent / condition code / exclusion reason',
 'difficulty': 'task performance summary, single state rating or scale score',
 'effort': 'task performance summary, single state rating or scale score',
 'fatigued': 'task performance summary, single state rating or scale score',
 'mood': 'task performance summary, single state rating or scale score',
 'yearsinUS': 'task performance summary, single state rating or scale score',
 'hourseat': 'task performance summary, single state rating or scale score',
 'hungry': 'task performance summary, single state rating or scale score',
 'cold': 'task performance summary, single state rating or scale score',
 'hourssleep': 'task performance summary, single state rating or scale score',
 'tired': 'task performance summary, single state rating or scale score',
 'TSC': 'task performance summary, single state rating or scale score',
 'BAS': 'task performance summary, single state rating or scale score',
 'BIS': 'task performance summary, single state rating or scale score',
 'BAS_d': 'task performance summary, single state rating or scale score',
 'BAS_fs': 'task performance summary, single state rating or scale score',
 'BAS_rr': 'task performance summary, single state rating or scale score',
 'NeedCog': 'task performance summary, single state rating or scale score',
 'AATQ_approach': 'task performance summary, single state rating or scale score',
 'AATQ_avoid': 'task performance summary, single state rating or scale score',
 'Unnamed: 35': 'task performance summary, single state rating or scale score',
 'Unnamed: 36': 'task performance summary, single state rating or scale score',
 'values.completed': 'task performance summary, single state rating or scale score',
 'values.version': 'task performance summary, single state rating or scale score',
 'propSelection_HD': 'task performance summary, single state rating or scale score',
 'meanRTchoice_HD': 'task performance summary, single state rating or scale score',
 'propSelection_LD': 'task performance summary, single state rating or scale score',
 'meanRTchoice_LD': 'task performance summary, single state rating or scale score',
 'propCorrect': 'task performance summary, single state rating or scale score',
 'meanRT': 'task performance summary, single state rating or scale score',
 'propCorrect_HD': 'task performance summary, single state rating or scale score',
 'meanRT_HD': 'task performance summary, single state rating or scale score',
 'propCorrect_LD': 'task performance summary, single state rating or scale score',
 'meanRT_LD': 'task performance summary, single state rating or scale score',
 'propCorrect_parity': 'task performance summary, single state rating or scale score',
 'meanRT_parity': 'task performance summary, single state rating or scale score',
 'propCorrect_magnitude': 'task performance summary, single state rating or scale score',
 'meanRT_magnitude': 'task performance summary, single state rating or scale score',
 'propCorrect_HD_parity': 'task performance summary, single state rating or scale score',
 'meanRT_HD_Parity': 'task performance summary, single state rating or scale score',
 'propCorrect_HD_magnitude': 'task performance summary, single state rating or scale score',
 'meanRT_HD_magnitude': 'task performance summary, single state rating or scale score',
 'propCorrect_LD_parity': 'task performance summary, single state rating or scale score',
 'meanRT_LD_parity': 'task performance summary, single state rating or scale score',
 'propCorrect_LD_magnitude': 'task performance summary, single state rating or scale score',
 'meanRT_LD_magnitude': 'task performance summary, single state rating or scale score',
 'nr_switchTrials': 'task performance summary, single state rating or scale score',
 'nr_repetitionTrials': 'task performance summary, single state rating or scale score',
 'propCorrect_switch': 'task performance summary, single state rating or scale score',
 'meanRT_switch': 'task performance summary, single state rating or scale score',
 'propCorrect_Repetition': 'task performance summary, single state rating or scale score',
 'meanRT_Repetition': 'task performance summary, single state rating or scale score',
 'meanRT_HD_Repetition': 'task performance summary, single state rating or scale score',
 'meanRT_HD_Switch': 'task performance summary, single state rating or scale score',
 'meanRT_LD_Repetition': 'task performance summary, single state rating or scale score',
 'meanRT_LD_Switch': 'task performance summary, single state rating or scale score',
 'propCorrect_HD_Repetition': 'task performance summary, single state rating or scale score',
 'propCorrect_HD_Switch': 'task performance summary, single state rating or scale score',
 'propCorrect_LD_Repetition': 'task performance summary, single state rating or scale score',
 'propCorrect_LD_Switch': 'task performance summary, single state rating or scale score',
 'CV_RT_total': 'task performance summary, single state rating or scale score',
 'CV_PropCorrect': 'task performance summary, single state rating or scale score',
 'CV_PropHD_total': 'task performance summary, single state rating or scale score',
 'CV_RT_block1': 'task performance summary, single state rating or scale score',
 'CV_RT_block2': 'task performance summary, single state rating or scale score',
 'CV_RT_block3': 'task performance summary, single state rating or scale score',
 'CV_RT_block4': 'task performance summary, single state rating or scale score',
 'CV_Correct_block1': 'task performance summary, single state rating or scale score',
 'CV_Correct_block2': 'task performance summary, single state rating or scale score',
 'CV_Correct_block3': 'task performance summary, single state rating or scale score',
 'CV_Correct_block4': 'task performance summary, single state rating or scale score',
 'CV_PropHD_block1': 'task performance summary, single state rating or scale score',
 'CV_PropHD_block2': 'task performance summary, single state rating or scale score',
 'CV_PropHD_block3': 'task performance summary, single state rating or scale score',
 'CV_PropHD_block4': 'task performance summary, single state rating or scale score',
 'MeanRT_block1': 'task performance summary, single state rating or scale score',
 'MeanRT_block2': 'task performance summary, single state rating or scale score',
 'MeanRT_block3': 'task performance summary, single state rating or scale score',
 'MeanRT_block4': 'task performance summary, single state rating or scale score',
 'SDRT_block1': 'task performance summary, single state rating or scale score',
 'SDRT_block2': 'task performance summary, single state rating or scale score',
 'SDRT_block3': 'task performance summary, single state rating or scale score',
 'SDRT_block4': 'task performance summary, single state rating or scale score',
 'SDRT_total': 'task performance summary, single state rating or scale score',
 'PropCorrect_block1': 'task performance summary, single state rating or scale score',
 'SDCorrect_block1': 'task performance summary, single state rating or scale score',
 'PropCorrect_block2': 'task performance summary, single state rating or scale score',
 'SDCorrect_block2': 'task performance summary, single state rating or scale score',
 'PropCorrect_block3': 'task performance summary, single state rating or scale score',
 'SDCorrect_block3': 'task performance summary, single state rating or scale score',
 'PropCorrect_block4': 'task performance summary, single state rating or scale score',
 'SDCorrect_block4': 'task performance summary, single state rating or scale score',
 'SDCorrect_total': 'task performance summary, single state rating or scale score',
 'PropHD_block1': 'task performance summary, single state rating or scale score',
 'SD_PropHD_block1': 'task performance summary, single state rating or scale score',
 'PropHD_block2': 'task performance summary, single state rating or scale score',
 'SD_PropHD_block2': 'task performance summary, single state rating or scale score',
 'PropHD_block3': 'task performance summary, single state rating or scale score',
 'SD_PropHD_block3': 'task performance summary, single state rating or scale score',
 'PropHD_block4': 'task performance summary, single state rating or scale score',
 'SD_PropHD_block4': 'task performance summary, single state rating or scale score',
 'SD_PropHD_total': 'task performance summary, single state rating or scale score'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_csv(io.BytesIO(content), header=0, **{'encoding': 'utf-8-sig'})


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """NeedCog cells are partly stored as quoted strings ("'2'"); one holds stray text and is set missing"""
    for c in [c for c in d.columns if re.fullmatch(r"NeedCog[0-9]+", c)]:
        d[c] = pd.to_numeric(d[c].map(lambda v: v if pd.isna(v) else str(v).strip().strip("'")), errors="coerce")
    for c in ["study", "Condition Assigned", "race", "birth_country"]:
        d[c] = d[c].map(slug)
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
