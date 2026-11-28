#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/yb262txrvn
# DOI: 10.17632/yb262txrvn.2 (data)
#   Galina Ilieva; Tania Yankova; Yulia Dzhabarova; Margarita Ruseva; Delian Angelov; Stanislava Klisarova-Belcheva
#     (2023). Impact of COVID-19 Pandemic on Customer Attitude toward E-wallet Payments [Dataset]. Mendeley Data.
# License: CC BY 4.0 (Mendeley Data record: share/copy/modify with credit)
# Data: 257 Bulgarian adults (Google Forms, Nov-Dec 2022) on e-wallet payments after COVID-19, 1-5 agreement items.
#   Read from the deposit's coded CSV; the text CSV was used only to key the demographic codes.
# Tables: one per construct (the bracket prefix of each header); items pu1.. in column order within the construct.
# Covariates: cov_gender, cov_age_group, cov_settlement_size, cov_income, cov_education, cov_hours_online (codes
#   keyed against the deposit's text-valued CSV)
# PII: none; municipality dropped (geographic code rule); the open comment column is not carried
# Item text: available -- the bracketed statements in the headers; questionnaire PDFs in the deposit
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

SOURCES = [{'url': 'https://data.mendeley.com/public-files/datasets/yb262txrvn/files/b1fdce27-79f5-4093-875c-797dca85ce7d/file_downloaded',
  'kind': 'csv',
  'read_kw': {'sep': ';', 'encoding': 'cp1252'},
  'n_rows': 257,
  'range': (1, 5),
  'blocks': {'ilieva_2023_perceived_usefulness': ['Perceived Usefulness [Using an e-wallet makes it easier for me to '
                                                  'conduct my daily transactions]',
                                                  'Perceived Usefulness [Using an e-wallet allows me to manage my '
                                                  'transactions more efficiently]',
                                                  'Perceived Usefulness [Using an e-wallet increases my '
                                                  'productivity]',
                                                  'Perceived Usefulness [Using an e-wallet enables me to accomplish '
                                                  'tasks e.g., payments more quickly]',
                                                  'Perceived Usefulness [Overall, I believe an e-wallet is more '
                                                  'useful than traditional ways of conduct transactions]'],
             'ilieva_2023_perceived_ease_of_use': ['Perceived Easy of Use [Learning how to use an e-Wallet is easy '
                                                   'for me]',
                                                   'Perceived Easy of Use [My interaction with an e-Wallet is clear '
                                                   'and understandable]',
                                                   'Perceived Easy of Use [I find an e-wallet easy to use]',
                                                   'Perceived Easy of Use [It is easy for me to become skillful at '
                                                   'using an e-wallet]',
                                                   'Perceived Easy of Use [It is easy for me to remember how to '
                                                   'perform task with an e-wallet]',
                                                   'Perceived Easy of Use [I like the fact that payments done '
                                                   'through an e-wallet require minimum effort]'],
             'ilieva_2023_social_influence': ['Social Influence [People who influence my behavior think that I '
                                              'should use an e-wallet]',
                                              'Social Influence [People who are important to me think that I should '
                                              'use an e-wallet]',
                                              'Social Influence [E-wallets are widely used by people in my '
                                              'community]',
                                              'Social Influence [Almost all my friends use e-wallets]',
                                              'Social Influence [My family members use e-wallets]'],
             'ilieva_2023_facilitating_conditions': ['Facilitating Conditions [I am given the necessary support and '
                                                     'assistance to use an e-wallet]',
                                                     'Facilitating Conditions [I have the financial and '
                                                     'technological resources required to use an e-wallet]',
                                                     'Facilitating Conditions [I have access to the software and '
                                                     'hardware required to use an e-wallet]',
                                                     'Facilitating Conditions [The e-wallet services I use are well '
                                                     'integrated and provided in a stable service infrastructure]',
                                                     'Facilitating Conditions [My service provider/operator '
                                                     'facilitates the use of an e-wallet]'],
             'ilieva_2023_lifestyle_compatibility': ['Lifestyle Compatibility [Using e-wallet services is compatible '
                                                     'with all aspects of my lifestyle]',
                                                     'Lifestyle Compatibility [Using e-wallet services fits into my '
                                                     'lifestyle]',
                                                     'Lifestyle Compatibility [Using e-wallet services fits well '
                                                     'with the way I like to purchase products and services]',
                                                     'Lifestyle Compatibility [Using e-wallets is completely '
                                                     'compatible with my current situation]'],
             'ilieva_2023_perceived_trust': ['Perceived Trust [I trust that a transaction conducted through an '
                                             'e-wallet is secure and private]',
                                             'Perceived Trust [I trust payments made through e-wallet channels will '
                                             'be processed securely]',
                                             'Perceived Trust [I believe my personal information on an e-wallet will '
                                             'be kept confidential]',
                                             'Perceived Trust [I believe e-wallet providers keeps customers’ best '
                                             'interests in mind]',
                                             'Perceived Trust [I believe that in case of any issue, the e-wallet '
                                             'service provider will provide me assistance]',
                                             'Perceived Trust [I believe that the e-wallet service providers follow '
                                             'consumer laws]'],
             'ilieva_2023_intention_to_use': ['Intention to Use e-Wallet [Assuming that I have access to e-wallet, I '
                                              'intend to use it]',
                                              'Intention to Use e-Wallet [I intend to use an e-wallet if the cost '
                                              'and times is reasonable for me]',
                                              'Intention to Use e-Wallet [I intend to use an e-wallet in the future]',
                                              'Intention to Use e-Wallet [I intend to increase my use of e-wallets '
                                              'in the future]',
                                              'Intention to Use e-Wallet [I intend to continue using an e-wallet '
                                              'more frequently in the future]',
                                              'Intention to Use e-Wallet [I intend to use an e-wallet in my daily '
                                              'life]'],
             'ilieva_2023_adoption': ['Adoption of e-Wallet [I often use an e-wallet to manage my account]',
                                      'Adoption of e-Wallet [I often use an e-wallet to transfer and remit money]',
                                      'Adoption of e-Wallet [I often use an e-wallet to make payments]',
                                      'Adoption of e-Wallet [I subscribe to financial products that are exclusive to '
                                      'mobile banking]']},
  'covs': {'Gender': 'cov_gender',
           'Age Group': 'cov_age_group',
           'Population of place of residence': 'cov_settlement_size',
           'Average monthly income per household member': 'cov_income',
           'Education': 'cov_education',
           'How many hours do you spend online daily average the Internet (excluding work commitments)?': 'cov_hours_online'},
  'cov_maps': {'cov_gender': {1: 'female', 2: 'male'},
               'cov_age_group': {1: '<20', 2: '21-30', 3: '31-40', 4: '41-50', 5: '51+'},
               'cov_settlement_size': {1: '<1000', 2: '1000-50000', 3: '>50000'},
               'cov_income': {1: '<1320 BGN', 2: '>1320 BGN'},
               'cov_education': {1: 'high school', 2: 'bachelor', 3: 'master', 4: 'PhD'},
               'cov_hours_online': {1: '<1', 2: '1-4', 3: '>4'}},
  'not_shipped': {'Timestamp': 'form timestamp',
                  'Municipality (by place of residence)': 'municipality (geographic code rule)',
                  'Do you use e-wallet software?': 'multi-select usage question',
                  'On average, how often have you used an e-wallet per month?': 'single usage-frequency question',
                  'What is your attitude towards e-payments and has the pandemic affected your attitude toward e-wallets?': 'open-ended '
                                                                                                                            'comment'},
  'label': 'ilieva_2023_ewallet_bulgaria',
  'item_names': {'Perceived Usefulness [Using an e-wallet makes it easier for me to conduct my daily transactions]': 'pu1',
                 'Perceived Usefulness [Using an e-wallet allows me to manage my transactions more efficiently]': 'pu2',
                 'Perceived Usefulness [Using an e-wallet increases my productivity]': 'pu3',
                 'Perceived Usefulness [Using an e-wallet enables me to accomplish tasks e.g., payments more quickly]': 'pu4',
                 'Perceived Usefulness [Overall, I believe an e-wallet is more useful than traditional ways of conduct transactions]': 'pu5',
                 'Perceived Easy of Use [Learning how to use an e-Wallet is easy for me]': 'peou1',
                 'Perceived Easy of Use [My interaction with an e-Wallet is clear and understandable]': 'peou2',
                 'Perceived Easy of Use [I find an e-wallet easy to use]': 'peou3',
                 'Perceived Easy of Use [It is easy for me to become skillful at using an e-wallet]': 'peou4',
                 'Perceived Easy of Use [It is easy for me to remember how to perform task with an e-wallet]': 'peou5',
                 'Perceived Easy of Use [I like the fact that payments done through an e-wallet require minimum effort]': 'peou6',
                 'Social Influence [People who influence my behavior think that I should use an e-wallet]': 'si1',
                 'Social Influence [People who are important to me think that I should use an e-wallet]': 'si2',
                 'Social Influence [E-wallets are widely used by people in my community]': 'si3',
                 'Social Influence [Almost all my friends use e-wallets]': 'si4',
                 'Social Influence [My family members use e-wallets]': 'si5',
                 'Facilitating Conditions [I am given the necessary support and assistance to use an e-wallet]': 'fc1',
                 'Facilitating Conditions [I have the financial and technological resources required to use an e-wallet]': 'fc2',
                 'Facilitating Conditions [I have access to the software and hardware required to use an e-wallet]': 'fc3',
                 'Facilitating Conditions [The e-wallet services I use are well integrated and provided in a stable service infrastructure]': 'fc4',
                 'Facilitating Conditions [My service provider/operator facilitates the use of an e-wallet]': 'fc5',
                 'Lifestyle Compatibility [Using e-wallet services is compatible with all aspects of my lifestyle]': 'lc1',
                 'Lifestyle Compatibility [Using e-wallet services fits into my lifestyle]': 'lc2',
                 'Lifestyle Compatibility [Using e-wallet services fits well with the way I like to purchase products and services]': 'lc3',
                 'Lifestyle Compatibility [Using e-wallets is completely compatible with my current situation]': 'lc4',
                 'Perceived Trust [I trust that a transaction conducted through an e-wallet is secure and private]': 'pt1',
                 'Perceived Trust [I trust payments made through e-wallet channels will be processed securely]': 'pt2',
                 'Perceived Trust [I believe my personal information on an e-wallet will be kept confidential]': 'pt3',
                 'Perceived Trust [I believe e-wallet providers keeps customers’ best interests in mind]': 'pt4',
                 'Perceived Trust [I believe that in case of any issue, the e-wallet service provider will provide me assistance]': 'pt5',
                 'Perceived Trust [I believe that the e-wallet service providers follow consumer laws]': 'pt6',
                 'Intention to Use e-Wallet [Assuming that I have access to e-wallet, I intend to use it]': 'int1',
                 'Intention to Use e-Wallet [I intend to use an e-wallet if the cost and times is reasonable for me]': 'int2',
                 'Intention to Use e-Wallet [I intend to use an e-wallet in the future]': 'int3',
                 'Intention to Use e-Wallet [I intend to increase my use of e-wallets in the future]': 'int4',
                 'Intention to Use e-Wallet [I intend to continue using an e-wallet more frequently in the future]': 'int5',
                 'Intention to Use e-Wallet [I intend to use an e-wallet in my daily life]': 'int6',
                 'Adoption of e-Wallet [I often use an e-wallet to manage my account]': 'ad1',
                 'Adoption of e-Wallet [I often use an e-wallet to transfer and remit money]': 'ad2',
                 'Adoption of e-Wallet [I often use an e-wallet to make payments]': 'ad3',
                 'Adoption of e-Wallet [I subscribe to financial products that are exclusive to mobile banking]': 'ad4'}}]

# rows written per table (asserted)
EXPECT = {'ilieva_2023_adoption': 1028,
 'ilieva_2023_facilitating_conditions': 1285,
 'ilieva_2023_intention_to_use': 1542,
 'ilieva_2023_lifestyle_compatibility': 1028,
 'ilieva_2023_perceived_ease_of_use': 1542,
 'ilieva_2023_perceived_trust': 1542,
 'ilieva_2023_perceived_usefulness': 1285,
 'ilieva_2023_social_influence': 1285}


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
