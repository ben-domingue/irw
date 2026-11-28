#!/usr/bin/env python3
# Source: https://zenodo.org/records/22677
# DOI: 10.5281/zenodo.22677 (data)
#   Valera-Gálvez, Jorge Luis (2015). Percepción de la comunidad sobre la calidad del servicio de una institución
#     educativa de Ventanilla - Callao - Padres [Dataset]. Zenodo.
# License: CC0 1.0 (Zenodo record)
# Data: 165 parents at a public school in Ventanilla, Callao (Peru), 51 Spanish 1-5 items on four dimensions of the
#   school's service quality (Valera-Gálvez thesis, 2012). One Item7 cell (6) and one Item43 cell (33) lie outside
#   1-5, each isolated to its item: data-entry errors, set missing.
# Tables: one per dimension, per the deposit's own Suma_* columns (organisation/institutional items 1-12,
#   administrative 13-25, pedagogical 26-41, community 42-51); item = the SPSS name.
# Covariates: cov_education (code: 1 primaria, 2 secundaria, 3 superior), cov_age, cov_gender
# PII: none found (string columns screened)
# Item text: available -- SPSS variable labels carry the Spanish statements
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

SOURCES = [{'url': 'https://zenodo.org/api/records/22677/files/2012_Valera_Percepcion_de_la_comunidad_sobre_la_calidad_del_servicio_de_una_institucion_educativa_de_Ventanilla_-_Callao_-_padres.sav/content',
  'kind': 'sav',
  'read_kw': {},
  'n_rows': 165,
  'range': (1, 5),
  'blocks': {'valera_2012_parents_institutional': ['Item1',
                                                   'Item2',
                                                   'Item3',
                                                   'Item4',
                                                   'Item5',
                                                   'Item6',
                                                   'Item7',
                                                   'Item8',
                                                   'Item9',
                                                   'Item10',
                                                   'Item11',
                                                   'Item12'],
             'valera_2012_parents_administrative': ['Item13',
                                                    'Item14',
                                                    'Item15',
                                                    'Item16',
                                                    'Item17',
                                                    'Item18',
                                                    'Item19',
                                                    'Item20',
                                                    'Item21',
                                                    'Item22',
                                                    'Item23',
                                                    'Item24',
                                                    'Item25'],
             'valera_2012_parents_pedagogical': ['Item26',
                                                 'Item27',
                                                 'Item28',
                                                 'Item29',
                                                 'Item30',
                                                 'Item31',
                                                 'Item32',
                                                 'Item33',
                                                 'Item34',
                                                 'Item35',
                                                 'Item36',
                                                 'Item37',
                                                 'Item38',
                                                 'Item39',
                                                 'Item40',
                                                 'Item41'],
             'valera_2012_parents_community': ['Item42',
                                               'Item43',
                                               'Item44',
                                               'Item45',
                                               'Item46',
                                               'Item47',
                                               'Item48',
                                               'Item49',
                                               'Item50',
                                               'Item51']},
  'covs': {'Grado': 'cov_education', 'Edad': 'cov_age', 'Genero': 'cov_gender'},
  'cov_maps': {'cov_gender': {'F': 'female', 'M': 'male'}},
  'not_shipped': {'Suma_org': 'sum or level score (derived)',
                  'Suma_admin': 'sum or level score (derived)',
                  'Suma_pedag': 'sum or level score (derived)',
                  'Suma_com': 'sum or level score (derived)',
                  'Calidad': 'sum or level score (derived)',
                  'Calidad1': 'sum or level score (derived)',
                  'Institucional': 'sum or level score (derived)',
                  'Administrativa1': 'sum or level score (derived)',
                  'Pedagógica1': 'sum or level score (derived)',
                  'Comunitaria1': 'sum or level score (derived)'},
  'label': 'valera_2012_service_quality_parents',
  'item_names': {'Item1': 'Item1',
                 'Item2': 'Item2',
                 'Item3': 'Item3',
                 'Item4': 'Item4',
                 'Item5': 'Item5',
                 'Item6': 'Item6',
                 'Item7': 'Item7',
                 'Item8': 'Item8',
                 'Item9': 'Item9',
                 'Item10': 'Item10',
                 'Item11': 'Item11',
                 'Item12': 'Item12',
                 'Item13': 'Item13',
                 'Item14': 'Item14',
                 'Item15': 'Item15',
                 'Item16': 'Item16',
                 'Item17': 'Item17',
                 'Item18': 'Item18',
                 'Item19': 'Item19',
                 'Item20': 'Item20',
                 'Item21': 'Item21',
                 'Item22': 'Item22',
                 'Item23': 'Item23',
                 'Item24': 'Item24',
                 'Item25': 'Item25',
                 'Item26': 'Item26',
                 'Item27': 'Item27',
                 'Item28': 'Item28',
                 'Item29': 'Item29',
                 'Item30': 'Item30',
                 'Item31': 'Item31',
                 'Item32': 'Item32',
                 'Item33': 'Item33',
                 'Item34': 'Item34',
                 'Item35': 'Item35',
                 'Item36': 'Item36',
                 'Item37': 'Item37',
                 'Item38': 'Item38',
                 'Item39': 'Item39',
                 'Item40': 'Item40',
                 'Item41': 'Item41',
                 'Item42': 'Item42',
                 'Item43': 'Item43',
                 'Item44': 'Item44',
                 'Item45': 'Item45',
                 'Item46': 'Item46',
                 'Item47': 'Item47',
                 'Item48': 'Item48',
                 'Item49': 'Item49',
                 'Item50': 'Item50',
                 'Item51': 'Item51'},
  'invalid': {'Item7': [6], 'Item43': [33]}}]

# rows written per table (asserted)
EXPECT = {'valera_2012_parents_administrative': 2145,
 'valera_2012_parents_community': 1649,
 'valera_2012_parents_institutional': 1979,
 'valera_2012_parents_pedagogical': 2640}


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
