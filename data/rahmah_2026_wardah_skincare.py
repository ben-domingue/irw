#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.33071000.v1
# DOI: 10.6084/m9.figshare.33071000.v1 (data)
#   Nurhalidza Fauziah Rahmah (2026). Data Responden Penelitian - Analisis Pengaruh Brand Experience Terhadap Brand
#     Loyalty Melalui Brand Trust dan Brand Love Studi Pada Gen Z Pengguna Produk Skincare Wardah di Jabodetabek
#     [Dataset]. figshare.
# License: CC BY 4.0 (Zenodo record)
# Data: 230 Gen Z users of Wardah skincare in Jabodetabek (Indonesia), 1-5 items, Indonesian statements.
# Tables: brand experience (11 statements), brand trust (4), brand love (4), brand loyalty (4): IRW's reading of the
#   statement headers in sheet order, matching the title's four constructs; items by position within block.
# Covariates: cov_age_group, cov_gender, cov_occupation, cov_monthly_expenses (Indonesian labels as printed)
# PII: the 'Nama' column holds names masked to an initial plus asterisks; dropped. Domisili dropped (geographic
#   rule).
# Item text: available -- the headers are the Indonesian statements
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

SOURCES = [{'url': 'https://ndownloader.figshare.com/files/66927155',
  'kind': 'excel',
  'read_kw': {},
  'n_rows': 230,
  'range': (1, 5),
  'blocks': {'rahmah_2026_brand_experience': ['Saya merasa produk skincare merek Wardah terlihat menarik',
                                              'Saya merasa produk skincare merek Wardah memiliki aroma yang enak',
                                              'Saya merasa nama merek Wardah mudah diingat dan terdengar baik',
                                              'Saya merasa tekstur produk skincare merek Wardah nyaman di kulit',
                                              'Saya merasa senang dengan merek skincare Wardah',
                                              'Saya merasa lebih nyaman saat menggunakan produk skincare merek '
                                              'Wardah',
                                              'Saya terbiasa memakai produk skincare merek Wardah dalam perawatan '
                                              'kulit saya',
                                              'Saya merasa skincare merek Wardah memengaruhi cara saya merawat kulit',
                                              'Saya merasa skincare merek Wardah cocok dengan gaya hidup saya',
                                              'Saya ingin tahu lebih banyak tentang produk skincare merek Wardah',
                                              'Saya menjadi lebih teliti saat memilih produk skincare karena Wardah'],
             'rahmah_2026_brand_trust': ['Saya percaya pada produk skincare merek Wardah',
                                         'Saya merasa Wardah merupakan merek skincare yang dapat diandalkan',
                                         'Saya merasa Wardah merupakan merek skincare yang jujur',
                                         'Saya merasa aman ketika menggunakan produk skincare merek Wardah'],
             'rahmah_2026_brand_love': ['Saya memiliki kesan positif terhadap merek skincare Wardah',
                                        'Saya merasa ada kedekatan emosional dengan Wardah',
                                        'Saya sangat menyukai skincare merek Wardah dibanding beberapa merek '
                                        'skincare lain.',
                                        'Saya lebih tertarik pada skincare merek Wardah dibanding dengan merek '
                                        'skincare lain'],
             'rahmah_2026_brand_loyalty': ['Saya akan membeli kembali produk skincare merek Wardah',
                                           'Merek Wardah akan menjadi pilihan utama saya ketika membeli produk '
                                           'skincare',
                                           'Saya bersedia merekomendasikan produk skincare merek Wardah kepada orang '
                                           'lain',
                                           'Saya menceritakan hal-hal positif tentang skincare merek Wardah kepada '
                                           'orang lain.']},
  'covs': {'Usia': 'cov_age_group',
           'Jenis Kelamin': 'cov_gender',
           'Profesi': 'cov_occupation',
           'Pengeluaran Perbulan': 'cov_monthly_expenses'},
  'cov_maps': {'cov_gender': {'Laki-laki': 'male', 'Perempuan': 'female'}},
  'not_shipped': {'Apakah usia Anda termasuk kategori Generasi Z (Individu kelahiran 1997-2012 atau berusia 14-29 tahun) ?': 'screener '
                                                                                                                             '(all '
                                                                                                                             'yes)',
                  'Apakah anda pernah melakukan pembelian produk skincare merek Wardah minimal 2 kali dalam waktu dekat?': 'screener '
                                                                                                                           '(all '
                                                                                                                           'yes)',
                  'Nama': "masked name field ('R*****'): dropped in any form",
                  'Domisili': 'city of residence (geographic code rule)',
                  'Jenis produk skincare Wardah yang digunakan / pernah dibeli?': 'product type bought '
                                                                                  '(multi-category)',
                  'Dimana anda membeli produk skincare Wardah tersebut?': 'purchase channel'},
  'label': 'rahmah_2026_wardah_skincare',
  'item_names': {'Saya merasa produk skincare merek Wardah terlihat menarik': 'bx1',
                 'Saya merasa produk skincare merek Wardah memiliki aroma yang enak': 'bx2',
                 'Saya merasa nama merek Wardah mudah diingat dan terdengar baik': 'bx3',
                 'Saya merasa tekstur produk skincare merek Wardah nyaman di kulit': 'bx4',
                 'Saya merasa senang dengan merek skincare Wardah': 'bx5',
                 'Saya merasa lebih nyaman saat menggunakan produk skincare merek Wardah': 'bx6',
                 'Saya terbiasa memakai produk skincare merek Wardah dalam perawatan kulit saya': 'bx7',
                 'Saya merasa skincare merek Wardah memengaruhi cara saya merawat kulit': 'bx8',
                 'Saya merasa skincare merek Wardah cocok dengan gaya hidup saya': 'bx9',
                 'Saya ingin tahu lebih banyak tentang produk skincare merek Wardah': 'bx10',
                 'Saya menjadi lebih teliti saat memilih produk skincare karena Wardah': 'bx11',
                 'Saya percaya pada produk skincare merek Wardah': 'bt1',
                 'Saya merasa Wardah merupakan merek skincare yang dapat diandalkan': 'bt2',
                 'Saya merasa Wardah merupakan merek skincare yang jujur': 'bt3',
                 'Saya merasa aman ketika menggunakan produk skincare merek Wardah': 'bt4',
                 'Saya memiliki kesan positif terhadap merek skincare Wardah': 'bl1',
                 'Saya merasa ada kedekatan emosional dengan Wardah': 'bl2',
                 'Saya sangat menyukai skincare merek Wardah dibanding beberapa merek skincare lain.': 'bl3',
                 'Saya lebih tertarik pada skincare merek Wardah dibanding dengan merek skincare lain': 'bl4',
                 'Saya akan membeli kembali produk skincare merek Wardah': 'loy1',
                 'Merek Wardah akan menjadi pilihan utama saya ketika membeli produk skincare': 'loy2',
                 'Saya bersedia merekomendasikan produk skincare merek Wardah kepada orang lain': 'loy3',
                 'Saya menceritakan hal-hal positif tentang skincare merek Wardah kepada orang lain.': 'loy4'}}]

# rows written per table (asserted)
EXPECT = {'rahmah_2026_brand_experience': 2530,
 'rahmah_2026_brand_love': 920,
 'rahmah_2026_brand_loyalty': 920,
 'rahmah_2026_brand_trust': 920}


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
