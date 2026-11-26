#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_b_How_Empowering_Leadership_Stimulates_Physical_Education_Teachers_Innovative_Work_Behavior_A_Cross-Level_Chain_Mediation_Model_Based_on_Psychological_Empowerment_and_Self-Efficacy_b_/31018120
# DOI: 10.6084/m9.figshare.31018120.v1 (data)
#   Suxuan Xing (2026). <b>How Empowering Leadership Stimulates Physical Education Teachers’ Innovative Work
#     Behavior: A Cross-Level Chain Mediation Model Based on Psychological Empowerment and Self-Efficacy</b>
# License: CC BY 4.0 (repository record)
# Data: 504 Chinese PE teachers nested in 29 schools. Column headers name each subscale (psychological
#   empowerment: meaning, autonomy, self-efficacy, impact, 1-5; teaching efficacy: strategies, classroom management,
#   engagement, 1-9; innovative work behaviour: idea generation, communication, implementation, 1-7). The leaders'
#   empowering-leadership ratings are school-level and repeat across teacher rows, so they are not shipped.
# Tables: one per instrument (subscales pooled); item = subscale code + position (WM meaning, AUT autonomy, SE
#   self-efficacy, WI impact; TSE strategies, CME classroom management, SEE student engagement; IG idea generation,
#   CC creative communication, CI creative implementation).
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

SOURCES = [{'url': 'https://ndownloader.figshare.com/files/60856027',
  'kind': 'excel',
  'read_kw': {},
  'n_rows': 504,
  'range': (1, 5),
  'blocks': {'xing_2026_pe_teacher_psych_empowerment': ['WM1',
                                                        'WM2',
                                                        'WM3',
                                                        'AUT1',
                                                        'AUT2',
                                                        'AUT3',
                                                        'SE1',
                                                        'SE2',
                                                        'SE3',
                                                        'WI1',
                                                        'WI2',
                                                        'WI3'],
             'xing_2026_pe_teacher_teaching_efficacy': ['TSE1',
                                                        'TSE2',
                                                        'TSE3',
                                                        'TSE4',
                                                        'CME1',
                                                        'CME2',
                                                        'CME3',
                                                        'CME4',
                                                        'SEE1',
                                                        'SEE2',
                                                        'SEE3',
                                                        'SEE4'],
             'xing_2026_pe_teacher_innovative_work': ['IG1', 'IG2', 'IG3', 'CC1', 'CC2', 'CC3', 'CI1', 'CI2', 'CI3']},
  'covs': {},
  'cov_maps': {},
  'not_shipped': {'Teacher _ School name': 'school label (School01...), not carried',
                  'Teacher _ Gender': 'unkeyed code',
                  'Teacher _ Age': 'not carried',
                  'Teacher _ Educational Background': 'unkeyed code',
                  'Teacher _ Teaching Seniority': 'unkeyed code',
                  'Teacher _ Title': 'unkeyed code',
                  'Teacher _ Ren Teaching Section': 'unkeyed code',
                  'Teacher _ Teaching Discipline': 'unkeyed code',
                  'Teacher _ Yes No Class teacher': 'unkeyed code',
                  'Teacher _ Nature of school': 'unkeyed code',
                  'Leader _ School Name': 'school leader rating, repeated on every teacher row of the school (leader '
                                          'level), not carried',
                  'Leadership _ Gender': 'school leader rating, repeated on every teacher row of the school (leader '
                                         'level), not carried',
                  'Leadership _ Age': 'school leader rating, repeated on every teacher row of the school (leader '
                                      'level), not carried',
                  'Leadership _ Education Background': 'school leader rating, repeated on every teacher row of the '
                                                       'school (leader level), not carried',
                  'Leadership _ School Type': 'school leader rating, repeated on every teacher row of the school '
                                              '(leader level), not carried',
                  'Leadership _ School Nature': 'school leader rating, repeated on every teacher row of the school '
                                                '(leader level), not carried',
                  'Leadership _ School Size': 'school leader rating, repeated on every teacher row of the school '
                                              '(leader level), not carried',
                  'Leadership _ Personal Development Support 1': 'school leader rating, repeated on every teacher '
                                                                 'row of the school (leader level), not carried',
                  'Leadership _ Personal Development Support 2': 'school leader rating, repeated on every teacher '
                                                                 'row of the school (leader level), not carried',
                  'Leadership _ Personal Development Support 3': 'school leader rating, repeated on every teacher '
                                                                 'row of the school (leader level), not carried',
                  'Leadership _ Personal Development Support 4': 'school leader rating, repeated on every teacher '
                                                                 'row of the school (leader level), not carried',
                  'Leadership _ Personal Development Support 5': 'school leader rating, repeated on every teacher '
                                                                 'row of the school (leader level), not carried',
                  'Leadership _ Personal Development Support 6': 'school leader rating, repeated on every teacher '
                                                                 'row of the school (leader level), not carried',
                  'Leader _ Process Control 1': 'school leader rating, repeated on every teacher row of the school '
                                                '(leader level), not carried',
                  'Leadership _ Process Control 2': 'school leader rating, repeated on every teacher row of the '
                                                    'school (leader level), not carried',
                  'Leadership _ Process Control 3': 'school leader rating, repeated on every teacher row of the '
                                                    'school (leader level), not carried',
                  'Leadership _ Process Control 4': 'school leader rating, repeated on every teacher row of the '
                                                    'school (leader level), not carried',
                  'Leadership _ Authority Appointment 1': 'school leader rating, repeated on every teacher row of '
                                                          'the school (leader level), not carried',
                  'Leadership _ Authority Appointment 2': 'school leader rating, repeated on every teacher row of '
                                                          'the school (leader level), not carried',
                  'Leadership _ Authority Appointment 3': 'school leader rating, repeated on every teacher row of '
                                                          'the school (leader level), not carried',
                  'Leadership _ Results and Objectives Control 1': 'school leader rating, repeated on every teacher '
                                                                   'row of the school (leader level), not carried',
                  'Leadership _ Results and Objectives Control 2': 'school leader rating, repeated on every teacher '
                                                                   'row of the school (leader level), not carried',
                  'Leadership _ Results and Objectives Control 3': 'school leader rating, repeated on every teacher '
                                                                   'row of the school (leader level), not carried',
                  'Leadership _ Results and Objectives Control 4': 'school leader rating, repeated on every teacher '
                                                                   'row of the school (leader level), not carried',
                  'Leadership _ Participation in Decision Making 1': 'school leader rating, repeated on every '
                                                                     'teacher row of the school (leader level), not '
                                                                     'carried',
                  'Leadership _ Participation in Decision Making 2': 'school leader rating, repeated on every '
                                                                     'teacher row of the school (leader level), not '
                                                                     'carried',
                  'Leadership _ Participation in Decision Making 3': 'school leader rating, repeated on every '
                                                                     'teacher row of the school (leader level), not '
                                                                     'carried',
                  'Leadership _ Participation in Decision Making 4': 'school leader rating, repeated on every '
                                                                     'teacher row of the school (leader level), not '
                                                                     'carried',
                  'Leadership _ Work Guidance 1': 'school leader rating, repeated on every teacher row of the school '
                                                  '(leader level), not carried',
                  'Leadership _ Work Guidance 2': 'school leader rating, repeated on every teacher row of the school '
                                                  '(leader level), not carried',
                  'Leadership _ Work guidance 3': 'school leader rating, repeated on every teacher row of the school '
                                                  '(leader level), not carried'},
  'rename': {'Teacher _ Work Meaning 1': 'WM1',
             'Teacher _ Work Meaning 2': 'WM2',
             'Teacher _ Work Meaning 3': 'WM3',
             'Teacher _ Autonomy 1': 'AUT1',
             'Teacher _ Autonomy 2': 'AUT2',
             'Teacher _ Autonomy 3': 'AUT3',
             'Teacher _ Self-Efficacy 1': 'SE1',
             'Teacher _ Self-Efficacy 2': 'SE2',
             'Teacher _ Self-Efficacy 3': 'SE3',
             'Teacher _ Work Impact 1': 'WI1',
             'Teacher _ Work Impact 2': 'WI2',
             'Teacher _ Work Impact 3': 'WI3',
             'Teacher _ Teaching Strategy Effectiveness 1': 'TSE1',
             'Teacher _ Teaching Strategy Effectiveness 2': 'TSE2',
             'Teacher _ Teaching Strategy Effectiveness 3': 'TSE3',
             'Teacher _ Teaching Strategy Effectiveness 4': 'TSE4',
             'Teachers _ Classroom Management Effectiveness 1': 'CME1',
             'Teachers _ Classroom Management Effectiveness 2': 'CME2',
             'Teachers _ Classroom Management Effectiveness 3': 'CME3',
             'Teachers _ Classroom Management Effectiveness 4': 'CME4',
             'Teacher _ Student Engagement Effectiveness 1': 'SEE1',
             'Teacher _ Student Engagement Effectiveness 2': 'SEE2',
             'Teacher _ Student Engagement Effectiveness 3': 'SEE3',
             'Teacher _ Student Engagement Effectiveness 4': 'SEE4',
             'Teacher _ Idea Generation 1': 'IG1',
             'Teacher _ Idea Generation 2': 'IG2',
             'Teacher _ Idea Generation 3': 'IG3',
             'Teacher _ Creative Communication 1': 'CC1',
             'Teacher _ Creative Communication 2': 'CC2',
             'Teacher _ Creative Communication 3': 'CC3',
             'Teacher _ Creative Implementation 1': 'CI1',
             'Teacher _ Creative Implementation 2': 'CI2',
             'Teacher _ Creative Implementation 3': 'CI3'},
  'ranges': {'xing_2026_pe_teacher_psych_empowerment': (1, 5),
             'xing_2026_pe_teacher_teaching_efficacy': (1, 9),
             'xing_2026_pe_teacher_innovative_work': (1, 7)},
  'label': 'xing_2026_pe_teacher_iwb'}]


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
