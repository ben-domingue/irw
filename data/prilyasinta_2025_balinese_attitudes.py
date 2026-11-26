#!/usr/bin/env python3
# Source: https://zenodo.org/records/17173323
# DOI: 10.5281/zenodo.17173323 (data)
#   Prilyasinta, Ni Wayan; Purnawan, I Kadek (2025). Revitalizing Indigenous Language: Students' Attitudes and
#     Parental Involvement in Balinese Language Learning
# License: CC BY 4.0 (repository record)
# Data: 665 Balinese secondary students (the CFA file). Headers carry the item number, subscale and English
#   statement; items are coded by subscale + the questionnaire number (PS2-PS5 perceived parental involvement;
#   COG/AFF/BEH language attitudes), six-point. The 355-student EFA file is a separate calibration sample with the
#   full item pool and is not shipped here.
# Tables: prilyasinta_2025_parental_involvement (4 items), prilyasinta_2025_balinese_attitudes (13 items across
#   cognitive, affective and behavioural subscales).
# Covariates: cov_gender_code, cov_daily_balinese, cov_area_code (0/1 as deposited; the README does not say which
#   value is which).
# PII: none found (string columns screened)
# Item text: not shipped -- English statements are the column headers; the six anchors are not in the deposit.
# Built by the 2026-11-23 repos sweep (lane 2) from a shared template; one self-contained script per deposit.

import io
import os
import sys
import tempfile
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "irw-pipeline/1.0"}

SOURCES = [{'url': 'https://zenodo.org/api/records/17173323/files/Data%20for%20Confirmatory%20Factor%20Analysis_665%20Students.csv/content',
  'kind': 'csv',
  'read_kw': {},
  'n_rows': 665,
  'range': (1, 6),
  'blocks': {'prilyasinta_2025_parental_involvement': ['PS2', 'PS3', 'PS4', 'PS5'],
             'prilyasinta_2025_balinese_attitudes': ['COG6',
                                                     'COG7',
                                                     'COG9',
                                                     'COG10',
                                                     'AFF13',
                                                     'AFF14',
                                                     'AFF17',
                                                     'AFF18',
                                                     'AFF19',
                                                     'BEH22',
                                                     'BEH23',
                                                     'BEH24',
                                                     'BEH25']},
  'covs': {'Gender': 'cov_gender_code',
           'Daily Language Use': 'cov_daily_balinese',
           'Residential Area': 'cov_area_code'},
  'cov_maps': {},
  'not_shipped': {'Participants': 'row number',
                  'Perceived Parental Involvement (Average)': 'derived mean',
                  'Cognitive aspect (Average)': 'derived mean',
                  'Affective aspect (Average)': 'derived mean',
                  'Behavioral aspect (Average)': 'derived mean',
                  'Language Attitude Average': 'derived mean'},
  'rename': {'2. (Parental Support) My parents always speak Balinese with me.': 'PS2',
             '3. (Parental Support) My parents always teach me to use good Balinese.': 'PS3',
             '4. (Parental Support) When advising me, my parents use Balinese.': 'PS4',
             '5. (Parental Support) My parents taught me about Balinese culture and Hinduism using the Balinese language.': 'PS5',
             "6. (Cognitive) In today's Balinese society, person who speak the language will hold greater respect.": 'COG6',
             '7. (Cognitive) Knowledge of Balinese language can lead to numerous career prospects.': 'COG7',
             '9. (Cognitive) Every native Balinese person needs to be able to carry on daily conversations in Balinese.': 'COG9',
             '. 10. (Cognitive) Being able to communicate well in Balinese is crucial for surviving in the modern Balinese society.': 'COG10',
             '13. (Affective) I feel proud to learn Balinese.': 'AFF13',
             '14. (Affective) I like learning Balinese at school because the lessons are fun and interesting.': 'AFF14',
             '17. (Affective) I enjoy all the learning activities in the Balinese language class at school.': 'AFF17',
             '18. (Affective) Learning Balinese has increased my motivation and enthusiasm for learning.': 'AFF18',
             '19. (Affective) I feel comfortable learning Balinese at school.': 'AFF19',
             '22. (Behavioral) Before Balinese language lessons, I always take the time to prepare myself or study first at home.': 'BEH22',
             '23. (Behavioral) I watch and listen to Balinese language programs diligently on TV or radio broadcasts.': 'BEH23',
             '24. (Behavioral) I read Balinese literary works, such as short stories, novels, poetry in Balinese.': 'BEH24',
             '25. (Behavioral) I actively watch Balinese language content on social media, such as Instagram, Youtube, Facebook, WhatsApp, etc.': 'BEH25'},
  'label': 'prilyasinta_2025_balinese_attitudes'}]


def load(content, kind, read_kw):
    if kind == "csv":
        return pd.read_csv(io.BytesIO(content), **read_kw)
    if kind == "excel":
        return pd.read_excel(io.BytesIO(content), **read_kw)
    if kind == "sav":
        import pyreadstat
        with tempfile.NamedTemporaryFile(suffix=".sav", delete=False) as fh:
            fh.write(content)
        try:
            df, _ = pyreadstat.read_sav(fh.name, **read_kw)
        finally:
            os.unlink(fh.name)
        return df
    if kind == "dta":
        return pd.read_stata(io.BytesIO(content), convert_categoricals=False)
    raise ValueError(kind)


def build_source(src):
    for attempt in range(5):  # Mendeley's public-files endpoint returns transient 502s
        r = requests.get(src["url"], timeout=300, headers=UA)
        if r.status_code < 500:
            break
        time.sleep(20 * (attempt + 1))
    r.raise_for_status()
    d = load(r.content, src["kind"], src.get("read_kw", {}))
    if src.get("resplit"):
        # the workbook holds one column whose header and cells are ;-joined; split it back out
        col = d.columns[0]
        d = pd.read_csv(io.StringIO("\n".join([str(col)] + d[col].astype(str).tolist())), sep=";")
    d.columns = [" ".join(str(c).split()) for c in d.columns]
    d = d.rename(columns=src.get("rename", {}))
    assert len(d) == src["n_rows"], (src["label"], len(d))
    before = len(d)
    if src.get("keep_col_eq"):
        col, val = src["keep_col_eq"]
        d = d[d[col] == val]
    if src.get("keep_any_item"):
        d = d[d[[c for cols in src["blocks"].values() for c in cols]].notna().any(axis=1)]
    if len(d) != before:
        print(f"{src['label']}: kept {len(d)} of {before} rows ({src.get('keep_reason', '')})")
    # The books: every source column is shipped (item or covariate), the id, or skipped for a stated reason.
    items = [c for cols in src["blocks"].values() for c in cols]
    used = set(items) | set(src.get("covs", {})) | set(src.get("not_shipped", {}))
    if src.get("id_col"):
        used.add(src["id_col"])
    unaccounted = [c for c in d.columns if c not in used]
    assert not unaccounted, (src["label"], unaccounted)
    missing = [c for c in used if c not in d.columns]
    assert not missing, (src["label"], missing)
    if src.get("id_col"):
        assert d[src["id_col"]].notna().all() and d[src["id_col"]].is_unique, "id not unique"
        d["id"] = d[src["id_col"]].astype(str)
    else:
        d["id"] = [str(k) for k in range(1, len(d) + 1)]
    if src.get("id_prefix"):
        d["id"] = src["id_prefix"] + "_" + d["id"]
    for col, bad in src.get("invalid", {}).items():
        # out-of-range codes isolated to one item: data-entry errors, set missing (see header)
        hit = d[col].isin(bad)
        print(f"{src['label']}: {col}: {int(hit.sum())} cell(s) {bad} set missing")
        d.loc[hit, col] = None
    covs = []
    for col, cov in src.get("covs", {}).items():
        m = src.get("cov_maps", {}).get(cov)
        if m is not None:
            vals = d[col].map(lambda v: m.get(v, m.get(str(v).strip())) if pd.notna(v) else None)
            bad = [v for v in d[col].dropna().unique() if v not in m and str(v).strip() not in m]
            assert len(bad) == 0, (cov, bad[:10])
            d[cov] = vals
        else:
            d[cov] = d[col]
        covs.append(cov)
    for k, v in src.get("const_covs", {}).items():
        d[k] = v
        covs.append(k)
    out = {}
    for name, cols in src["blocks"].items():
        t = d[["id"] + covs + cols].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        rec = src.get("recode", {})
        if rec:
            t["resp"] = t["resp"].map(lambda v: rec.get(str(v).strip(), v) if pd.notna(v) else v)
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        miss = src.get("missing_codes", [])
        if miss:
            t.loc[t["resp"].isin(miss), "resp"] = None
        t = t.dropna(subset=["resp"])
        shift = src.get("shift", {}).get(name, 0)
        t["resp"] = t["resp"] + shift
        lo, hi = src.get("ranges", {}).get(name, src["range"])
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        assert t["resp"].between(lo, hi).all(), (name, t["resp"].min(), t["resp"].max())
        t["resp"] = t["resp"].astype(int)
        out[name] = (t, (lo, hi))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tables = {}
    for src in SOURCES:
        for name, (t, rng) in build_source(src).items():
            tables.setdefault(name, []).append((t, rng))
    for name, parts in tables.items():
        assert len({rng for _, rng in parts}) == 1, name
        lo, hi = parts[0][1]
        t = pd.concat([p for p, _ in parts], ignore_index=True)
        covs = [c for c in t.columns if c.startswith("cov_")]
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"], kind="stable")
        assert not t.duplicated(["id", "item"]).any(), name
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        assert len(name) <= 40, name
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    assert len(tables) == len(set(tables)), "duplicate table names"


if __name__ == "__main__":
    main()
