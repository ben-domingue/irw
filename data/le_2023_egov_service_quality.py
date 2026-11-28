#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/C4IL6G
# DOI: 10.7910/DVN/C4IL6G (data)
#   Le, Mai Thi Thu (2023). Replication Data for: E-government service quality, perceived value, satisfaction, and
#     loyalty: Evidence from a newly emerging country [Dataset]. Harvard Dataverse.
# License: CC0 1.0 (Harvard Dataverse)
# Data: 340 citizens using e-government services in Vietnam (a newly emerging country), 1 = Totally disagree .. 5 =
#   Totally agree. The same .sav is deposited again as Dataverse BZK0LB (lead 92, identical; not shipped).
# Tables: one per construct, item = the SPSS name.
# Covariates: cov_gender, cov_age_group, cov_education (SPSS codes, labelled in the .sav)
# PII: none found (string columns screened)
# Item text: not shipped -- no variable labels; value labels carry only the agreement anchors
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

SOURCES = [{'url': 'https://dataverse.harvard.edu/api/access/datafile/7356583?format=original',
  'kind': 'sav',
  'read_kw': {},
  'n_rows': 340,
  'range': (1, 5),
  'blocks': {'le_2023_ease_of_interaction': ['Easeofinteraction1',
                                             'Easeofinteraction2',
                                             'Easeofinteraction3',
                                             'Easeofinteraction4',
                                             'Easeofinteraction5',
                                             'Easeofinteraction6',
                                             'Easeofinteraction7',
                                             'Easeofinteraction8',
                                             'Easeofinteraction9'],
             'le_2023_fulfillment': ['Fulfillment1',
                                     'Fulfillment2',
                                     'Fulfillment3',
                                     'Fulfillment4',
                                     'Fulfillment5',
                                     'Fulfillment6',
                                     'Fulfillment7',
                                     'Fulfillment8',
                                     'Fulfillment9',
                                     'Fulfillment10'],
             'le_2023_security_privacy': ['SecurityandPrivacy1',
                                          'SecurityandPrivacy2',
                                          'SecurityandPrivacy3',
                                          'SecurityandPrivacy4',
                                          'SecurityandPrivacy5',
                                          'SecurityandPrivacy6',
                                          'SecurityandPrivacy7'],
             'le_2023_citizen_care': ['CitizenCare1', 'CitizenCare2', 'CitizenCare3', 'CitizenCare4', 'CitizenCare5'],
             'le_2023_trustworthiness': ['Trustworthiness1',
                                         'Trustworthiness2',
                                         'Trustworthiness3',
                                         'Trustworthiness4',
                                         'Trustworthiness5'],
             'le_2023_perceived_value': ['PerceivedValue1',
                                         'PerceivedValue2',
                                         'PerceivedValue3',
                                         'PerceivedValue4',
                                         'PerceivedValue5'],
             'le_2023_satisfaction': ['Satisfaction1',
                                      'Satisfaction2',
                                      'Satisfaction3',
                                      'Satisfaction4',
                                      'Satisfaction5'],
             'le_2023_loyalty': ['Loyalty1', 'Loyalty2', 'Loyalty3', 'Loyalty4', 'Loyalty5', 'Loyalty6']},
  'covs': {'Gender': 'cov_gender', 'Age': 'cov_age_group', 'Education': 'cov_education'},
  'cov_maps': {},
  'not_shipped': {},
  'label': 'le_2023_egov_service_quality'}]

# rows written per table (asserted)
EXPECT = {'le_2023_citizen_care': 1700,
 'le_2023_ease_of_interaction': 3060,
 'le_2023_fulfillment': 3400,
 'le_2023_loyalty': 2040,
 'le_2023_perceived_value': 1700,
 'le_2023_satisfaction': 1700,
 'le_2023_security_privacy': 2380,
 'le_2023_trustworthiness': 1700}


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
