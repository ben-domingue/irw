#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/d7sdn42v4m
# DOI: 10.17632/d7sdn42v4m (data)
#   Hiroaki Sakai (2026). Final analytic dataset for perceived value, brand attachment, and brand loyalty intentions
#     across product-category groups
# License: CC BY 4.0 (repository record)
# Data: 2,092 Japanese consumers attached to a brand (Cross Marketing panel, March and May 2021), the authors'
#   final analytic file. Question_Items.docx lists the wording: Q2 = 36 perceived-brand-value statements
#   (functional, emotional, self-expressive and social value, pooled), Q3 = brand attachment (brand-self connection
#   and prominence items, Park et al. 2010: Q3.1-3.5, 3.7) and loyalty intentions (the remaining Q3 items), all 1-7.
#   The authors dropped Q2.22, 2.25, 2.26, 2.29 and Q3.1-3.2 in their models; they ship here as administered.
# Tables: sakai_2026_perceived_brand_value (36), _brand_attachment (6), _brand_loyalty (12); item = the deposit
#   code.
# Covariates: cov_gender (SC1: 1 male, 2 female per the questionnaire), cov_age, cov_product_category (price x
#   visibility group).
# PII: none found (string columns screened)
# q3_17 ("I am thinking about switching ... (reverse)") is stored as answered (r = -.15 to -.17 with q3_14 and
#   q3_18), not reverse-keyed.
# Item text: not shipped -- English wording of every item is in Question_Items.docx (listed in order, codes by
#   position); the seven anchors are only "1 = strongly disagree .. 7 = strongly agree" on the Dataverse twin; cheap
#   later build.
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

SOURCES = [{'url': 'https://data.mendeley.com/public-files/datasets/d7sdn42v4m/files/7c211ca3-ac68-43fd-9e92-f938df1471ab/file_downloaded',
  'kind': 'excel',
  'read_kw': {},
  'n_rows': 2092,
  'range': (1, 7),
  'blocks': {'sakai_2026_perceived_brand_value': ['q2_1',
                                                  'q2_2',
                                                  'q2_3',
                                                  'q2_4',
                                                  'q2_5',
                                                  'q2_6',
                                                  'q2_7',
                                                  'q2_8',
                                                  'q2_9',
                                                  'q2_10',
                                                  'q2_11',
                                                  'q2_12',
                                                  'q2_13',
                                                  'q2_14',
                                                  'q2_15',
                                                  'q2_16',
                                                  'q2_17',
                                                  'q2_18',
                                                  'q2_19',
                                                  'q2_20',
                                                  'q2_21',
                                                  'q2_22',
                                                  'q2_23',
                                                  'q2_24',
                                                  'q2_25',
                                                  'q2_26',
                                                  'q2_27',
                                                  'q2_28',
                                                  'q2_29',
                                                  'q2_30',
                                                  'q2_31',
                                                  'q2_32',
                                                  'q2_33',
                                                  'q2_34',
                                                  'q2_35',
                                                  'q2_36'],
             'sakai_2026_brand_attachment': ['q3_1', 'q3_2', 'q3_3', 'q3_4', 'q3_5', 'q3_7'],
             'sakai_2026_brand_loyalty': ['q3_6',
                                          'q3_8',
                                          'q3_9',
                                          'q3_10',
                                          'q3_11',
                                          'q3_12',
                                          'q3_13',
                                          'q3_14',
                                          'q3_15',
                                          'q3_16.LDB',
                                          'q3_17.LDB',
                                          'q3_18.LDB']},
  'covs': {'sc1': 'cov_gender', 'sc2_1': 'cov_age', 'category': 'cov_product_category'},
  'cov_maps': {'cov_gender': {1: 'male', 2: 'female'}},
  'not_shipped': {'no': 'respondent number (not unique across the two survey waves; id = row order)',
                  'sc3': 'prefecture of residence (geographic code rule)',
                  'q1_1': 'open-ended brand name',
                  'q1_2_1': 'open-ended product category',
                  'sc4': 'category screener (carried as cov_product_category)',
                  'group': 'category x wave group code'},
  'label': 'sakai_2026_brand_attachment_value'}]


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
