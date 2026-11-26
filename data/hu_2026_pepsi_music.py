#!/usr/bin/env python3
# Source: https://zenodo.org/records/18539604
# DOI: 10.5281/zenodo.18539604 (data)
#   Hu, Hui-Ling (2026). How Musical Emotional Expressiveness and Brand–Music Congruence Shape Brand Loyalty: The
#     Mediating Roles of Emotional Attachment and Brand Attitude
# License: CC BY 4.0 (repository record)
# Data: 601 Chinese respondents rating a Pepsi music advert (Wenjuanxing export). Each header is the code plus the
#   Chinese stem and its construct name, so the codes are documented in the file itself.
# Tables: one per construct, item = the deposit code.
# Covariates: none carried
# PII: none found (string columns screened)
# Item text: not shipped -- the Chinese stems are the column headers, but the seven anchors are not in the
#   deposit; register row needed.
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

SOURCES = [{'url': 'https://zenodo.org/api/records/18539604/files/%E9%9F%B3%E4%B9%90%E8%90%A5%E9%94%80.xlsx/content',
  'kind': 'excel',
  'read_kw': {},
  'n_rows': 601,
  'range': (1, 7),
  'blocks': {'hu_2026_pepsi_music_expressiveness': ['MEE1', 'MEE2', 'MEE3', 'MEE4', 'MEE5'],
             'hu_2026_pepsi_brand_music_congruence': ['BMC1', 'BMC2', 'BMC3', 'BMC4', 'BMC5'],
             'hu_2026_pepsi_emotional_attachment': ['EA1', 'EA2', 'EA3', 'EA4', 'EA5'],
             'hu_2026_pepsi_brand_attitude': ['BA1', 'BA2', 'BA3', 'BA4', 'BA5'],
             'hu_2026_pepsi_brand_loyalty': ['BL1', 'BL2', 'BL3', 'BL4', 'BL5']},
  'covs': {},
  'cov_maps': {},
  'not_shipped': {'答题时长': 'not carried',
                  '7.性别': 'not carried',
                  '8.年龄': 'not carried',
                  '9.教育程度': 'not carried',
                  '10.每月平均购买碳酸饮料次数': 'not carried',
                  '11.最常购买的饮料品牌': 'not carried',
                  '12.其他品牌': 'not carried'},
  'rename': {'MEE1 2.音乐情感表达力:这段百事可乐音乐让我感受到强烈的情绪': 'MEE1',
             'MEE2 2.音乐情感表达力:我觉得这段音乐充满活力与感染力': 'MEE2',
             'MEE3 2.音乐情感表达力:聆听这段音乐时，我感受到快乐与兴奋的情绪': 'MEE3',
             'MEE4 2.音乐情感表达力:这段音乐的旋律和节奏能引起我的情感共鸣': 'MEE4',
             'MEE5 2.音乐情感表达力:我能明显感受到这段音乐所想传达的情感氛围': 'MEE5',
             'BMC1 3.品牌–音乐契合度:这段音乐与百事可乐的品牌形象非常一致': 'BMC1',
             'BMC2 3.品牌–音乐契合度:音乐所表达的风格与百事可乐品牌的年轻特质相符': 'BMC2',
             'BMC3 3.品牌–音乐契合度:我觉得这段音乐成功地表现出百事可乐的活力': 'BMC3',
             'BMC4 3.品牌–音乐契合度:音乐与百事可乐的广告内容彼此搭配得很好': 'BMC4',
             'BMC5 3.品牌–音乐契合度:听完这段音乐，我觉得它与百事可乐的品牌形象十分契合': 'BMC5',
             'EA1 4.情感依附:我对百事可乐有深厚的情感连结': 'EA1',
             'EA2 4.情感依附:百事可乐对我而言不只是饮料品牌，更是一种情感象征': 'EA2',
             'EA3 4.情感依附:当我看到百事可乐时，会有熟悉或亲切的感觉': 'EA3',
             'EA4 4.情感依附:我在情感上依附于百事可乐这个品牌': 'EA4',
             'EA5 4.情感依附:若百事可乐消失，我会感到失落': 'EA5',
             'BA1 5.品牌态度:我对百事可乐的整体印象是正面的': 'BA1',
             'BA2 5.品牌态度:我喜欢百事可乐这个品牌': 'BA2',
             'BA3 5.品牌态度:我觉得百事可乐是一个值得信赖的品牌': 'BA3',
             'BA4 5.品牌态度:我对百事可乐的品牌感受良好': 'BA4',
             'BA5 5.品牌态度:百事可乐的品牌形象让我感到愉悦': 'BA5',
             'BL1 6.品牌忠诚度:我愿意在未来继续购买百事可乐的产品': 'BL1',
             'BL2 6.品牌忠诚度:即使有其他品牌的替代品，我仍会选择百事可乐': 'BL2',
             'BL3 6.品牌忠诚度:我会向他人推荐百事可乐': 'BL3',
             'BL4 6.品牌忠诚度:我对百事可乐的忠诚度很高': 'BL4',
             'BL5 6.品牌忠诚度:百事可乐是我最信任的饮料品牌之一': 'BL5'},
  'label': 'hu_2026_pepsi_music'}]


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
