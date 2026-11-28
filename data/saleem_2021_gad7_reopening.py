#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/djd7xvw6d5
# DOI: 10.17632/djd7xvw6d5.1 (data)
#   Sarosh Saleem; Saadia Shahzad (2021). Reopening of Universities for on-campus teaching in COVID- 19 Pandemic:
#     Status of Generalized Anxiety in medical students [Dataset]. Mendeley Data.
# License: CC BY 4.0 (Mendeley Data record: share/copy/modify with credit)
# Data: 552 Pakistani medical and dental students before campuses reopened (Sept 2020), GAD-7 worded 'particularly
#   thinking about re-opening of College/University ... in the past 2 weeks'; text answers mapped 0-3 (Not at all,
#   Several days, More than half the days, Nearly every day).
# Tables: one GAD-7 table; items gad1..gad7 in the questionnaire's order (the bracketed statements are the seven
#   GAD-7 stems in standard order).
# Covariates: cov_age (ages 4, 10 and 1994 typed in the free-text age field set missing), cov_gender,
#   cov_institution_type, cov_year_of_study, cov_residence
# PII: none; the city column is dropped (geographic code rule)
# Item text: available -- the bracketed GAD-7 stems in the headers
# Built by the 2026-11-20 repos leads (lane 2) from a shared template; one self-contained script per deposit.

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

SOURCES = [{'url': 'https://data.mendeley.com/public-files/datasets/djd7xvw6d5/files/514ca590-eff9-49f9-af8e-81bdbb2c955d/file_downloaded',
  'kind': 'csv',
  'read_kw': {},
  'n_rows': 552,
  'range': (0, 3),
  'blocks': {'saleem_2021_gad7': ['Particularly thinking about re-opening of College/University, please answer the '
                                  'following questions of how you have felt in the past 2 weeks [Feeling anxious, '
                                  'nervous, or on edge]',
                                  'Particularly thinking about re-opening of College/University, please answer the '
                                  'following questions of how you have felt in the past 2 weeks [Inability to stop '
                                  'worrying or control worrying]',
                                  'Particularly thinking about re-opening of College/University, please answer the '
                                  'following questions of how you have felt in the past 2 weeks [Excessive worrying '
                                  'about different things]',
                                  'Particularly thinking about re-opening of College/University, please answer the '
                                  'following questions of how you have felt in the past 2 weeks [Restlessness that '
                                  'it’s hard to sit still]',
                                  'Particularly thinking about re-opening of College/University, please answer the '
                                  'following questions of how you have felt in the past 2 weeks [Difficulty in '
                                  'relaxing]',
                                  'Particularly thinking about re-opening of College/University, please answer the '
                                  'following questions of how you have felt in the past 2 weeks [Becoming easily '
                                  'annoyed or irritable]',
                                  'Particularly thinking about re-opening of College/University, please answer the '
                                  'following questions of how you have felt in the past 2 weeks [Feeling afraid as '
                                  'if something awful might happen]']},
  'covs': {'Your age (in Years)': 'cov_age',
           'Gender': 'cov_gender',
           'Your College/University is': 'cov_institution_type',
           'Year of Study': 'cov_year_of_study',
           'You are a': 'cov_residence'},
  'cov_maps': {'cov_gender': {'Female': 'female', 'Male': 'male', 'Prefer not to say': None},
               'cov_institution_type': {'Private': 'private', 'Government': 'government'},
               'cov_year_of_study': {'1st Year': '1',
                                     '2nd Year': '2',
                                     '3rd Year': '3',
                                     '4th Year': '4',
                                     '5th Year': '5',
                                     'Final year': 'final',
                                     'House officer ': 'house officer',
                                     'House officer': 'house officer',
                                     'housejob': 'house officer',
                                     'House job': 'house officer'},
               'cov_residence': {'Day scholar': 'day scholar',
                                 'Hostelite': 'hostel',
                                 'Citizen': None,
                                 "Stays at relative's house": 'relative'}},
  'not_shipped': {'Timestamp': 'form timestamp',
                  'Your College/University is located in which City': 'city of the college (geographic code rule)',
                  'Have you ever been?': 'single COVID attitude item, not a scale',
                  'Are you afraid of being infected by COVID-19 while on campus?': 'single COVID attitude item, not '
                                                                                   'a scale',
                  'Do you prefer online educational activities as compared to being on campus?': 'single COVID '
                                                                                                 'attitude item, not '
                                                                                                 'a scale',
                  'How committed you will be to observe the precautions yourself (wearing face masks/ social distancing/ hand washing) at all times while you are at campus?': 'single '
                                                                                                                                                                               'COVID '
                                                                                                                                                                               'attitude '
                                                                                                                                                                               'item, '
                                                                                                                                                                               'not '
                                                                                                                                                                               'a '
                                                                                                                                                                               'scale',
                  'What would you fear most in going back to college during the Pandemic? (You can tick more than one)': 'single '
                                                                                                                         'COVID '
                                                                                                                         'attitude '
                                                                                                                         'item, '
                                                                                                                         'not '
                                                                                                                         'a '
                                                                                                                         'scale'},
  'label': 'saleem_2021_gad7_reopening',
  'item_names': {'Particularly thinking about re-opening of College/University, please answer the following questions of how you have felt in the past 2 weeks [Feeling anxious, nervous, or on edge]': 'gad1',
                 'Particularly thinking about re-opening of College/University, please answer the following questions of how you have felt in the past 2 weeks [Inability to stop worrying or control worrying]': 'gad2',
                 'Particularly thinking about re-opening of College/University, please answer the following questions of how you have felt in the past 2 weeks [Excessive worrying about different things]': 'gad3',
                 'Particularly thinking about re-opening of College/University, please answer the following questions of how you have felt in the past 2 weeks [Restlessness that it’s hard to sit still]': 'gad4',
                 'Particularly thinking about re-opening of College/University, please answer the following questions of how you have felt in the past 2 weeks [Difficulty in relaxing]': 'gad5',
                 'Particularly thinking about re-opening of College/University, please answer the following questions of how you have felt in the past 2 weeks [Becoming easily annoyed or irritable]': 'gad6',
                 'Particularly thinking about re-opening of College/University, please answer the following questions of how you have felt in the past 2 weeks [Feeling afraid as if something awful might happen]': 'gad7'},
  'recode': {'Not at all': 0, 'Several Days': 1, 'More than half the days': 2, 'Nearly Every Day': 3},
  'invalid': {'Your age (in Years)': [4, 10, 1994]}}]

# rows written per table (asserted)
EXPECT = {'saleem_2021_gad7': 3864}


def load(content, kind, read_kw):
    if kind == "csv":
        return pd.read_csv(io.BytesIO(content), **read_kw)
    if kind == "excel":
        return pd.read_excel(io.BytesIO(content), **read_kw)
    if kind in ("sav", "dta"):
        import pyreadstat
        with tempfile.NamedTemporaryFile(suffix="." + kind, delete=False) as fh:
            fh.write(content)
        try:
            reader = pyreadstat.read_sav if kind == "sav" else pyreadstat.read_dta
            df, _ = reader(fh.name, **read_kw)
        finally:
            os.unlink(fh.name)
        return df
    raise ValueError(kind)


def fetch(url):
    for attempt in range(6):  # Mendeley's public-files endpoint returns transient 502s
        try:
            r = requests.get(url, timeout=300, headers=UA)
        except requests.RequestException:
            time.sleep(15 * (attempt + 1))
            continue
        if r.status_code < 500:
            break
        time.sleep(20 * (attempt + 1))
    r.raise_for_status()
    return r.content


def build_source(src):
    d = load(fetch(src["url"]), src["kind"], src.get("read_kw", {}))
    d.columns = [" ".join(str(c).split()) for c in d.columns]
    d = d.rename(columns=src.get("rename", {}))
    if src.get("drop_empty_rows"):
        d = d.dropna(how="all")
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
    special = [x["col"] for x in (src.get("wave"), src.get("treat")) if x]
    used = set(items) | set(src.get("covs", {})) | set(src.get("not_shipped", {})) | set(special)
    if src.get("id_col"):
        used.add(src["id_col"])
    unaccounted = [c for c in d.columns if c not in used]
    assert not unaccounted, (src["label"], unaccounted)
    missing = [c for c in used if c not in d.columns]
    assert not missing, (src["label"], missing)
    if src.get("id_col"):
        if src.get("wave"):
            assert not d.duplicated([src["id_col"], src["wave"]["col"]]).any(), "id x wave not unique"
        else:
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
    extra = []
    for key in ("wave", "treat"):
        spec = src.get(key)
        if spec:
            m = spec.get("map")
            v = d[spec["col"]]
            if m is not None:
                bad = [x for x in v.dropna().unique() if x not in m]
                assert not bad, (key, bad)
                v = v.map(m)
            d[key] = v
            extra.append(key)
    for k, v in src.get("const", {}).items():
        d[k] = v
        extra.append(k)
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
    names = src.get("item_names", {})
    out = {}
    for name, cols in src["blocks"].items():
        t = d[["id"] + extra + covs + cols].melt(id_vars=["id"] + extra + covs, var_name="item", value_name="resp")
        rec = src.get("recode", {})
        if rec:
            def _rc(v):
                if pd.isna(v):
                    return v
                k = " ".join(str(v).split())
                assert k in rec or not isinstance(v, str), (name, v)
                return rec.get(k, v)
            t["resp"] = t["resp"].map(_rc)
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        miss = src.get("missing_codes", [])
        if miss:
            t.loc[t["resp"].isin(miss), "resp"] = None
        t = t.dropna(subset=["resp"])
        t["item"] = t["item"].map(lambda c: names.get(c, c))
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
        lo = min(r[0] for _, r in parts)
        hi = max(r[1] for _, r in parts)
        t = pd.concat([p for p, _ in parts], ignore_index=True)
        lead = [c for c in ("wave", "treat") if c in t.columns]
        covs = [c for c in t.columns if c.startswith("cov_")]
        t = t[["id", "item", "resp"] + lead + covs].sort_values(["id", "item"] + lead[:1], kind="stable")
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t.columns else [])).any(), name
        assert t["id"].nunique() >= 100, (name, t["id"].nunique())
        assert t["item"].nunique() >= 3, (name, t["item"].nunique())
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        assert len(name) <= 40, name
        if EXPECT:
            assert len(t) == EXPECT[name], (name, len(t), EXPECT[name])
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    if EXPECT:
        assert set(EXPECT) == set(tables), sorted(set(EXPECT) ^ set(tables))


if __name__ == "__main__":
    main()
