#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/gy44skzm4p
# DOI: 10.17632/gy44skzm4p.1 (data)
#   瀚浩 孙 (2026). Autonomous or Static: The effect of AI-enabled environmental benefits in shaping consumer green
#     purchase intention database [Dataset]. Mendeley Data.
# License: CC BY 4.0 (Mendeley Data record: share/copy/modify with credit)
# Data: Three online experiments (241, 359, 362 Chinese consumers) on AI-enabled environmental benefits (autonomous
#   vs static, X); 1-7 items. M (5 items) and Y (4 items) are asked in all three, TJ in studies 2 (3 items) and 3 (4
#   items).
# Tables: M, Y and TJ stacked across studies with cov_study; ids prefixed s1_/s2_/s3_. The record never expands M, Y
#   or TJ, so the tables keep the codes (IRW's reading: M the mediator, Y green purchase intention, TJ the
#   moderator).
# Covariates: treat = X (AI-enabled autonomous benefit condition); cov_study; cov_tj_condition (studies 2-3
#   moderator arm, TJBL)
# PII: none found (string columns screened)
# Item text: not shipped -- codes only in the data file; no anchors/wording in the deposit
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

SOURCES = [{'url': 'https://data.mendeley.com/public-files/datasets/gy44skzm4p/files/513bf21a-a7ff-4e68-afdb-c05c92648ee7/file_downloaded',
  'kind': 'excel',
  'read_kw': {'sheet_name': 0},
  'n_rows': 241,
  'range': (1, 7),
  'blocks': {'sun_2026_m': ['M1', 'M2', 'M3', 'M4', 'M5'], 'sun_2026_y': ['Y1', 'Y2', 'Y3', 'Y4']},
  'covs': {},
  'cov_maps': {},
  'not_shipped': {'CZ1': 'manipulation check (2 items)',
                  'CZ2': 'manipulation check (2 items)',
                  'M': 'composite',
                  'Y': 'composite'},
  'label': 'sun_2026_ai_green_benefits_s1',
  'id_prefix': 's1',
  'treat': {'col': 'X', 'map': {0: 0, 1: 1}},
  'const_covs': {'cov_study': 'study1'}},
 {'url': 'https://data.mendeley.com/public-files/datasets/gy44skzm4p/files/55cd0847-79ed-4b95-b078-a91478886fb6/file_downloaded',
  'kind': 'excel',
  'read_kw': {'sheet_name': 0},
  'n_rows': 359,
  'range': (1, 7),
  'blocks': {'sun_2026_m': ['M1', 'M2', 'M3', 'M4', 'M5'],
             'sun_2026_y': ['Y1', 'Y2', 'Y3', 'Y4'],
             'sun_2026_tj': ['TJ1', 'TJ2', 'TJ3']},
  'covs': {'TJBL': 'cov_tj_condition'},
  'cov_maps': {},
  'not_shipped': {'CZ1': 'manipulation check (2 items)',
                  'CZ2': 'manipulation check (2 items)',
                  'M': 'composite',
                  'Y': 'composite',
                  'TJCZ': 'moderator manipulation check',
                  'TJ': 'composite'},
  'label': 'sun_2026_ai_green_benefits_s2',
  'id_prefix': 's2',
  'treat': {'col': 'X', 'map': {0: 0, 1: 1}},
  'const_covs': {'cov_study': 'study2'}},
 {'url': 'https://data.mendeley.com/public-files/datasets/gy44skzm4p/files/74bf9da7-f553-48bb-8ac0-8e72526d0bdc/file_downloaded',
  'kind': 'excel',
  'read_kw': {'sheet_name': 0},
  'n_rows': 362,
  'range': (1, 7),
  'blocks': {'sun_2026_m': ['M1', 'M2', 'M3', 'M4', 'M5'],
             'sun_2026_y': ['Y1', 'Y2', 'Y3', 'Y4'],
             'sun_2026_tj': ['TJ1', 'TJ2', 'TJ3', 'TJ4']},
  'covs': {'TJBL': 'cov_tj_condition'},
  'cov_maps': {},
  'not_shipped': {'CZ1': 'manipulation check (2 items)',
                  'CZ2': 'manipulation check (2 items)',
                  'M': 'composite',
                  'Y': 'composite',
                  'TJCZ': 'moderator manipulation check',
                  'TJ': 'composite'},
  'label': 'sun_2026_ai_green_benefits_s3',
  'id_prefix': 's3',
  'treat': {'col': 'X', 'map': {0: 0, 1: 1}},
  'const_covs': {'cov_study': 'study3'}}]

# rows written per table (asserted)
EXPECT = {'sun_2026_m': 4810, 'sun_2026_tj': 2525, 'sun_2026_y': 3848}


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
