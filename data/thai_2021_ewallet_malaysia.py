#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.15167982.v1
# DOI: 10.6084/m9.figshare.15167982.v1 (data)
#   Thai Siew Bee (2021). Database For E-Wallet Adoption in Malaysia [Dataset]. figshare.
# License: CC0 (figshare record)
# Data: 100 Malaysian e-wallet users, 1-5 items.
# Tables: one per construct (header prefix); items peou1.. by the statement number in the bracket.
# Covariates: none carried
# PII: none found (string columns screened)
# Item text: available -- the bracketed statements in the headers
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

SOURCES = [{'url': 'https://ndownloader.figshare.com/files/29139081',
  'kind': 'excel',
  'read_kw': {},
  'n_rows': 100,
  'range': (1, 5),
  'blocks': {'thai_2021_perceived_ease_of_use': ['1. Perceived Ease of Use [1. The use of E-wallet is clear and '
                                                 'understandable.]',
                                                 "1. Perceived Ease of Use [2. Using E-wallet isn't mentally "
                                                 'challenging.]',
                                                 '1. Perceived Ease of Use [3. It is easy for me to learn how to use '
                                                 'E-wallet.]',
                                                 '1. Perceived Ease of Use [4. It is easy for me to remember the '
                                                 'steps to use E-wallet.]',
                                                 '1. Perceived Ease of Use [5. The operation interface of E-wallet '
                                                 'is friendly and understandable]'],
             'thai_2021_perceived_usefulness': ['2. Perceived Usefulness [1. Using E-wallet makes me save time.]',
                                                '2. Perceived Usefulness [2. Using E-wallet makes it easier for me '
                                                'to conduct transactions.]',
                                                '2. Perceived Usefulness [3. E-wallet is a useful paying method.]',
                                                '2. Perceived Usefulness [4. Overall, I find E-wallet useful in my '
                                                'life.]'],
             'thai_2021_perceived_risk': ['3. Perceived Risk [1. E-wallets ensure protection against risk of fraud '
                                          'and financial loss.]',
                                          '3. Perceived Risk [2. I am not worried that information transferred by '
                                          'using E-wallet may be intercepted by other people.]',
                                          '3. Perceived Risk [3. The risk of abuse of usage information (e.g., names '
                                          'of business partners, payment amount) is low when using E-wallet.]',
                                          '3. Perceived Risk [4. I think that privacy is guaranteed when using '
                                          'E-wallet.]',
                                          '3. Perceived Risk [5. I am not afraid that the confidentiality of my '
                                          'financial transactions might get lost when using E-wallet.]'],
             'thai_2021_social_influence': ['4. Social Influence [1. I will use E-wallet if the service is widely '
                                            'used by people in my community.]',
                                            '4. Social Influence [2. I will use E-wallet if people who are important '
                                            'to me are likely to recommend me to use E-wallet.]',
                                            '4. Social Influence [3. I will use E-wallet if people who are important '
                                            'to me expect me to use E-wallet.]',
                                            '4. Social Influence [4. I will use E-wallet if people who influence my '
                                            'behavior think that I should use E-wallet.]'],
             'thai_2021_government_support': ['5. Government Support [1. I believe the government has introduced '
                                              'favorable legislation and regulations for E-wallet services.]',
                                              '5. Government Support [2. I believe the government is active in '
                                              'setting up all kinds of infrastructure such as the infrastructure '
                                              'telecom network, which has a positive role in promoting E-wallet '
                                              'services.]',
                                              '5. Government Support [3. I believe the government supports and '
                                              'improves the use of E-wallet services.]',
                                              '5. Government Support [4. I will use E-wallet if the government '
                                              'ensures e-wallets server facilities.]']},
  'covs': {},
  'cov_maps': {},
  'not_shipped': {'1. Gender': 'coded demographic without a key in the deposit',
                  '2. Age': 'coded demographic without a key in the deposit',
                  '3. Race': 'coded demographic without a key in the deposit',
                  '4. Education Level': 'coded demographic without a key in the deposit',
                  '5. Employment': 'coded demographic without a key in the deposit',
                  '6. Income Level': 'coded demographic without a key in the deposit',
                  '7. E-wallet service usage In a month': 'coded demographic without a key in the deposit'},
  'label': 'thai_2021_ewallet_malaysia',
  'item_names': {'1. Perceived Ease of Use [1. The use of E-wallet is clear and understandable.]': 'peou1',
                 "1. Perceived Ease of Use [2. Using E-wallet isn't mentally challenging.]": 'peou2',
                 '1. Perceived Ease of Use [3. It is easy for me to learn how to use E-wallet.]': 'peou3',
                 '1. Perceived Ease of Use [4. It is easy for me to remember the steps to use E-wallet.]': 'peou4',
                 '1. Perceived Ease of Use [5. The operation interface of E-wallet is friendly and understandable]': 'peou5',
                 '2. Perceived Usefulness [1. Using E-wallet makes me save time.]': 'pu1',
                 '2. Perceived Usefulness [2. Using E-wallet makes it easier for me to conduct transactions.]': 'pu2',
                 '2. Perceived Usefulness [3. E-wallet is a useful paying method.]': 'pu3',
                 '2. Perceived Usefulness [4. Overall, I find E-wallet useful in my life.]': 'pu4',
                 '3. Perceived Risk [1. E-wallets ensure protection against risk of fraud and financial loss.]': 'pr1',
                 '3. Perceived Risk [2. I am not worried that information transferred by using E-wallet may be intercepted by other people.]': 'pr2',
                 '3. Perceived Risk [3. The risk of abuse of usage information (e.g., names of business partners, payment amount) is low when using E-wallet.]': 'pr3',
                 '3. Perceived Risk [4. I think that privacy is guaranteed when using E-wallet.]': 'pr4',
                 '3. Perceived Risk [5. I am not afraid that the confidentiality of my financial transactions might get lost when using E-wallet.]': 'pr5',
                 '4. Social Influence [1. I will use E-wallet if the service is widely used by people in my community.]': 'si1',
                 '4. Social Influence [2. I will use E-wallet if people who are important to me are likely to recommend me to use E-wallet.]': 'si2',
                 '4. Social Influence [3. I will use E-wallet if people who are important to me expect me to use E-wallet.]': 'si3',
                 '4. Social Influence [4. I will use E-wallet if people who influence my behavior think that I should use E-wallet.]': 'si4',
                 '5. Government Support [1. I believe the government has introduced favorable legislation and regulations for E-wallet services.]': 'gs1',
                 '5. Government Support [2. I believe the government is active in setting up all kinds of infrastructure such as the infrastructure telecom network, which has a positive role in promoting E-wallet services.]': 'gs2',
                 '5. Government Support [3. I believe the government supports and improves the use of E-wallet services.]': 'gs3',
                 '5. Government Support [4. I will use E-wallet if the government ensures e-wallets server facilities.]': 'gs4'}}]

# rows written per table (asserted)
EXPECT = {'thai_2021_government_support': 400,
 'thai_2021_perceived_ease_of_use': 500,
 'thai_2021_perceived_risk': 500,
 'thai_2021_perceived_usefulness': 400,
 'thai_2021_social_influence': 400}


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
