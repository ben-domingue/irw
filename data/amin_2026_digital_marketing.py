#!/usr/bin/env python3
# Source: https://zenodo.org/records/22105174
# DOI: 10.5281/zenodo.22105174 (data)
#   Amin, Farhan; Khan, Muhammad (2026). A Mixed-Method approach to understanding the Impact of Digital Marketing
#     Strategies on Brand Trust and Consumer Behavior in E-Commerce Sector [Dataset]. Zenodo.
# License: CC BY 4.0 (Zenodo record)
# Data: 771 Pakistani online shoppers (screened 'yes' to having bought online), 1-5 items, from the deposit's
#   processed file. One EM4 cell reads 6 on a 1-5 item (isolated to that item): set missing. The processed file's
#   'BR3' is the third brand-trust item (BT1, BT2, BR3, BT4, BT5) and is renamed BT3.
# Tables: one per construct in the deposit's Survey Instrument (construct mapping table), item = the deposit code.
# Covariates: none carried
# PII: none found (string columns screened)
# Item text: available -- 1 Supplementary_Material Raw_Data_Instrument.xlsx headers hold the full statements; the
#   Survey Instrument docx gives abbreviated wording per code
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

SOURCES = [{'url': 'https://zenodo.org/api/records/22105174/files/2%20Supplementary_Material%20Proceed%20Data.csv/content',
  'kind': 'csv',
  'read_kw': {'encoding': 'cp1252'},
  'n_rows': 771,
  'range': (1, 5),
  'blocks': {'amin_2026_social_media_advertising': ['SMA1', 'SMA2', 'SMA3', 'SMA4', 'SMA5'],
             'amin_2026_search_engine_optimization': ['SEO1', 'SEO2', 'SEO3', 'SEO4', 'SEO5'],
             'amin_2026_email_marketing': ['EM1', 'EM2', 'EM3', 'EM4', 'EM5'],
             'amin_2026_influencer_marketing': ['IM1', 'IM2', 'IM3', 'IM4', 'IM5'],
             'amin_2026_content_marketing': ['CM1', 'CM2', 'CM3', 'CM4', 'CM5'],
             'amin_2026_brand_trust': ['BT1', 'BT2', 'BR3', 'BT4', 'BT5'],
             'amin_2026_purchase_intention': ['PI1', 'PI2', 'PI3', 'PI4', 'PI5'],
             'amin_2026_brand_awareness': ['BA1', 'BA2', 'BA3', 'BA4', 'BA5'],
             'amin_2026_customer_engagement': ['CE1', 'CE2', 'CE3', 'CE4', 'CE5']},
  'covs': {},
  'cov_maps': {},
  'not_shipped': {'Gender': "coded demographic (key not in the deposit's processed file)",
                  'Age': "coded demographic (key not in the deposit's processed file)",
                  'Educational Level': "coded demographic (key not in the deposit's processed file)",
                  'Monthly Income': "coded demographic (key not in the deposit's processed file)",
                  'Employment Status': "coded demographic (key not in the deposit's processed file)",
                  'Frequency of Online Shopping': "coded demographic (key not in the deposit's processed file)",
                  'Preferred Device for Online Shopping': "coded demographic (key not in the deposit's processed "
                                                          'file)'},
  'label': 'amin_2026_digital_marketing',
  'item_names': {'BR3': 'BT3'},
  'invalid': {'EM4': [6]}}]

# rows written per table (asserted)
EXPECT = {'amin_2026_brand_awareness': 3855,
 'amin_2026_brand_trust': 3855,
 'amin_2026_content_marketing': 3855,
 'amin_2026_customer_engagement': 3855,
 'amin_2026_email_marketing': 3848,
 'amin_2026_influencer_marketing': 3855,
 'amin_2026_purchase_intention': 3855,
 'amin_2026_search_engine_optimization': 3855,
 'amin_2026_social_media_advertising': 3855}


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
