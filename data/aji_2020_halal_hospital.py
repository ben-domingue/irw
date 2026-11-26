#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/f77pbdkmn6
# DOI: 10.17632/f77pbdkmn6 (data)
#   Hendy Mustiko Aji (2020). Impact of brand self-expressive value on halal brand personality, brand tribalism and
#     brand loyalty: Case of Islamic hospitals
# License: CC BY 4.0 (repository record)
# Data: 214 Muslim visitors to Islamic hospitals in Yogyakarta. The .sav carries no labels; each item block was
#   tied to the deposit's own composite (Purity, Safety, Sophistication, Righteousness, Self_Expressive, Tribalism,
#   Loyalty) by checking the composite equals the block mean exactly for every row. Item numbers skip where the
#   authors dropped items.
# Tables: one per construct, item = the deposit code.
# Covariates: none carried
# PII: none found (string columns screened)
# Item text: not shipped -- codes only in the data file; no anchors/wording in the deposit
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

SOURCES = [{'url': 'https://data.mendeley.com/public-files/datasets/f77pbdkmn6/files/f1828be3-98e4-472a-9fa8-c06432b575c5/file_downloaded',
  'kind': 'sav',
  'read_kw': {},
  'n_rows': 214,
  'range': (1, 5),
  'blocks': {'aji_2020_halal_purity': ['A.HBP1', 'A.HBP2', 'A.HBP3', 'A.HBP4'],
             'aji_2020_halal_safety': ['C.HBP7', 'C.HBP8', 'C.HBP9'],
             'aji_2020_halal_sophistication': ['D.HBP10', 'D.HBP11', 'D.HBP12', 'D.HBP13'],
             'aji_2020_halal_righteousness': ['E.HBP14', 'E.HBP15', 'E.HBP16'],
             'aji_2020_halal_brand_loyalty': ['BL1', 'BL2', 'BL3', 'BL4'],
             'aji_2020_halal_brand_tribalism': ['B.BT3', 'B.BT4', 'B.BT5', 'D.BT8', 'D.BT9'],
             'aji_2020_halal_self_expressive_value': ['A.SEV1', 'A.SEV2', 'B.SEV3', 'B.SEV4', 'B.SEV5']},
  'covs': {},
  'cov_maps': {},
  'not_shipped': {'Purity': 'composite (mean of A.HBP items, verified)',
                  'Safety': 'composite (C.HBP, verified)',
                  'Sophistication': 'composite (D.HBP, verified)',
                  'Righteousness': 'composite (E.HBP, verified)',
                  'Self_Expressive': 'composite (verified)',
                  'Tribalism': 'composite (verified)',
                  'Loyalty': 'composite (verified)',
                  'Gender': 'unlabelled demographic code, not carried',
                  'Marriage': 'unlabelled demographic code, not carried',
                  'Religion': 'unlabelled demographic code, not carried',
                  'YearBorn': 'unlabelled demographic code, not carried',
                  'Expenditure': 'unlabelled demographic code, not carried',
                  'Education': 'unlabelled demographic code, not carried',
                  'Job': 'unlabelled demographic code, not carried'},
  'label': 'aji_2020_halal_hospital'}]


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
