#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/7pwhtgfn9f
# DOI: 10.17632/7pwhtgfn9f.1 (data)
#   Naman Sreen; Pradip Sadarangani; SHANKAR PURBEY (2017). Data for: IMPACT OF CULTURE, BEHAVIOR, AND GENDER ON
#     GREEN PURCHASE INTENTION [Dataset]. Mendeley Data.
# License: CC BY 4.0 (Mendeley Data record: share/copy/modify with credit)
# Data: 452 educated urban Indian consumers (Google Form, 2017), 1-5 agreement items; the study behind Sreen, Purbey
#   & Sadarangani (2018), Journal of Retailing and Consumer Services 41:177-189,
#   doi:10.1016/j.jretconser.2017.12.002.
# Tables: one per construct. The headers are the full statements; the blocks (TPB attitude, subjective norm, PBC,
#   intention; collectivism, long-term orientation, man-nature orientation, environmental knowledge) are IRW's
#   reading of the statements in sheet order. The subjective-norm statement that sits after the collectivism block
#   (column 24) is sn4. Item codes are the block abbreviation + position within the block in sheet order (att1 =
#   column 5 ... ek5 = column 38).
# Covariates: cov_education, cov_income (annual, lakh rupees), cov_gender ('Male, Female' -> missing)
# PII: none found (string columns screened)
# Item text: available -- the column headers are the English statements
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

SOURCES = [{'url': 'https://data.mendeley.com/public-files/datasets/7pwhtgfn9f/files/a6839dd3-ddf0-4d44-8544-088711917b01/file_downloaded',
  'kind': 'excel',
  'read_kw': {'sheet_name': 'Form Responses 1'},
  'n_rows': 452,
  'range': (1, 5),
  'blocks': {'sreen_2017_attitude': ['Environmental protection is important to me when making product purchases',
                                     'I believe that green products help to reduce pollution(water,air,etc.)',
                                     'I believe that green products help to save nature and its resources',
                                     'Given a choice i will prefer a green product over a conventional product'],
             'sreen_2017_subjective_norm': ['People who are important to me thinks that i should buy green products',
                                            'My interaction with people influences me to buy green products',
                                            'My acquaintances would approve of my decision to buy green products',
                                            'People who are important to me want me to buy green products'],
             'sreen_2017_perceived_behav_control': ['It is entirely my decision to buy green products',
                                                    'I cannot pay more to buy green products',
                                                    'I require a lot of time to search for green products',
                                                    'I am confident about credibility of green product labels ( ex: '
                                                    'energy efficient rating such as 5 star energy efficient)'],
             'sreen_2017_purchase_intention': ['I intend to buy green products',
                                               'I plan to purchase green products',
                                               'I will purchase green products in my next purchase'],
             'sreen_2017_collectivism': ['The well-being of my group members is important for me',
                                         'Individuals should only pursue their goals after considering the welfare '
                                         'of the group',
                                         'I work hard for the goals of a group, even if it does not result in '
                                         'personal recognition',
                                         'Family members should stick together, even if they do not agree',
                                         'I enjoy sharing items and spending time with my group members'],
             'sreen_2017_long_term_orientation': ['I tend to use my money carefully in present so that i can save it '
                                                  'for future',
                                                  'Failure does not stop me from trying again again',
                                                  'I work hard for success in future',
                                                  'I would like to be secure in the future and hence i prefer long '
                                                  'term planning',
                                                  'I don’t mind giving up today’s fun for success in the future'],
             'sreen_2017_man_nature_orientation': ['It is important for me to understand the ways of nature and act '
                                                   'accordingly',
                                                   'I should maintain harmony with nature',
                                                   'Being the master of the world, human beings are entitled to '
                                                   'deploy any of the natural resources as they like',
                                                   'Human beings are only part of nature'],
             'sreen_2017_environmental_knowledge': ['I am familiar with the environmental phrases and symbols on '
                                                    'product packages',
                                                    'I am very knowledgeable about environmental issues in my '
                                                    'country',
                                                    'I know which products are environmentally friendly products and '
                                                    'i prefer to buy them',
                                                    'I know how to select products and packages that reduce the '
                                                    'amount of waste ending up in landfills',
                                                    'I understand the phrases wet waste and dry waste and can sort '
                                                    'it properly']},
  'covs': {'Education': 'cov_education', 'Income Level': 'cov_income', 'Gender': 'cov_gender'},
  'cov_maps': {'cov_gender': {'Male': 'male', 'Female': 'female', 'Male, Female': None},
               'cov_education': {'Graduate': 'graduate',
                                 'Post graduate': 'postgraduate',
                                 'Post Graduate': 'postgraduate',
                                 'Undergraduate': 'undergraduate',
                                 'Under graduate': 'undergraduate',
                                 'Doctorate': 'doctorate',
                                 'High School': 'high school'},
               'cov_income': {'less than 2 lakhs per annum': '<2 lakh',
                              'between 2-4 lakhs per annum': '2-4 lakh',
                              'between 4-6 lakhs per annum': '4-6 lakh',
                              '6 lakhs per annum and above': '>=6 lakh'}},
  'not_shipped': {'Timestamp': 'form timestamp (half the rows blank)'},
  'label': 'sreen_2017_green_purchase',
  'item_names': {'Environmental protection is important to me when making product purchases': 'att1',
                 'I believe that green products help to reduce pollution(water,air,etc.)': 'att2',
                 'I believe that green products help to save nature and its resources': 'att3',
                 'Given a choice i will prefer a green product over a conventional product': 'att4',
                 'People who are important to me thinks that i should buy green products': 'sn1',
                 'My interaction with people influences me to buy green products': 'sn2',
                 'My acquaintances would approve of my decision to buy green products': 'sn3',
                 'People who are important to me want me to buy green products': 'sn4',
                 'It is entirely my decision to buy green products': 'pbc1',
                 'I cannot pay more to buy green products': 'pbc2',
                 'I require a lot of time to search for green products': 'pbc3',
                 'I am confident about credibility of green product labels ( ex: energy efficient rating such as 5 star energy efficient)': 'pbc4',
                 'I intend to buy green products': 'pi1',
                 'I plan to purchase green products': 'pi2',
                 'I will purchase green products in my next purchase': 'pi3',
                 'The well-being of my group members is important for me': 'col1',
                 'Individuals should only pursue their goals after considering the welfare of the group': 'col2',
                 'I work hard for the goals of a group, even if it does not result in personal recognition': 'col3',
                 'Family members should stick together, even if they do not agree': 'col4',
                 'I enjoy sharing items and spending time with my group members': 'col5',
                 'I tend to use my money carefully in present so that i can save it for future': 'lto1',
                 'Failure does not stop me from trying again again': 'lto2',
                 'I work hard for success in future': 'lto3',
                 'I would like to be secure in the future and hence i prefer long term planning': 'lto4',
                 'I don’t mind giving up today’s fun for success in the future': 'lto5',
                 'It is important for me to understand the ways of nature and act accordingly': 'mno1',
                 'I should maintain harmony with nature': 'mno2',
                 'Being the master of the world, human beings are entitled to deploy any of the natural resources as they like': 'mno3',
                 'Human beings are only part of nature': 'mno4',
                 'I am familiar with the environmental phrases and symbols on product packages': 'ek1',
                 'I am very knowledgeable about environmental issues in my country': 'ek2',
                 'I know which products are environmentally friendly products and i prefer to buy them': 'ek3',
                 'I know how to select products and packages that reduce the amount of waste ending up in landfills': 'ek4',
                 'I understand the phrases wet waste and dry waste and can sort it properly': 'ek5'}}]

# rows written per table (asserted)
EXPECT = {'sreen_2017_attitude': 1808,
 'sreen_2017_collectivism': 2260,
 'sreen_2017_environmental_knowledge': 2260,
 'sreen_2017_long_term_orientation': 2260,
 'sreen_2017_man_nature_orientation': 1808,
 'sreen_2017_perceived_behav_control': 1808,
 'sreen_2017_purchase_intention': 1356,
 'sreen_2017_subjective_norm': 1808}


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
