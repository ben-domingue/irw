#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/AI-Driven_Journeys_The_Adoption_of_Artificial_Intelligence_AI_Chatbots_in_Tourism_and_Hospitality_by_Gen_Z_Dataset_/28184666
# DOI: 10.6084/m9.figshare.28184666.v1 (data)
#   Jerónimo Paiva (2025). AI-Driven Journeys: The Adoption of Artificial Intelligence (AI) Chatbots in Tourism and
#     Hospitality by Gen Z (Dataset)
# License: CC BY 4.0 (repository record)
# Data: 100 Portuguese Gen Z respondents (CSV export, latin-1). Each header holds the item code and the Portuguese
#   statement ("[SI1: ...]"); items keep the code. Constructs read from the codes and statements (social influence,
#   hedonic motivation, anthropomorphism, effort/performance expectancy, emotional response as bipolar adjective
#   pairs, willingness to accept, objections). The second CSV is a SmartPLS report and is not data.
# Tables: one per construct, item = the deposit code.
# Covariates: none carried
# PII: none found (string columns screened)
# Item text: not shipped -- Portuguese statements are the column headers; anchors not in the deposit.
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

SOURCES = [{'url': 'https://ndownloader.figshare.com/files/51600236',
  'kind': 'csv',
  'read_kw': {'encoding': 'latin-1'},
  'n_rows': 100,
  'range': (1, 5),
  'blocks': {'paiva_2025_social_influence': ['SI1', 'SI2', 'SI3', 'SI4', 'SI5', 'SI6'],
             'paiva_2025_hedonic_motivation': ['HM1', 'HM2', 'HM3', 'HM4', 'HM5'],
             'paiva_2025_anthropomorphism': ['ANT1', 'ANT2', 'ANT3', 'ANT4'],
             'paiva_2025_effort_expectancy': ['EE1', 'EE2', 'EE3'],
             'paiva_2025_performance_expectancy': ['PE1', 'PE2', 'PE3', 'PE4'],
             'paiva_2025_emotional_response': ['ER1', 'ER2', 'ER3', 'ER4', 'ER5'],
             'paiva_2025_willingness_to_accept': ['WA1', 'WA2', 'WA3'],
             'paiva_2025_objections': ['OBJ1', 'OBJ2', 'OBJ3', 'OBJ4']},
  'covs': {},
  'cov_maps': {},
  'not_shipped': {'Idade': 'demographic or AI-experience screener, not carried',
                  'Género': 'demographic or AI-experience screener, not carried',
                  'Experiência com o uso de AI Generativa e chatbots em atividades turísticas e hospitalidade': 'demographic '
                                                                                                                'or '
                                                                                                                'AI-experience '
                                                                                                                'screener, '
                                                                                                                'not '
                                                                                                                'carried'},
  'rename': {'[SI1: Utilizar chatbots baseados em IA reflete um símbolo de status nas minhas redes sociais.]': 'SI1',
             '[SI2: Pessoas que influenciam o meu comportamento gostariam que eu utilizasse chatbots baseados em IA.]': 'SI2',
             '[SI3: Pessoas nas minhas redes sociais que utilizam chatbots baseados em IA têm mais prestígio do que aquelas que não utilizam.]': 'SI3',
             '[SI4: Pessoas cujas opiniões eu valorizo prefeririam que eu utilizasse chatbots baseados em IA.]': 'SI4',
             '[SI5: Pessoas que são importantes para mim encorajariam-me a utilizar chatbots baseados em IA.]': 'SI5',
             '[SI6: Pessoas nas minhas redes sociais que utilizam chatbots baseados em IA têm um perfil elevado.]': 'SI6',
             '[HM1: Divirto-me a interagir com chatbots baseados em IA.]': 'HM1',
             '[HM2: Interagir com chatbots baseados em IA é divertido.]': 'HM2',
             '[HM3: Interagir com chatbots baseados em IA é entretenimento.]': 'HM3',
             '[HM4: A interação com chatbots baseados em IA é agradável.]': 'HM4',
             '[HM5: O próprio processo de interagir com chatbots baseados em IA seria agradável.]': 'HM5',
             '[ANT1: Chatbots baseados em IA têm uma mente própria.]': 'ANT1',
             '[ANT2: Chatbots baseados em IA têm consciência.]': 'ANT2',
             '[ANT3: Chatbots baseados em IA têm livre-arbítrio.]': 'ANT3',
             '[ANT4: Chatbots baseados em IA vão experimentar emoções.]': 'ANT4',
             '[EE1: Utilizar chatbots baseados em IA demora demasiado tempo.]': 'EE1',
             '[EE2: Trabalhar com chatbots baseados em IA é muito difícil de entender e utilizar nos serviços.]': 'EE2',
             '[EE3: Demoro demasiado tempo a aprender como interagir com chatbots baseados em IA.]': 'EE3',
             '[PE1: Chatbots baseados em IA são mais precisos do que os seres humanos.]': 'PE1',
             '[PE2: Chatbots baseados em IA são mais precisos e cometem menos erros humanos.]': 'PE2',
             '[PE3: Chatbots baseados em IA fornecem um serviço mais consistente do que os seres humanos.]': 'PE3',
             '[PE4: As informações fornecidas por chatbots baseados em IA são mais consistentes.]': 'PE4',
             '[ER1: Aborrecido-relaxado.]': 'ER1',
             '[ER2: Melancólico-satisfeito.]': 'ER2',
             '[ER3: Desesperado-esperançoso.]': 'ER3',
             '[ER4: Insatisfeito-satisfeito.]': 'ER4',
             '[ER5: Irritado-prazeroso.]': 'ER5',
             '[WA1: Estou disposto a receber serviços de chatbots baseados em IA.]': 'WA1',
             '[WA2: Sentir-me-ei feliz ao interagir com chatbots baseados em IA.]': 'WA2',
             '[WA3: É provável que eu interaja com chatbots baseados em IA.]': 'WA3',
             '[OBJ1: A informação é processada de uma maneira menos humanizada.]': 'OBJ1',
             '[OBJ2: Prefiro o contacto humano nas transações de serviço.]': 'OBJ2',
             '[OBJ3: As pessoas precisam de troca de emoções durante as transações de serviço.]': 'OBJ3',
             '[OBJ4: A interação com chatbots baseados em IA carece de contacto social.]': 'OBJ4'},
  'label': 'paiva_2025_ai_chatbots_tourism'}]


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
