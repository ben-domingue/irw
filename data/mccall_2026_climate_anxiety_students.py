#!/usr/bin/env python3
# Source: https://springernature.figshare.com/articles/dataset/Additional_file_1_of_Determinants_of_climate_anxiety_and_willingness_for_climate-friendly_behavioral_change_in_German_students_a_quantitative_study/31976897
# DOI: 10.6084/m9.figshare.31976897.v1 (data)
#   Timothy Mc Call; Gloria Düllberg; Michel Rinderhagen; Jonas Rickermann; Laura Niediek; Kristin Liebner; Maria
#     Leidinger; Carlotta Louisa Westfeld; Jan Kössendrup; Anna Lisa Schmid (2026). Additional file 1 of
#     Determinants of climate anxiety and willingness for climate-friendly behavioral change in German students: a
#     quantitative study [Dataset]. figshare.
# License: CC BY 4.0 (Springer Nature figshare, additional file 1)
# Data: 528 students at German universities (2024): a 10-item anxiety short scale (1-8), BFI-10 (1-5), Connectedness
#   to Nature (14 items, 1-7; the single-item Inclusion of Nature in Self is not shipped), willingness for six
#   climate-friendly behaviours (1-5) and the 13-item Climate Anxiety Scale (1-7).
# Tables: item = the SPSS name.
# Covariates: cov_age_group (9 = 'I don't want to brag' and 99 -> missing), cov_gender, cov_data_source (M/O)
# PII: none found (string columns screened)
# Item text: available -- SPSS variable labels carry the English statements (BFI-10, CNS and CAS are published
#   instruments: register rows needed)
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

SOURCES = [{'url': 'https://ndownloader.figshare.com/files/63607580',
  'kind': 'sav',
  'read_kw': {},
  'n_rows': 528,
  'range': (1, 7),
  'blocks': {'mccall_2026_anxiety': ['AE1', 'AE2', 'AE3', 'AE4', 'AE5', 'AE6', 'AE7', 'AE8', 'AE9', 'AE10'],
             'mccall_2026_bfi10': ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10'],
             'mccall_2026_connectedness_to_nature': ['NV2',
                                                     'NV3',
                                                     'NV4',
                                                     'NV5',
                                                     'NV6',
                                                     'NV7',
                                                     'NV8',
                                                     'NV9',
                                                     'NV10',
                                                     'NV11',
                                                     'NV12',
                                                     'NV13',
                                                     'NV14',
                                                     'NV15'],
             'mccall_2026_climate_behav_willingness': ['KG6', 'KG7', 'KG8', 'KG9', 'KG10', 'KG11'],
             'mccall_2026_climate_anxiety': ['KA1',
                                             'KA2',
                                             'KA3',
                                             'KA4',
                                             'KA5',
                                             'KA6',
                                             'KA7',
                                             'KA8',
                                             'KA9',
                                             'KA10',
                                             'KA11',
                                             'KA12',
                                             'KA13']},
  'covs': {'Age': 'cov_age_group', 'Gender': 'cov_gender', 'DatensatzUrsprung': 'cov_data_source'},
  'cov_maps': {'cov_age_group': {1.0: '18-20',
                                 2.0: '21-25',
                                 3.0: '26-30',
                                 4.0: '31-35',
                                 5.0: '36-40',
                                 6.0: '41-45',
                                 7.0: '46-50',
                                 8.0: '>50',
                                 9.0: None,
                                 99.0: None},
               'cov_gender': {1.0: 'female', 2.0: 'male', 3.0: 'diverse'}},
  'not_shipped': {'Consent': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                             'comment or timestamp',
                  'GermanU': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                             'comment or timestamp',
                  'NV1_INS': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                             'comment or timestamp',
                  'KG1.1': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                           'comment or timestamp',
                  'KG1.2': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                           'comment or timestamp',
                  'KG1.3': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                           'comment or timestamp',
                  'KG1.4': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                           'comment or timestamp',
                  'KG1.5': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                           'comment or timestamp',
                  'KG1.6': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                           'comment or timestamp',
                  'KG1.7': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                           'comment or timestamp',
                  'KG1.8': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                           'comment or timestamp',
                  'KG1.9': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                           'comment or timestamp',
                  'KG1.10': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                            'comment or timestamp',
                  'KG2': 'not carried: screener, single question, multi-select checklist, recode, composite, comment '
                         'or timestamp',
                  'KG3': 'not carried: screener, single question, multi-select checklist, recode, composite, comment '
                         'or timestamp',
                  'KG4': 'not carried: screener, single question, multi-select checklist, recode, composite, comment '
                         'or timestamp',
                  'KG5': 'not carried: screener, single question, multi-select checklist, recode, composite, comment '
                         'or timestamp',
                  'KG12': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'KG13': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'KG14': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'KG15': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'KG16': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'KG17': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'KG18.1': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                            'comment or timestamp',
                  'KG18.2': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                            'comment or timestamp',
                  'KG18.3': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                            'comment or timestamp',
                  'KG18.4': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                            'comment or timestamp',
                  'KG18.5': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                            'comment or timestamp',
                  'KG18.6': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                            'comment or timestamp',
                  'KG18.7': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                            'comment or timestamp',
                  'KG18.8': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                            'comment or timestamp',
                  'KG18.9': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                            'comment or timestamp',
                  'ANM': 'free-text comment (not carried)',
                  'Zeitstempel': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                                 'comment or timestamp',
                  'A3_1': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'A3_2': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'A3_3': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'AE': 'not carried: screener, single question, multi-select checklist, recode, composite, comment '
                        'or timestamp',
                  'P_EX': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'P_AG': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'P_CO': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'P_NE': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'P_OP': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                          'comment or timestamp',
                  'CTN': 'not carried: screener, single question, multi-select checklist, recode, composite, comment '
                         'or timestamp',
                  'KA': 'not carried: screener, single question, multi-select checklist, recode, composite, comment '
                        'or timestamp',
                  'KG_BV': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                           'comment or timestamp',
                  'KG_HK': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                           'comment or timestamp',
                  'KG_GF': 'not carried: screener, single question, multi-select checklist, recode, composite, '
                           'comment or timestamp'},
  'label': 'mccall_2026_climate_anxiety_students',
  'ranges': {'mccall_2026_anxiety': (1, 8),
             'mccall_2026_bfi10': (1, 5),
             'mccall_2026_climate_behav_willingness': (1, 5)},
  'id_col': 'Nr'}]

# rows written per table (asserted)
EXPECT = {'mccall_2026_anxiety': 5274,
 'mccall_2026_bfi10': 5269,
 'mccall_2026_climate_anxiety': 6840,
 'mccall_2026_climate_behav_willingness': 3163,
 'mccall_2026_connectedness_to_nature': 7345}


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
