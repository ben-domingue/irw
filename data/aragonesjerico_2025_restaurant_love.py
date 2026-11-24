#!/usr/bin/env python3
# Source: https://zenodo.org/records/14678832
# DOI: 10.5281/zenodo.14678832 (data)
#   Aragonés-Jericó, Cristina; Carmen Rodríguez Santos; Ines Kuster Boluda; Natalia Vila Lopez (2025). Brand loyalty
#     and eWOM: Restaurants experiences
# License: CC BY 4.0 (repository record)
# Data: 650 Spanish restaurant customers. Rows 1-2 of the sheet name the construct and sub-dimension over each
#   column, row 3 the Spanish statement; the script reads past all three and names items by construct and position:
#   brand experience (sensory 2, affective 2, behavioural 1, intellectual 1), brand loyalty (purchase 3, attitudinal
#   2), word of mouth (WOM 4, eWOM 3), brand love (8), utilitarian (2) and hedonic (6) benefits, brand satisfaction
#   (3).
# Tables: one per construct; item = construct code + position in the sheet (e.g. WOM5 = the first eWOM column).
# Covariates: none carried
# PII: none found (string columns screened)
# Item text: not shipped -- the Spanish statements are the second header row; anchors not in the deposit.
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

SOURCES = [{'url': 'https://zenodo.org/api/records/14678832/files/BBDDbrandLoveRestaurants.xlsx/content',
  'kind': 'excel',
  'read_kw': {'header': None, 'skiprows': 3},
  'n_rows': 650,
  'range': (1, 5),
  'blocks': {'aragonesjerico_2025_brand_experience': ['BE1', 'BE2', 'BE3', 'BE4', 'BE5', 'BE6'],
             'aragonesjerico_2025_brand_loyalty': ['BL1', 'BL2', 'BL3', 'BL4', 'BL5'],
             'aragonesjerico_2025_word_of_mouth': ['WOM1', 'WOM2', 'WOM3', 'WOM4', 'WOM5', 'WOM6', 'WOM7'],
             'aragonesjerico_2025_brand_love': ['LOVE1',
                                                'LOVE2',
                                                'LOVE3',
                                                'LOVE4',
                                                'LOVE5',
                                                'LOVE6',
                                                'LOVE7',
                                                'LOVE8'],
             'aragonesjerico_2025_utilitarian_benefit': ['UB1', 'UB2'],
             'aragonesjerico_2025_hedonic_benefit': ['HB1', 'HB2', 'HB3', 'HB4', 'HB5', 'HB6'],
             'aragonesjerico_2025_brand_satisfaction': ['SAT1', 'SAT2', 'SAT3']},
  'covs': {},
  'cov_maps': {},
  'not_shipped': {'EXPERIENCIA': 'unlabelled 1/2 grouping column'},
  'rename': {'0': 'BE1',
             '1': 'BE2',
             '2': 'BE3',
             '3': 'BE4',
             '4': 'BE5',
             '5': 'BE6',
             '6': 'BL1',
             '7': 'BL2',
             '8': 'BL3',
             '9': 'BL4',
             '10': 'BL5',
             '11': 'WOM1',
             '12': 'WOM2',
             '13': 'WOM3',
             '14': 'WOM4',
             '15': 'WOM5',
             '16': 'WOM6',
             '17': 'WOM7',
             '18': 'LOVE1',
             '19': 'LOVE2',
             '20': 'LOVE3',
             '21': 'LOVE4',
             '22': 'LOVE5',
             '23': 'LOVE6',
             '24': 'LOVE7',
             '25': 'LOVE8',
             '26': 'UB1',
             '27': 'UB2',
             '28': 'HB1',
             '29': 'HB2',
             '30': 'HB3',
             '31': 'HB4',
             '32': 'HB5',
             '33': 'HB6',
             '34': 'SAT1',
             '35': 'SAT2',
             '36': 'SAT3',
             '37': 'EXPERIENCIA'},
  'label': 'aragonesjerico_2025_restaurant_love'}]


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
