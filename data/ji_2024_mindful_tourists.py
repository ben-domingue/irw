#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/687vv29wsk
# DOI: 10.17632/687vv29wsk.1 (data)
#   Dongyi Ji (2024). Survey Responses from Chinese Tourists: Mindful Consumption and Green Purchase Intention
#     [Dataset]. Mendeley Data.
# License: CC BY 4.0 (Mendeley Data record: share/copy/modify with credit)
# Data: 226 Chinese tourists (Wenjuanxing survey), mindful consumption and green purchase intention, 1-5 items. The
#   deposit's file name says the EC (environmental concern) block was reverse-coded; EC ships as deposited, and which
#   of its items (if any) the depositors flipped is not recorded, so check direction before scoring. One age of 128 is set missing.
# Tables: one per block. A/C/T are IRW's reading of the Chinese labels as the mindful-consumption facets (caring for
#   others' welfare, caring for the environment, temperance); EI is ethical/socially-responsible self-identity.
# Covariates: cov_gender, cov_age, cov_education, cov_income (SPSS codes, Chinese value labels),
#   cov_completion_time_s
# PII: none; Q11 (province-city-district) dropped under the geographic-code rule
# Item text: available -- SPSS variable labels carry the Chinese statements
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

SOURCES = [{'url': 'https://data.mendeley.com/public-files/datasets/687vv29wsk/files/162f68e4-6766-43cd-b48f-64a6d94afef5/file_downloaded',
  'kind': 'sav',
  'read_kw': {},
  'n_rows': 226,
  'range': (1, 5),
  'blocks': {'ji_2024_health_consciousness': ['HC1', 'HC2', 'HC3'],
             'ji_2024_perceived_behav_control': ['PBC1', 'PBC2', 'PBC3', 'PBC4', 'PBC5'],
             'ji_2024_ethical_identity': ['EI1', 'EI2', 'EI3'],
             'ji_2024_green_purchase_intention': ['GPI1', 'GPI2', 'GPI3', 'GPI4', 'GPI5'],
             'ji_2024_mc_caring_others': ['A1', 'A2', 'A3'],
             'ji_2024_mc_caring_environment': ['C1', 'C2', 'C3', 'C4', 'C5'],
             'ji_2024_mc_temperance': ['T1', 'T2', 'T3'],
             'ji_2024_environmental_concern': ['EC1', 'EC2', 'EC3']},
  'covs': {'Q7': 'cov_gender',
           'Q8': 'cov_age',
           'Q9': 'cov_education',
           'Q10': 'cov_income',
           'totalseconds': 'cov_completion_time_s'},
  'cov_maps': {},
  'not_shipped': {'index': 'platform row number (id = row order)',
                  'totalvalue': 'platform total score (derived)',
                  'Q1': 'travel-status screener',
                  'Q2': 'travel-status screener',
                  'Q3': 'travel-status screener',
                  'Q4': 'travel-status screener',
                  'Q5': 'travel-status screener',
                  'Q6': 'travel-status screener',
                  'Q11': 'province-city-district of residence (geographic code rule)'},
  'label': 'ji_2024_mindful_tourists',
  'invalid': {'Q8': ['128']}}]

# rows written per table (asserted)
EXPECT = {'ji_2024_environmental_concern': 678,
 'ji_2024_ethical_identity': 678,
 'ji_2024_green_purchase_intention': 1130,
 'ji_2024_health_consciousness': 678,
 'ji_2024_mc_caring_environment': 1130,
 'ji_2024_mc_caring_others': 678,
 'ji_2024_mc_temperance': 678,
 'ji_2024_perceived_behav_control': 1130}


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
