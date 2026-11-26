#!/usr/bin/env python3
# Source: https://doi.org/10.25377/sussex.33406369.v1
# DOI: 10.25377/sussex.33406369.v1 (data)
#   Garnham A, Oakhill J, Drew H, Banerjee R (2026). Scripts and variables from 'Is leisure-time reading related to empathy and social skills in 8- to 10-year-old children' (BJDP 2026) [Data set]. figshare. https://doi.org/10.25377/sussex.33406369.v1
# License: CC BY 4.0 (record metadata)
# Data: EmpathyRDFPaperData.csv, 113 UK children aged 8-10 (Years 4-5), the file's CODE (trailing blank rows dropped); 999 = missing.
#   EmQue 1-3, BES 1-5 (raw items; the *r reverse-coded copies are the authors' recodes), social skills 0-2, SDQ items 1-3,
#   reading-attitude items 0/1.
# Covariates: gender, year group, reading age (months), reading habits, Author Recognition Test total.
# Dropped: totals, subscales, z-scores, *r copies, who-questions.
# PII: none.
# Item text: codes only; published child instruments (EmQue, BES, SDQ).
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
URL = 'https://ndownloader.figshare.com/files/68108149'
N_ROWS = 113
ID_COL = 'CODE'
COVS = {'Gender': 'cov_gender',
 'Yr_Grp': 'cov_year_group',
 'RAmonths': 'cov_reading_age_months',
 'LikeReading': 'cov_likes_reading',
 'StoryType': 'cov_story_type',
 'FreqReadSelf': 'cov_freq_read_self',
 'FreqReadsToYou': 'cov_freq_read_to',
 'FreqYouReadTo': 'cov_freq_read_to_others',
 'FreqTalkAbout': 'cov_freq_talk_books',
 'FreqLibrary': 'cov_freq_library',
 'ART_total': 'cov_author_recognition'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'garnham_2026_emque': ['EmQue_1',
                        'EmQue_2',
                        'EmQue_3',
                        'EmQue_4',
                        'EmQue_5',
                        'EmQue_6',
                        'EmQue_7',
                        'EmQue_8',
                        'EmQue_9',
                        'EmQue_10',
                        'EmQue_11',
                        'EmQue_12',
                        'EmQue_13',
                        'EmQUe_14',
                        'EmQue_15',
                        'EmQue_16',
                        'EmQue_17',
                        'EmQue_18'],
 'garnham_2026_bes': ['BES_1',
                      'BES_2',
                      'BES_3',
                      'BES_4',
                      'BES_5',
                      'BES_6',
                      'BES_7',
                      'BES_8',
                      'BES_9',
                      'BES_10',
                      'BES_11',
                      'BES_12',
                      'BES_13',
                      'BES_14',
                      'BES_15',
                      'BES_16',
                      'BES_17',
                      'BES_18',
                      'BES_19',
                      'BES_20'],
 'garnham_2026_social_skills': ['SS_1', 'SS_2', 'SS_3', 'SS_4', 'SS_5', 'SS_6', 'SS_7', 'SS_8'],
 'garnham_2026_sdq_items': ['SDQ_1',
                            'SDQ_2',
                            'SDQ_3',
                            'SDQ_4',
                            'SDQ_5',
                            'SDQ_6',
                            'SDQ_7',
                            'SDQ_8',
                            'SDQ_9',
                            'SDQ_10'],
 'garnham_2026_reading_attitudes': ['Readboring',
                                    'Readhard',
                                    'Readtired',
                                    'Readattention',
                                    'Readsitting',
                                    'Readpicture']}
# (lo, hi) response range per table
RANGES = {'garnham_2026_emque': (1, 3),
 'garnham_2026_bes': (1, 5),
 'garnham_2026_social_skills': (0, 2),
 'garnham_2026_sdq_items': (1, 3),
 'garnham_2026_reading_attitudes': (0, 1)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {'garnham_2026_emque': [999],
 'garnham_2026_bes': [999],
 'garnham_2026_social_skills': [999],
 'garnham_2026_sdq_items': [999],
 'garnham_2026_reading_attitudes': [999]}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'ReadAge': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'Unnamed: 5': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'WhoReadsToYou': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'WhoYouReadTo': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'WhoTalkAbout': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'WhoLibrary': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'Favouritebooks': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'FavBooksTotal': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ReadTotal': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZFreqTalkAbout': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZFreqReadsToYou': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZFreqYouReadTo': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZFreqReadSelf': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'Unnamed: 30': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'Unnamed: 49': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'EmQueTot': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'EmQueAff': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'EmQueCog': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'EmQuePro': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'EmQueCogAff': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZEMQCA': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZEmQueAff': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZEmQueCog': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'Unnamed: 58': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'RMETTotal': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZRMETTotal': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'Unnamed: 61': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'SSTotal': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZSSTotal': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'Unnamed: 72': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'BES_1r': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'BES_6r': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'BES_7r': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'BES_8r': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'BES_13r': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'BES_18r': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'BES_19r': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'BES_20r': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'BESTotal': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'BESAff': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'BESCog': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZBESAff': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZBESCog': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZBESTot': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'Unnamed: 107': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'SDQproso': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'Unnamed: 119': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZRead4Av': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'Zemp': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZAff': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'ZCog': 'blank, who-question code, total, subscale, z-score or reverse-coded copy',
 'Unnamed: 124': 'blank, who-question code, total, subscale, z-score or reverse-coded copy'}
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
    d = d[d["CODE"].notna()].reset_index(drop=True)
    d["StoryType"] = d["StoryType"].map(slug)
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
