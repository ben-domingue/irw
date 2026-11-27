#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/NAVJVQ
# DOI: 10.7910/DVN/NAVJVQ (data)
#   Grant, Zack; Green, Jane; Evans, Geoff (2025). Replication Data for: Family Matters: How Concerns about the
#     Financial Wellbeing of Young Relatives Shape the Political Preferences of Older Adults [Dataset]. Harvard
#     Dataverse.
# License: CC0 1.0 (Harvard Dataverse)
# Data: 6,021 British adults (YouGov, 2022), support or opposition for 10 policies (state pension, elder care,
#   childcare, vocational and university education, renewables, affordable and government housing, school meals,
#   elder activities), 1 = Strongly oppose .. 5 = Strongly support; Don't know/skipped/not asked are missing in the
#   cleaned file.
# Tables: one table of the 10 policy-support items; item = the dataset variable name.
# Covariates: cov_age (years), cov_gender (from the 0/1 female flag)
# PII: none found (string columns screened)
# Item text: not shipped -- the Stata labels are truncated summaries; full wording in the deposit's cleaning .do and
#   README
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

SOURCES = [{'url': 'https://dataverse.harvard.edu/api/access/datafile/10866861?format=original',
  'kind': 'dta',
  'read_kw': {},
  'n_rows': 6021,
  'range': (1, 5),
  'blocks': {'grant_2025_policy_support': ['support_pension',
                                           'support_eldercare',
                                           'support_childcare',
                                           'support_vocateduc',
                                           'support_unieduc',
                                           'support_renewables',
                                           'support_affordhousing',
                                           'support_govhousing',
                                           'support_schoolmeal',
                                           'support_elderactivity']},
  'covs': {'age_yg': 'cov_age', 'female': 'cov_gender'},
  'cov_maps': {'cov_gender': {1: 'female', 0: 'male'}},
  'not_shipped': {'response_date': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                   'scale scores',
                  'weight': 'not carried: weights, derived or imputed demographics, other survey questions, scale '
                            'scores',
                  'age10': 'not carried: weights, derived or imputed demographics, other survey questions, scale '
                           'scores',
                  'agegroup_decades': 'not carried: weights, derived or imputed demographics, other survey '
                                      'questions, scale scores',
                  'aged60plus': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                'scale scores',
                  'ethnicity_NA': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                  'scale scores',
                  'ethnicity_imputed': 'not carried: weights, derived or imputed demographics, other survey '
                                       'questions, scale scores',
                  'education_NA': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                  'scale scores',
                  'unidegree_NA': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                  'scale scores',
                  'education_imputed': 'not carried: weights, derived or imputed demographics, other survey '
                                       'questions, scale scores',
                  'unidegree_imputed': 'not carried: weights, derived or imputed demographics, other survey '
                                       'questions, scale scores',
                  'workstatus': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                'scale scores',
                  'nssec_occupclass_NA': 'not carried: weights, derived or imputed demographics, other survey '
                                         'questions, scale scores',
                  'socialgrade_NA': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                    'scale scores',
                  'region_NA': 'not carried: weights, derived or imputed demographics, other survey questions, scale '
                               'scores',
                  'housevalue_logged_imputed': 'not carried: weights, derived or imputed demographics, other survey '
                                               'questions, scale scores',
                  'housevalue_logged_NA': 'not carried: weights, derived or imputed demographics, other survey '
                                          'questions, scale scores',
                  'homevaluegrp_NA': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                     'scale scores',
                  'HHvaluelinear_impute': 'not carried: weights, derived or imputed demographics, other survey '
                                          'questions, scale scores',
                  'HHvaluelinear_NA': 'not carried: weights, derived or imputed demographics, other survey '
                                      'questions, scale scores',
                  'homevaluegrp_imputed': 'not carried: weights, derived or imputed demographics, other survey '
                                          'questions, scale scores',
                  'partnered_NA': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                  'scale scores',
                  'HHincomegrp_NA': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                    'scale scores',
                  'HHincomelinear_NA': 'not carried: weights, derived or imputed demographics, other survey '
                                       'questions, scale scores',
                  'HHincomegrp_imputed': 'not carried: weights, derived or imputed demographics, other survey '
                                         'questions, scale scores',
                  'HHincomelinear_imputed': 'not carried: weights, derived or imputed demographics, other survey '
                                            'questions, scale scores',
                  'HHincomelog_NA': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                    'scale scores',
                  'HHincomelog_imputed': 'not carried: weights, derived or imputed demographics, other survey '
                                         'questions, scale scores',
                  'equivHHincomelinear_NA': 'not carried: weights, derived or imputed demographics, other survey '
                                            'questions, scale scores',
                  'equivHHincomelinear_imputed': 'not carried: weights, derived or imputed demographics, other '
                                                 'survey questions, scale scores',
                  'equivHHincomelog_NA': 'not carried: weights, derived or imputed demographics, other survey '
                                         'questions, scale scores',
                  'equivHHincomelog_imputed': 'not carried: weights, derived or imputed demographics, other survey '
                                              'questions, scale scores',
                  'equivHHincomequintiles_NA': 'not carried: weights, derived or imputed demographics, other survey '
                                               'questions, scale scores',
                  'equivHHincomequintiles_imputed': 'not carried: weights, derived or imputed demographics, other '
                                                    'survey questions, scale scores',
                  'cashsavings_NA': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                    'scale scores',
                  'logcashsavings_NA': 'not carried: weights, derived or imputed demographics, other survey '
                                       'questions, scale scores',
                  'savingsvalue_NA': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                     'scale scores',
                  'cashsavings_imputed': 'not carried: weights, derived or imputed demographics, other survey '
                                         'questions, scale scores',
                  'logcashsavings_imputed': 'not carried: weights, derived or imputed demographics, other survey '
                                            'questions, scale scores',
                  'savingsvalue_imputed': 'not carried: weights, derived or imputed demographics, other survey '
                                          'questions, scale scores',
                  'financesFam20s': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                    'scale scores',
                  'financesFam40s': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                    'scale scores',
                  'financesFam60s': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                    'scale scores',
                  'financesFam20group': 'not carried: weights, derived or imputed demographics, other survey '
                                        'questions, scale scores',
                  'financesFam40group': 'not carried: weights, derived or imputed demographics, other survey '
                                        'questions, scale scores',
                  'financesFam60group': 'not carried: weights, derived or imputed demographics, other survey '
                                        'questions, scale scores',
                  'strugglefam20': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                   'scale scores',
                  'strugglefam40': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                   'scale scores',
                  'strugglefam60': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                   'scale scores',
                  'haschild1839': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                  'scale scores',
                  'hasgrandchild1839': 'not carried: weights, derived or imputed demographics, other survey '
                                       'questions, scale scores',
                  'haschildORgrandchild1839': 'not carried: weights, derived or imputed demographics, other survey '
                                              'questions, scale scores',
                  'olderchild_assetsSIMP': 'not carried: weights, derived or imputed demographics, other survey '
                                           'questions, scale scores',
                  'riskElderly_lin': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                     'scale scores',
                  'riskYouth_lin': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                   'scale scores',
                  'youthpol_scale': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                    'scale scores',
                  'nYARP': 'not carried: weights, derived or imputed demographics, other survey questions, scale '
                           'scores',
                  'nOARP': 'not carried: weights, derived or imputed demographics, other survey questions, scale '
                           'scores',
                  'priority_nYARP': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                    'scale scores',
                  'priority_nOARP': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                    'scale scores',
                  'agree_educVpensions': 'not carried: weights, derived or imputed demographics, other survey '
                                         'questions, scale scores',
                  'BES_nationalEconEvalCombo': 'not carried: weights, derived or imputed demographics, other survey '
                                               'questions, scale scores',
                  'BES_personalEconEvalCombo': 'not carried: weights, derived or imputed demographics, other survey '
                                               'questions, scale scores',
                  'partyID_BES': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                 'scale scores',
                  'shortpartyID_w23': 'not carried: weights, derived or imputed demographics, other survey '
                                      'questions, scale scores',
                  'SIMPintendedvote_2022': 'not carried: weights, derived or imputed demographics, other survey '
                                           'questions, scale scores',
                  'vote_OtherCon': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                   'scale scores',
                  'conLookAfterYoung': 'not carried: weights, derived or imputed demographics, other survey '
                                       'questions, scale scores',
                  'conLookAfterRetired': 'not carried: weights, derived or imputed demographics, other survey '
                                         'questions, scale scores',
                  'priority_youngVold': 'not carried: weights, derived or imputed demographics, other survey '
                                        'questions, scale scores',
                  'priority_pensions': 'not carried: weights, derived or imputed demographics, other survey '
                                       'questions, scale scores',
                  'priority_eldercare': 'not carried: weights, derived or imputed demographics, other survey '
                                        'questions, scale scores',
                  'priority_eldertransport': 'not carried: weights, derived or imputed demographics, other survey '
                                             'questions, scale scores',
                  'priority_winterfuel': 'not carried: weights, derived or imputed demographics, other survey '
                                         'questions, scale scores',
                  'priority_affordhousing': 'not carried: weights, derived or imputed demographics, other survey '
                                            'questions, scale scores',
                  'priority_childcare': 'not carried: weights, derived or imputed demographics, other survey '
                                        'questions, scale scores',
                  'priority_vocateduc': 'not carried: weights, derived or imputed demographics, other survey '
                                        'questions, scale scores',
                  'priority_unieduc': 'not carried: weights, derived or imputed demographics, other survey '
                                      'questions, scale scores',
                  'priority_renewables': 'not carried: weights, derived or imputed demographics, other survey '
                                         'questions, scale scores',
                  'priority_borderforce': 'not carried: weights, derived or imputed demographics, other survey '
                                          'questions, scale scores',
                  'econGenProsp': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                  'scale scores',
                  'econGenRetro': 'not carried: weights, derived or imputed demographics, other survey questions, '
                                  'scale scores',
                  'leftrightscaleID_yg': 'not carried: weights, derived or imputed demographics, other survey '
                                         'questions, scale scores',
                  'BES_selfproTaxSpend_lin': 'not carried: weights, derived or imputed demographics, other survey '
                                             'questions, scale scores',
                  'BES_selfTaxSpend_grp': 'not carried: weights, derived or imputed demographics, other survey '
                                          'questions, scale scores',
                  'BES_selfproImmig_lin': 'not carried: weights, derived or imputed demographics, other survey '
                                          'questions, scale scores',
                  'BES_selfImmig_grp': 'not carried: weights, derived or imputed demographics, other survey '
                                       'questions, scale scores',
                  'eurefchoice2016_yg': 'not carried: weights, derived or imputed demographics, other survey '
                                        'questions, scale scores'},
  'label': 'grant_2025_family_matters',
  'id_col': 'id'}]

# rows written per table (asserted)
EXPECT = {'grant_2025_policy_support': 55335}


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
