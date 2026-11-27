#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/HZFAKL
# DOI: 10.7910/DVN/HZFAKL (data)
#   Javadizadeh, Bahareh (2022). Examining Firefighter and Police Officers’ Trust and Service Quality: What
#     Resources Matter? [Dataset]. Harvard Dataverse.
# License: CC0 1.0 (Harvard Dataverse)
# Data: Two US surveys: 120 firefighters (study 1) and 119 police officers (study 2) on service quality, staffing,
#   communication, training, public-service motivation, trust and organisational safety; 1-7 items. Same
#   instruments, stacked with cov_sample (ids prefixed). The fire file's StaffS/TrgC prefixes are the police file's
#   Staff/Trg and are unified to Staff/Trg. Items present in one sample only (e.g. Trust8-13 fire only) stay in the
#   stacked table.
# Tables: one per instrument in the deposit codebook; item = the codebook code. Reverse-keyed (R) items ship as
#   deposited: whether the depositors recoded them is not recorded (their correlations with their scales are mixed in
#   sign), so check direction before scoring.
# Covariates: cov_sample (fire/police)
# PII: none found (string columns screened)
# Item text: available -- Codebook.xlsx gives each item's wording, source (several adapted from SERVQUAL / Vahey;
#   others 'new for this survey') and anchors
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

SOURCES = [{'url': 'https://dataverse.harvard.edu/api/access/datafile/6358307',
  'kind': 'excel',
  'read_kw': {},
  'n_rows': 120,
  'range': (1, 7),
  'blocks': {'javadizadeh_2022_service_quality': ['SerQ1',
                                                  'SerQ2',
                                                  'SerQ3',
                                                  'SerQ4',
                                                  'SerQ5',
                                                  'SerQ6',
                                                  'SerQ7',
                                                  'SerQ8',
                                                  'SerQ9'],
             'javadizadeh_2022_staffing': ['StaffS1',
                                           'StaffS2',
                                           'StaffS3',
                                           'StaffS4',
                                           'StaffS5',
                                           'StaffS6',
                                           'StaffS7',
                                           'StaffS8',
                                           'StaffS9R',
                                           'StaffS10R'],
             'javadizadeh_2022_communication': ['Comm1', 'Comm2', 'Comm3', 'Comm4', 'Comm5', 'Comm6', 'Comm7'],
             'javadizadeh_2022_training': ['TrgC1', 'TrgC2', 'TrgC3', 'TrgC4', 'TrgC5R', 'TrgC6', 'TrgC7', 'TrgC8', 'TrgC9'],
             'javadizadeh_2022_motivation_public_svc': ['MotPS1', 'MotPS2', 'MotPS3', 'MotPS4', 'MotPS5', 'MotPS6'],
             'javadizadeh_2022_trust': ['Trust1',
                                        'Trust2',
                                        'Trust3',
                                        'Trust4',
                                        'Trust5',
                                        'Trust6',
                                        'Trust7',
                                        'Trust8',
                                        'Trust9',
                                        'Trust10',
                                        'Trust11',
                                        'Trust12',
                                        'Trust13',
                                        'Trust14',
                                        'Trust15',
                                        'Trust16',
                                        'Trust17',
                                        'Trust18R'],
             'javadizadeh_2022_psm': ['PSmot1', 'PSmot2', 'PSmot3', 'PSmot4', 'PSmot5'],
             'javadizadeh_2022_org_safety': ['OrgSaf1', 'OrgSaf2', 'OrgSaf3', 'OrgSaf4', 'OrgSaf5', 'OrgSaf6']},
  'covs': {},
  'cov_maps': {},
  'not_shipped': {
                  'Turnov': 'single item',
                  'SERQ': 'composite',
                  'STAFF': 'composite',
                  'COMM': 'composite',
                  'TRG': 'composite',
                  'TRGCOM': 'composite',
                  'MOTPS': 'composite',
                  'TRUST': 'composite',
                  'PSMOT': 'composite',
                  'ORGSAF': 'composite',
                  'TRGA': 'composite'},
  'label': 'javadizadeh_2022_trust_service_quality_fire',
  'item_names': {'SerQ1': 'SerQ1',
                 'SerQ2': 'SerQ2',
                 'SerQ3': 'SerQ3',
                 'SerQ4': 'SerQ4',
                 'SerQ5': 'SerQ5',
                 'SerQ6': 'SerQ6',
                 'SerQ7': 'SerQ7',
                 'SerQ8': 'SerQ8',
                 'SerQ9': 'SerQ9',
                 'StaffS1': 'Staff1',
                 'StaffS2': 'Staff2',
                 'StaffS3': 'Staff3',
                 'StaffS4': 'Staff4',
                 'StaffS5': 'Staff5',
                 'StaffS6': 'Staff6',
                 'StaffS7': 'Staff7',
                 'StaffS8': 'Staff8',
                 'StaffS9R': 'Staff9R',
                 'StaffS10R': 'Staff10R',
                 'Comm1': 'Comm1',
                 'Comm2': 'Comm2',
                 'Comm3': 'Comm3',
                 'Comm4': 'Comm4',
                 'Comm5': 'Comm5',
                 'Comm6': 'Comm6',
                 'Comm7': 'Comm7',
                 'TrgC1': 'Trg1',
                 'TrgC2': 'Trg2',
                 'TrgC3': 'Trg3',
                 'TrgC4': 'Trg4',
                 'TrgC5R': 'Trg5R',
                 'TrgC6': 'Trg6',
                 'TrgC7': 'Trg7',
                 'TrgC8': 'Trg8',
                 'TrgC9': 'Trg9',
                 'MotPS1': 'MotPS1',
                 'MotPS2': 'MotPS2',
                 'MotPS3': 'MotPS3',
                 'MotPS4': 'MotPS4',
                 'MotPS5': 'MotPS5',
                 'MotPS6': 'MotPS6',
                 'Trust1': 'Trust1',
                 'Trust2': 'Trust2',
                 'Trust3': 'Trust3',
                 'Trust4': 'Trust4',
                 'Trust5': 'Trust5',
                 'Trust6': 'Trust6',
                 'Trust7': 'Trust7',
                 'Trust8': 'Trust8',
                 'Trust9': 'Trust9',
                 'Trust10': 'Trust10',
                 'Trust11': 'Trust11',
                 'Trust12': 'Trust12',
                 'Trust13': 'Trust13',
                 'Trust14': 'Trust14',
                 'Trust15': 'Trust15',
                 'Trust16': 'Trust16',
                 'Trust17': 'Trust17',
                 'Trust18R': 'Trust18R',
                 'PSmot1': 'PSmot1',
                 'PSmot2': 'PSmot2',
                 'PSmot3': 'PSmot3',
                 'PSmot4': 'PSmot4',
                 'PSmot5': 'PSmot5',
                 'OrgSaf1': 'OrgSaf1',
                 'OrgSaf2': 'OrgSaf2',
                 'OrgSaf3': 'OrgSaf3',
                 'OrgSaf4': 'OrgSaf4',
                 'OrgSaf5': 'OrgSaf5',
                 'OrgSaf6': 'OrgSaf6'},
  'id_prefix': 'fire',
  'const_covs': {'cov_sample': 'fire'}},
 {'url': 'https://dataverse.harvard.edu/api/access/datafile/6358308',
  'kind': 'excel',
  'read_kw': {},
  'n_rows': 119,
  'range': (1, 7),
  'blocks': {'javadizadeh_2022_service_quality': ['SerQ1',
                                                  'SerQ2',
                                                  'SerQ3',
                                                  'SerQ4',
                                                  'SerQ5',
                                                  'SerQ6',
                                                  'SerQ7',
                                                  'SerQ8',
                                                  'SerQ9'],
             'javadizadeh_2022_training': ['Trg1', 'Trg2', 'Trg3', 'Trg4', 'Trg5R', 'Trg6', 'Trg7', 'Trg8', 'Trg9'],
             'javadizadeh_2022_staffing': ['Staff1',
                                           'Staff2',
                                           'Staff3',
                                           'Staff4',
                                           'Staff5',
                                           'Staff6',
                                           'Staff7',
                                           'Staff8',
                                           'Staff9R',
                                           'Staff10R'],
             'javadizadeh_2022_communication': ['Comm1', 'Comm2', 'Comm3', 'Comm4', 'Comm5', 'Comm6'],
             'javadizadeh_2022_psm': ['PSmot1', 'PSmot2', 'PSmot3', 'PSmot4', 'PSmot5'],
             'javadizadeh_2022_trust': ['Trust1',
                                        'Trust2',
                                        'Trust3',
                                        'Trust4',
                                        'Trust5',
                                        'Trust6',
                                        'Trust7',
                                        'Trust14',
                                        'Trust15',
                                        'Trust16',
                                        'Trust17',
                                        'Trust18R'],
             'javadizadeh_2022_motivation_public_svc': ['MotPS1', 'MotPS2', 'MotPS3', 'MotPS4', 'MotPS5', 'MotPS6'],
             'javadizadeh_2022_org_safety': ['OrgSaf1', 'OrgSaf2', 'OrgSaf3', 'OrgSaf4', 'OrgSaf5', 'OrgSaf6']},
  'covs': {},
  'cov_maps': {},
  'not_shipped': {
                  'SERQ': 'composite',
                  'STAFF': 'composite',
                  'COMM': 'composite',
                  'TRG': 'composite',
                  'TRGCOM': 'composite',
                  'MOTPPS': 'composite',
                  'TRUST': 'composite',
                  'PSMOT': 'composite',
                  'ORGSAF': 'composite',
                  'TRGA': 'composite',
                  'TRUSTA': 'composite'},
  'label': 'javadizadeh_2022_trust_service_quality_police',
  'item_names': {'SerQ1': 'SerQ1',
                 'SerQ2': 'SerQ2',
                 'SerQ3': 'SerQ3',
                 'SerQ4': 'SerQ4',
                 'SerQ5': 'SerQ5',
                 'SerQ6': 'SerQ6',
                 'SerQ7': 'SerQ7',
                 'SerQ8': 'SerQ8',
                 'SerQ9': 'SerQ9',
                 'Trg1': 'Trg1',
                 'Trg2': 'Trg2',
                 'Trg3': 'Trg3',
                 'Trg4': 'Trg4',
                 'Trg5R': 'Trg5R',
                 'Trg6': 'Trg6',
                 'Trg7': 'Trg7',
                 'Trg8': 'Trg8',
                 'Trg9': 'Trg9',
                 'Staff1': 'Staff1',
                 'Staff2': 'Staff2',
                 'Staff3': 'Staff3',
                 'Staff4': 'Staff4',
                 'Staff5': 'Staff5',
                 'Staff6': 'Staff6',
                 'Staff7': 'Staff7',
                 'Staff8': 'Staff8',
                 'Staff9R': 'Staff9R',
                 'Staff10R': 'Staff10R',
                 'Comm1': 'Comm1',
                 'Comm2': 'Comm2',
                 'Comm3': 'Comm3',
                 'Comm4': 'Comm4',
                 'Comm5': 'Comm5',
                 'Comm6': 'Comm6',
                 'PSmot1': 'PSmot1',
                 'PSmot2': 'PSmot2',
                 'PSmot3': 'PSmot3',
                 'PSmot4': 'PSmot4',
                 'PSmot5': 'PSmot5',
                 'Trust1': 'Trust1',
                 'Trust2': 'Trust2',
                 'Trust3': 'Trust3',
                 'Trust4': 'Trust4',
                 'Trust5': 'Trust5',
                 'Trust6': 'Trust6',
                 'Trust7': 'Trust7',
                 'Trust14': 'Trust14',
                 'Trust15': 'Trust15',
                 'Trust16': 'Trust16',
                 'Trust17': 'Trust17',
                 'Trust18R': 'Trust18R',
                 'MotPS1': 'MotPS1',
                 'MotPS2': 'MotPS2',
                 'MotPS3': 'MotPS3',
                 'MotPS4': 'MotPS4',
                 'MotPS5': 'MotPS5',
                 'MotPS6': 'MotPS6',
                 'OrgSaf1': 'OrgSaf1',
                 'OrgSaf2': 'OrgSaf2',
                 'OrgSaf3': 'OrgSaf3',
                 'OrgSaf4': 'OrgSaf4',
                 'OrgSaf5': 'OrgSaf5',
                 'OrgSaf6': 'OrgSaf6'},
  'id_prefix': 'police',
  'const_covs': {'cov_sample': 'police'}}]

# rows written per table (asserted)
EXPECT = {'javadizadeh_2022_communication': 1553,
 'javadizadeh_2022_motivation_public_svc': 1428,
 'javadizadeh_2022_org_safety': 1422,
 'javadizadeh_2022_psm': 1190,
 'javadizadeh_2022_service_quality': 2141,
 'javadizadeh_2022_staffing': 2387,
 'javadizadeh_2022_training': 2150,
 'javadizadeh_2022_trust': 3588}


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
