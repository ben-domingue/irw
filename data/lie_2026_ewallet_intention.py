#!/usr/bin/env python3
# Source: https://zenodo.org/records/24362742
# DOI: 10.5281/zenodo.24362742 (data)
#   Lie, Yulius; Utomo, Kawang (2026). Study of Important Factors Affecting Intentions in using E-Wallet for Online
#     Transactions [Dataset]. Zenodo.
# License: CC BY 4.0 (Zenodo record)
# Data: 190 Indonesian e-wallet users (Jakarta area), 1-5 items.
# Tables: one per construct (TAM usefulness, ease of use, perceived risk, intention), IRW's reading of the statement
#   headers in sheet order; items pu1.. by position within each block.
# Covariates: cov_gender, cov_age_group, cov_monthly_expenses (as printed)
# PII: none; Domicile dropped (geographic code rule)
# Item text: available -- the headers are the English statements
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

SOURCES = [{'url': 'https://zenodo.org/api/records/24362742/files/Study%20of%20Important%20Factors%20Affecting%20Intentions%20in%20using%20E-Wallet%20for%20Online%20Transactions%20(Responses).xlsx/content',
  'kind': 'excel',
  'read_kw': {},
  'n_rows': 190,
  'range': (1, 5),
  'blocks': {'lie_2026_perceived_usefulness': ['Using an e-wallet helps me complete my daily routines more quickly',
                                               'Using an e-wallet improves my performance in daily life activities',
                                               'Using an e-wallet increases my overall productivity',
                                               'Using an e-wallet enhances my effectiveness in carrying out daily '
                                               'tasks',
                                               'Using an e-wallet makes it easier for me to complete my daily tasks '
                                               'and processes',
                                               'Overall, I find using an e-wallet beneficial'],
             'lie_2026_perceived_ease_of_use': ['Learning to use an e-wallet would be easy for me',
                                                'My interactions with an e-wallet would be clear and easy to '
                                                'understand',
                                                'I would find it easy to become skilled at using an e-wallet',
                                                'I would find an e-wallet flexible and easy to interact with',
                                                'Overall, I find an e-wallet easy to use'],
             'lie_2026_perceived_risk': ['There is a risk of losing money or making unintended purchases when using '
                                         'an e-wallet',
                                         'I am concerned about the reliability and security of the technology behind '
                                         'e-wallets',
                                         'Using an e-wallet may lead to errors or mistakes that negatively impact my '
                                         'finances',
                                         'Using an e-wallet puts my personal information at risk of leakage or '
                                         'unauthorized access',
                                         'I am concerned that network vulnerabilities may cause my e-wallet '
                                         'transactions to fail or be disrupted'],
             'lie_2026_intention_to_use': ['I intend to use an e-wallet in the future',
                                           'If I have access to an e-wallet, I intend to use it',
                                           'I intend to use an e-wallet regularly for my daily needs',
                                           'It is worth to use e-wallet',
                                           'I will frequently use an e-wallet in the future',
                                           'I believe it is worthwhile to use an e-wallet']},
  'covs': {'Gender': 'cov_gender', 'Age': 'cov_age_group', 'Monthly Expenses': 'cov_monthly_expenses'},
  'cov_maps': {'cov_gender': {'Male': 'male', 'Female': 'female'},
               'cov_age_group': {'<20': '<20',
                                 '20 - 25': '20-25',
                                 '26 -  30': '26-30',
                                 '30 - 35': '30-35',
                                 '35 - 40': '35-40',
                                 '> 40': '>40'}},
  'not_shipped': {'Timestamp': 'form timestamp', 'Domicile': 'city of residence (geographic code rule)'},
  'label': 'lie_2026_ewallet_intention',
  'item_names': {'Using an e-wallet helps me complete my daily routines more quickly': 'pu1',
                 'Using an e-wallet improves my performance in daily life activities': 'pu2',
                 'Using an e-wallet increases my overall productivity': 'pu3',
                 'Using an e-wallet enhances my effectiveness in carrying out daily tasks': 'pu4',
                 'Using an e-wallet makes it easier for me to complete my daily tasks and processes': 'pu5',
                 'Overall, I find using an e-wallet beneficial': 'pu6',
                 'Learning to use an e-wallet would be easy for me': 'peou1',
                 'My interactions with an e-wallet would be clear and easy to understand': 'peou2',
                 'I would find it easy to become skilled at using an e-wallet': 'peou3',
                 'I would find an e-wallet flexible and easy to interact with': 'peou4',
                 'Overall, I find an e-wallet easy to use': 'peou5',
                 'There is a risk of losing money or making unintended purchases when using an e-wallet': 'pr1',
                 'I am concerned about the reliability and security of the technology behind e-wallets': 'pr2',
                 'Using an e-wallet may lead to errors or mistakes that negatively impact my finances': 'pr3',
                 'Using an e-wallet puts my personal information at risk of leakage or unauthorized access': 'pr4',
                 'I am concerned that network vulnerabilities may cause my e-wallet transactions to fail or be disrupted': 'pr5',
                 'I intend to use an e-wallet in the future': 'int1',
                 'If I have access to an e-wallet, I intend to use it': 'int2',
                 'I intend to use an e-wallet regularly for my daily needs': 'int3',
                 'It is worth to use e-wallet': 'int4',
                 'I will frequently use an e-wallet in the future': 'int5',
                 'I believe it is worthwhile to use an e-wallet': 'int6'}}]

# rows written per table (asserted)
EXPECT = {'lie_2026_intention_to_use': 1140,
 'lie_2026_perceived_ease_of_use': 950,
 'lie_2026_perceived_risk': 950,
 'lie_2026_perceived_usefulness': 1140}


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
