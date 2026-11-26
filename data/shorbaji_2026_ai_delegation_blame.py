#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/gnwmrywr3w
# DOI: 10.17632/gnwmrywr3w (data)
#   Fouad Shorbaji (2026). Who’s Responsible? How Delegating Purchase Decisions to AI Agents Shifts Control and
#     Blame in Online Shopping
# License: CC BY 4.0 (repository record)
# Data: Three online experiments on delegating purchase decisions to AI agents (594, 718 and 687 respondents; 556,
#   642 and 631 after the authors' exclude_final flag, which the script applies). Every scale is a 1-7 multi-item
#   block named by its column stem; scales asked in more than one study (authority, repurchase intention, the four
#   blame targets, anthropomorphism, AI autonomy) are pooled across studies with cov_study and ids prefixed by study
#   (s1_, s2_, s3_).
# Tables: one per scale, item = the deposit column (auth_1 etc.).
# Covariates: cov_study, cov_condition (the study's manipulated factor as deposited: condition in study 1,
#   delegation in 2-3), cov_age, cov_gender (as deposited).
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

SOURCES = [{'url': 'https://data.mendeley.com/public-files/datasets/gnwmrywr3w/files/971d3680-c01b-4e48-a672-4e5dfc6bc38b/file_downloaded',
  'kind': 'excel',
  'read_kw': {'sheet_name': 'study_1'},
  'n_rows': 594,
  'range': (1, 7),
  'blocks': {'shorbaji_2026_perceived_authority': ['auth_1', 'auth_2', 'auth_3', 'auth_4', 'auth_5', 'auth_6'],
             'shorbaji_2026_repurchase_intention': ['intent_1', 'intent_2', 'intent_3'],
             'shorbaji_2026_self_blame': ['selfblame_1', 'selfblame_2', 'selfblame_3'],
             'shorbaji_2026_ai_blame': ['aiblame_1', 'aiblame_2', 'aiblame_3'],
             'shorbaji_2026_platform_blame': ['platformblame_1', 'platformblame_2', 'platformblame_3'],
             'shorbaji_2026_seller_blame': ['sellerblame_1', 'sellerblame_2', 'sellerblame_3'],
             'shorbaji_2026_anthropomorphism': ['anthro_1', 'anthro_2', 'anthro_3'],
             'shorbaji_2026_ai_autonomy': ['auton_1', 'auton_2', 'auton_3'],
             'shorbaji_2026_perceived_control': ['permcontrol_1', 'permcontrol_2', 'permcontrol_3', 'permcontrol_4'],
             'shorbaji_2026_role_recognition': ['rolerec_1', 'rolerec_2', 'rolerec_3'],
             'shorbaji_2026_felt_involvement': ['feltinv_1', 'feltinv_2', 'feltinv_3'],
             'shorbaji_2026_perceived_contribution': ['percontrib_1', 'percontrib_2', 'percontrib_3'],
             'shorbaji_2026_frustration': ['frustration_1', 'frustration_2', 'frustration_3'],
             'shorbaji_2026_competence': ['competence_1', 'competence_2', 'competence_3']},
  'covs': {'age': 'cov_age', 'gender': 'cov_gender', 'condition': 'cov_condition'},
  'cov_maps': {},
  'not_shipped': {'response_id': 'survey response id',
                  'participant_id': 'panel participant id (id = study + row order instead)',
                  'duration_sec': 'manipulation check, flag, single-item rating, timing or background code, not '
                                  'carried',
                  'condition_num': 'manipulation check, flag, single-item rating, timing or background code, not '
                                   'carried',
                  'product_category': 'manipulation check, flag, single-item rating, timing or background code, not '
                                      'carried',
                  'failure_type': 'manipulation check, flag, single-item rating, timing or background code, not '
                                  'carried',
                  'mc_decision_maker': 'manipulation check, flag, single-item rating, timing or background code, not '
                                       'carried',
                  'mc_delegation_level': 'manipulation check, flag, single-item rating, timing or background code, '
                                         'not carried',
                  'mc_ai_involvement': 'manipulation check, flag, single-item rating, timing or background code, not '
                                       'carried',
                  'mc_final_authority': 'manipulation check, flag, single-item rating, timing or background code, '
                                        'not carried',
                  'mc_human_involvement': 'manipulation check, flag, single-item rating, timing or background code, '
                                          'not carried',
                  'comp_check_passed': 'manipulation check, flag, single-item rating, timing or background code, not '
                                       'carried',
                  'cs_self': 'manipulation check, flag, single-item rating, timing or background code, not carried',
                  'cs_ai': 'manipulation check, flag, single-item rating, timing or background code, not carried',
                  'cs_platform': 'manipulation check, flag, single-item rating, timing or background code, not '
                                 'carried',
                  'cs_seller': 'manipulation check, flag, single-item rating, timing or background code, not carried',
                  'attention_check_1': 'manipulation check, flag, single-item rating, timing or background code, not '
                                       'carried',
                  'speed_flag': 'manipulation check, flag, single-item rating, timing or background code, not '
                                'carried',
                  'failed_manipulation': 'manipulation check, flag, single-item rating, timing or background code, '
                                         'not carried',
                  'exclude_final': 'manipulation check, flag, single-item rating, timing or background code, not '
                                   'carried',
                  'education': 'manipulation check, flag, single-item rating, timing or background code, not carried',
                  'online_shopping_freq': 'manipulation check, flag, single-item rating, timing or background code, '
                                          'not carried',
                  'ai_familiarity': 'manipulation check, flag, single-item rating, timing or background code, not '
                                    'carried'},
  'keep_col_eq': ['exclude_final', 0],
  'keep_reason': "the authors' exclude_final flag",
  'id_prefix': 's1',
  'const_covs': {'cov_study': 'study1'},
  'label': 'shorbaji_2026 study_1'},
 {'url': 'https://data.mendeley.com/public-files/datasets/gnwmrywr3w/files/971d3680-c01b-4e48-a672-4e5dfc6bc38b/file_downloaded',
  'kind': 'excel',
  'read_kw': {'sheet_name': 'Study_2'},
  'n_rows': 718,
  'range': (1, 7),
  'blocks': {'shorbaji_2026_perceived_authority': ['auth_1', 'auth_2', 'auth_3', 'auth_4', 'auth_5', 'auth_6'],
             'shorbaji_2026_repurchase_intention': ['intent_1', 'intent_2', 'intent_3'],
             'shorbaji_2026_self_blame': ['selfblame_1', 'selfblame_2', 'selfblame_3'],
             'shorbaji_2026_ai_blame': ['aiblame_1', 'aiblame_2', 'aiblame_3'],
             'shorbaji_2026_platform_blame': ['platformblame_1', 'platformblame_2', 'platformblame_3'],
             'shorbaji_2026_seller_blame': ['sellerblame_1', 'sellerblame_2', 'sellerblame_3'],
             'shorbaji_2026_anthropomorphism': ['anthro_1', 'anthro_2', 'anthro_3'],
             'shorbaji_2026_ai_autonomy': ['auton_1', 'auton_2', 'auton_3'],
             'shorbaji_2026_participation': ['partic_1', 'partic_2', 'partic_3']},
  'covs': {'age': 'cov_age', 'gender': 'cov_gender', 'delegation': 'cov_condition'},
  'cov_maps': {},
  'not_shipped': {'response_id': 'survey response id',
                  'participant_id': 'panel participant id (id = study + row order instead)',
                  'duration_sec': 'manipulation check, flag, single-item rating, timing or background code, not '
                                  'carried',
                  'delegation_num': 'manipulation check, flag, single-item rating, timing or background code, not '
                                    'carried',
                  'oversight': 'manipulation check, flag, single-item rating, timing or background code, not carried',
                  'oversight_num': 'manipulation check, flag, single-item rating, timing or background code, not '
                                   'carried',
                  'product_category': 'manipulation check, flag, single-item rating, timing or background code, not '
                                      'carried',
                  'failure_type': 'manipulation check, flag, single-item rating, timing or background code, not '
                                  'carried',
                  'mc_delegation_level': 'manipulation check, flag, single-item rating, timing or background code, '
                                         'not carried',
                  'mc_ai_involvement': 'manipulation check, flag, single-item rating, timing or background code, not '
                                       'carried',
                  'mc_oversight_present': 'manipulation check, flag, single-item rating, timing or background code, '
                                          'not carried',
                  'mc_override_ability': 'manipulation check, flag, single-item rating, timing or background code, '
                                         'not carried',
                  'mc_confirmation_required': 'manipulation check, flag, single-item rating, timing or background '
                                              'code, not carried',
                  'oversight_perceived': 'manipulation check, flag, single-item rating, timing or background code, '
                                         'not carried',
                  'cs_self': 'manipulation check, flag, single-item rating, timing or background code, not carried',
                  'cs_ai': 'manipulation check, flag, single-item rating, timing or background code, not carried',
                  'cs_platform': 'manipulation check, flag, single-item rating, timing or background code, not '
                                 'carried',
                  'cs_seller': 'manipulation check, flag, single-item rating, timing or background code, not carried',
                  'attention_check_1': 'manipulation check, flag, single-item rating, timing or background code, not '
                                       'carried',
                  'speed_flag': 'manipulation check, flag, single-item rating, timing or background code, not '
                                'carried',
                  'failed_manipulation': 'manipulation check, flag, single-item rating, timing or background code, '
                                         'not carried',
                  'exclude_final': 'manipulation check, flag, single-item rating, timing or background code, not '
                                   'carried',
                  'education': 'manipulation check, flag, single-item rating, timing or background code, not carried',
                  'online_shopping_freq': 'manipulation check, flag, single-item rating, timing or background code, '
                                          'not carried',
                  'ai_familiarity': 'manipulation check, flag, single-item rating, timing or background code, not '
                                    'carried'},
  'keep_col_eq': ['exclude_final', 0],
  'keep_reason': "the authors' exclude_final flag",
  'id_prefix': 's2',
  'const_covs': {'cov_study': 'study2'},
  'label': 'shorbaji_2026 Study_2'},
 {'url': 'https://data.mendeley.com/public-files/datasets/gnwmrywr3w/files/971d3680-c01b-4e48-a672-4e5dfc6bc38b/file_downloaded',
  'kind': 'excel',
  'read_kw': {'sheet_name': 'Study_3'},
  'n_rows': 687,
  'range': (1, 7),
  'blocks': {'shorbaji_2026_perceived_authority': ['auth_1', 'auth_2', 'auth_3', 'auth_4', 'auth_5', 'auth_6'],
             'shorbaji_2026_repurchase_intention': ['intent_1', 'intent_2', 'intent_3'],
             'shorbaji_2026_self_blame': ['selfblame_1', 'selfblame_2', 'selfblame_3'],
             'shorbaji_2026_ai_blame': ['aiblame_1', 'aiblame_2', 'aiblame_3'],
             'shorbaji_2026_platform_blame': ['platformblame_1', 'platformblame_2', 'platformblame_3'],
             'shorbaji_2026_seller_blame': ['sellerblame_1', 'sellerblame_2', 'sellerblame_3'],
             'shorbaji_2026_trust': ['trust_1', 'trust_2', 'trust_3'],
             'shorbaji_2026_future_use': ['futureuse_1', 'futureuse_2', 'futureuse_3'],
             'shorbaji_2026_switch_to_manual': ['switch_manual_1', 'switch_manual_2', 'switch_manual_3']},
  'covs': {'age': 'cov_age', 'gender': 'cov_gender', 'delegation': 'cov_condition'},
  'cov_maps': {},
  'not_shipped': {'response_id': 'survey response id',
                  'participant_id': 'panel participant id (id = study + row order instead)',
                  'duration_sec': 'manipulation check, flag, single-item rating, timing or background code, not '
                                  'carried',
                  'delegation_num': 'manipulation check, flag, single-item rating, timing or background code, not '
                                    'carried',
                  'failure_source': 'manipulation check, flag, single-item rating, timing or background code, not '
                                    'carried',
                  'failure_source_num': 'manipulation check, flag, single-item rating, timing or background code, '
                                        'not carried',
                  'failure_type': 'manipulation check, flag, single-item rating, timing or background code, not '
                                  'carried',
                  'product_category': 'manipulation check, flag, single-item rating, timing or background code, not '
                                      'carried',
                  'mc_delegation_level': 'manipulation check, flag, single-item rating, timing or background code, '
                                         'not carried',
                  'mc_ai_involvement': 'manipulation check, flag, single-item rating, timing or background code, not '
                                       'carried',
                  'mc_failure_source': 'manipulation check, flag, single-item rating, timing or background code, not '
                                       'carried',
                  'mc_primary_responsible': 'manipulation check, flag, single-item rating, timing or background '
                                            'code, not carried',
                  'mc_error_maker': 'manipulation check, flag, single-item rating, timing or background code, not '
                                    'carried',
                  'attrib_ambig': 'manipulation check, flag, single-item rating, timing or background code, not '
                                  'carried',
                  'cs_self': 'manipulation check, flag, single-item rating, timing or background code, not carried',
                  'cs_ai': 'manipulation check, flag, single-item rating, timing or background code, not carried',
                  'cs_platform': 'manipulation check, flag, single-item rating, timing or background code, not '
                                 'carried',
                  'cs_seller': 'manipulation check, flag, single-item rating, timing or background code, not carried',
                  'primary_responsible_choice': 'manipulation check, flag, single-item rating, timing or background '
                                                'code, not carried',
                  'attention_check_1': 'manipulation check, flag, single-item rating, timing or background code, not '
                                       'carried',
                  'speed_flag': 'manipulation check, flag, single-item rating, timing or background code, not '
                                'carried',
                  'failed_manipulation': 'manipulation check, flag, single-item rating, timing or background code, '
                                         'not carried',
                  'exclude_final': 'manipulation check, flag, single-item rating, timing or background code, not '
                                   'carried',
                  'education': 'manipulation check, flag, single-item rating, timing or background code, not carried',
                  'online_shopping_freq': 'manipulation check, flag, single-item rating, timing or background code, '
                                          'not carried',
                  'ai_familiarity': 'manipulation check, flag, single-item rating, timing or background code, not '
                                    'carried'},
  'keep_col_eq': ['exclude_final', 0],
  'keep_reason': "the authors' exclude_final flag",
  'id_prefix': 's3',
  'const_covs': {'cov_study': 'study3'},
  'label': 'shorbaji_2026 Study_3'}]


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
