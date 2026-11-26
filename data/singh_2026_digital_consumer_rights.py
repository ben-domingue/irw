#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/8g8hrrb2fj
# DOI: 10.17632/8g8hrrb2fj (data)
#   Pranjali Singh (2026). A Large-Scale Survey Dataset on Digital Consumer Rights, Dark Patterns, Online Shopping
#     Disputes and Grievance Behaviour in India
# License: CC BY 4.0 (repository record)
# Data: 712 Indian online consumers (record: digital consumer-rights awareness, dark patterns, disputes, privacy
#   and grievance behaviour). Besides 53 single text-answer questions, the file holds three ten-to-twelve item five-
#   point blocks coded ACR, EDP and CPB; the record does not expand them, so tables are named by code.
# Tables: one per code block, item = the deposit code. Names: IRW's reading of the deposit codes; the record does
#   not expand them.
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

SOURCES = [{'url': 'https://data.mendeley.com/public-files/datasets/8g8hrrb2fj/files/0e6bac33-b676-475a-bcf3-c0e743b2ff2d/file_downloaded',
  'kind': 'excel',
  'read_kw': {},
  'n_rows': 712,
  'range': (1, 5),
  'blocks': {'singh_2026_acr': ['ACR1', 'ACR2', 'ACR3', 'ACR4', 'ACR5', 'ACR6', 'ACR7', 'ACR8', 'ACR9', 'ACR10'],
             'singh_2026_edp': ['EDP1',
                                'EDP2',
                                'EDP3',
                                'EDP4',
                                'EDP5',
                                'EDP6',
                                'EDP7',
                                'EDP8',
                                'EDP9',
                                'EDP10',
                                'EDP11',
                                'EDP12'],
             'singh_2026_cpb': ['CPB1', 'CPB2', 'CPB3', 'CPB4', 'CPB5', 'CPB6', 'CPB7', 'CPB8', 'CPB9', 'CPB10']},
  'covs': {},
  'cov_maps': {},
  'not_shipped': {'Region': 'region of residence (geographic code rule)',
                  'Age Group': 'categorical background, experience-frequency or single-question column (text '
                               'answers), not carried',
                  'Gender': 'categorical background, experience-frequency or single-question column (text answers), '
                            'not carried',
                  'Education': 'categorical background, experience-frequency or single-question column (text '
                               'answers), not carried',
                  'Occupation': 'categorical background, experience-frequency or single-question column (text '
                                'answers), not carried',
                  'Monthly Personal Income': 'categorical background, experience-frequency or single-question column '
                                             '(text answers), not carried',
                  'Residence Type': 'categorical background, experience-frequency or single-question column (text '
                                    'answers), not carried',
                  'Online Purchase Frequency': 'categorical background, experience-frequency or single-question '
                                               'column (text answers), not carried',
                  'Main Digital Channel': 'categorical background, experience-frequency or single-question column '
                                          '(text answers), not carried',
                  'Online Purchase Experience': 'categorical background, experience-frequency or single-question '
                                                'column (text answers), not carried',
                  'Typical Monthly Online Spend': 'categorical background, experience-frequency or single-question '
                                                  'column (text answers), not carried',
                  'Main Device': 'categorical background, experience-frequency or single-question column (text '
                                 'answers), not carried',
                  'Main Payment Method': 'categorical background, experience-frequency or single-question column '
                                         '(text answers), not carried',
                  'Defective Damaged or Different Product': 'categorical background, experience-frequency or '
                                                            'single-question column (text answers), not carried',
                  'Non Delivery or Excessive Delay': 'categorical background, experience-frequency or '
                                                     'single-question column (text answers), not carried',
                  'Refund Difficulty': 'categorical background, experience-frequency or single-question column (text '
                                       'answers), not carried',
                  'Hidden or Unexpected Charges': 'categorical background, experience-frequency or single-question '
                                                  'column (text answers), not carried',
                  'Suspected Counterfeit': 'categorical background, experience-frequency or single-question column '
                                           '(text answers), not carried',
                  'Misleading Ad or Description': 'categorical background, experience-frequency or single-question '
                                                  'column (text answers), not carried',
                  'Unauthorized or Incorrect Charge': 'categorical background, experience-frequency or '
                                                      'single-question column (text answers), not carried',
                  'Subscription Cancellation Difficulty': 'categorical background, experience-frequency or '
                                                          'single-question column (text answers), not carried',
                  'Return or Refund Refusal': 'categorical background, experience-frequency or single-question '
                                              'column (text answers), not carried',
                  'Warranty or After Sales Dispute': 'categorical background, experience-frequency or '
                                                     'single-question column (text answers), not carried',
                  'Ratings Reviews Influence': 'categorical background, experience-frequency or single-question '
                                               'column (text answers), not carried',
                  'Confidence Reviews Genuine': 'categorical background, experience-frequency or single-question '
                                                'column (text answers), not carried',
                  'Suspect Fake or Manipulated Reviews': 'categorical background, experience-frequency or '
                                                         'single-question column (text answers), not carried',
                  'Influencer Endorsement Influence': 'categorical background, experience-frequency or '
                                                      'single-question column (text answers), not carried',
                  'Check Sponsorship Disclosure': 'categorical background, experience-frequency or single-question '
                                                  'column (text answers), not carried',
                  'Product Did Not Perform As Advertised': 'categorical background, experience-frequency or '
                                                           'single-question column (text answers), not carried',
                  'Concern Personal Data Collection': 'categorical background, experience-frequency or '
                                                      'single-question column (text answers), not carried',
                  'Read Privacy Notices': 'categorical background, experience-frequency or single-question column '
                                          '(text answers), not carried',
                  'Stopped Purchase Due to Data Request': 'categorical background, experience-frequency or '
                                                          'single-question column (text answers), not carried',
                  'Unconsented Promotional Contact': 'categorical background, experience-frequency or '
                                                     'single-question column (text answers), not carried',
                  'Comfort Personalized Recommendations': 'categorical background, experience-frequency or '
                                                          'single-question column (text answers), not carried',
                  'First Action When Problem': 'categorical background, experience-frequency or single-question '
                                               'column (text answers), not carried',
                  'Formal Complaint Ever': 'categorical background, experience-frequency or single-question column '
                                           '(text answers), not carried',
                  'Most Recent Complaint Channel': 'categorical background, experience-frequency or single-question '
                                                   'column (text answers), not carried',
                  'Most Recent Complaint Satisfaction': 'categorical background, experience-frequency or '
                                                        'single-question column (text answers), not carried',
                  'Most Recent Complaint Resolution': 'categorical background, experience-frequency or '
                                                      'single-question column (text answers), not carried',
                  'Resolution Time': 'categorical background, experience-frequency or single-question column (text '
                                     'answers), not carried',
                  'Main Reason Not Complaining': 'categorical background, experience-frequency or single-question '
                                                 'column (text answers), not carried',
                  'Future Formal Complaint Likelihood': 'categorical background, experience-frequency or '
                                                        'single-question column (text answers), not carried',
                  'Awareness Platform Grievance': 'categorical background, experience-frequency or single-question '
                                                  'column (text answers), not carried',
                  'Awareness National Consumer Helpline': 'categorical background, experience-frequency or '
                                                          'single-question column (text answers), not carried',
                  'Awareness Consumer Commissions': 'categorical background, experience-frequency or single-question '
                                                    'column (text answers), not carried',
                  'Awareness Online Complaint Mechanisms': 'categorical background, experience-frequency or '
                                                           'single-question column (text answers), not carried',
                  'Awareness Bank Payment Dispute Mechanisms': 'categorical background, experience-frequency or '
                                                               'single-question column (text answers), not carried',
                  'Awareness Cybercrime Reporting': 'categorical background, experience-frequency or single-question '
                                                    'column (text answers), not carried',
                  'Overall Online Shopping Safety': 'categorical background, experience-frequency or single-question '
                                                    'column (text answers), not carried',
                  'Trust Online Platforms Fairness': 'categorical background, experience-frequency or '
                                                     'single-question column (text answers), not carried',
                  'Ease Understanding Online Consumer Rights': 'categorical background, experience-frequency or '
                                                               'single-question column (text answers), not carried',
                  'Ease Obtaining Effective Redress': 'categorical background, experience-frequency or '
                                                      'single-question column (text answers), not carried',
                  'Importance Stronger Consumer Education': 'categorical background, experience-frequency or '
                                                            'single-question column (text answers), not carried'},
  'label': 'singh_2026_digital_consumer_rights'}]


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
