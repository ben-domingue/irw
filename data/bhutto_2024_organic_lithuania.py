#!/usr/bin/env python3
# Source: https://zenodo.org/records/13889210
# DOI: 10.5281/zenodo.13889210 (data)
#   MUHAMMAD YASEEN, Bhutto; Rūtelionė, Aušra (2024). Organic food consumption behavior in Lithuania
# License: CC BY 4.0 (repository record)
# Data: 1,000 Lithuanian adults (KTU Ekomaistas project). Every item carries its Lithuanian wording as an SPSS
#   variable label; construct names read from the code prefixes (FQ quality, FP price, SV social, CV conditional, EV
#   emotional, EP epistemic value; ES environmental self-identity; PI purchase intention; RB/UB/VB/IB/TB risk,
#   usage, value, image, tradition barriers; HC health consciousness; EL environmental literacy) -- IRW's reading of
#   standard codes.
# Tables: one per construct; the two-item image and tradition barriers ship as two-item tables.
# Covariates: cov_gender (D1 value labels: 1 Moteris = female, 2 Vyras = male, 3 Kita = other), cov_age.
# PII: none found (string columns screened)
# Item text: not shipped -- Lithuanian stems (variable labels) and the five agreement anchors (value labels) are
#   both in the .sav; cheap later build, needs register rows.
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

SOURCES = [{'url': 'https://zenodo.org/api/records/13889210/files/KTU_Ekomaistas_FINAL_20230801.sav/content',
  'kind': 'sav',
  'n_rows': 1000,
  'range': (1, 5),
  'id_col': 'record',
  'blocks': {'bhutto_2024_organic_quality': ['FQr1', 'FQr2', 'FQr3'],
             'bhutto_2024_organic_price': ['FPr1', 'FPr2', 'FPr3'],
             'bhutto_2024_organic_social_value': ['SVr1', 'SVr2', 'SVr3'],
             'bhutto_2024_organic_conditional_val': ['CVr1', 'CVr2', 'CVr3'],
             'bhutto_2024_organic_emotional_value': ['EVr1', 'EVr2', 'EVr3'],
             'bhutto_2024_organic_epistemic_value': ['EPr1', 'EPr2', 'EPr3', 'EPr4'],
             'bhutto_2024_env_self_identity': ['ESr1', 'ESr2', 'ESr3'],
             'bhutto_2024_organic_purchase_intent': ['PIr1', 'PIr2', 'PIr3', 'PIr4'],
             'bhutto_2024_organic_risk_barrier': ['RBr1', 'RBr2', 'RBr3'],
             'bhutto_2024_organic_usage_barrier': ['UBr1', 'UBr2', 'UBr3'],
             'bhutto_2024_organic_value_barrier': ['VBr1', 'VBr2', 'VBr3', 'VBr4'],
             'bhutto_2024_organic_image_barrier': ['IBr1', 'IBr2'],
             'bhutto_2024_organic_tradition_barrier': ['TBr1', 'TBr2'],
             'bhutto_2024_health_consciousness': ['HCr1', 'HCr2', 'HCr3'],
             'bhutto_2024_env_literacy': ['ELr1', 'ELr2', 'ELr3']},
  'covs': {'D1': 'cov_gender', 'D2': 'cov_age'},
  'cov_maps': {'cov_gender': {1.0: 'female', 2.0: 'male', 3.0: 'other'}},
  'not_shipped': {'date': 'completion timestamp',
                  'D2C': 'age recode (derived)',
                  'D3': 'county of residence (geographic code rule)',
                  'A1': 'organic purchase frequency, not carried',
                  'A2': 'household income band, not carried',
                  'A3': 'education, not carried'},
  'label': 'bhutto_2024_organic_lithuania'}]


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
