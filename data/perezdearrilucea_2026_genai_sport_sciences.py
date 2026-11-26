#!/usr/bin/env python3
# Source: https://zenodo.org/records/23077655
# DOI: 10.5281/zenodo.23077655 (data)
#   Perez De Arrilucea U, Tortola-Navarro A, Torregrosa D, Szendrei B, Ortiz Sanchez JA (2026). Dataset - Artificial Intelligence in Sports Science Education: Insights from Spanish Students [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23077655
# License: CC BY 4.0 (record metadata)
# Data: 'Habitos uso HIA por CAFD.sav' (value labels), 119 sport-science students at two Spanish universities; id = row order.
#   Blocks follow the questionnaire order: task-use frequency (1-5), perceptions (1-5), ethical judgements (1-3), attitudes (1-7).
# Covariates: sex, age, year, AI use in daily life / academia, admitted misuse (yes/no).
# Dropped: free text, the 'other tasks' perception item UsoOtras, the reverse-coded copy INV_Complicada, filter and the seven attitude composites.
# PII: none.
# Item text: item topics are the variable names; Spanish value labels give the response options.
import io
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://zenodo.org/api/records/23077655/files/H%C3%A1bitos%20uso%20HIA%20por%20CAFD.sav/content'
N_ROWS = 119
ID_COL = None
COVS = {'Sexo': 'cov_sex',
 'Edad': 'cov_age',
 'curso': 'cov_year',
 'HIAvida': 'cov_uses_ai_daily_life',
 'HIAacademia': 'cov_uses_ai_academic',
 'UsoHIAmal': 'cov_misused_ai'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'perezdearrilucea_2026_genai_use': ['HIA.GenText',
                                     'HIA.Audiov',
                                     'HIA.GenPpt',
                                     'HIA.Busqueda',
                                     'HIA.Transcrip',
                                     'HIA.Extraccion',
                                     'HIA.Resum',
                                     'HIA.Traduc',
                                     'HIA.Excel',
                                     'HIA.Logos',
                                     'HIA.AnalisisDatos',
                                     'HIA.An.Imagen',
                                     'Otras'],
 'perezdearrilucea_2026_genai_perceptions': ['HIA.Atractivo',
                                             'HIA.Eficiente',
                                             'HIA.Motivador',
                                             'HIA.Rdmnto',
                                             'HIA.Confusion',
                                             'HIA.Aburrimiento',
                                             'HIA.Potenciacion',
                                             'HIA.Desconocimiento',
                                             'HIA.Facil',
                                             'HIA.Rebanio',
                                             'HIA.Cogni',
                                             'HIA.EsCorrecto',
                                             'HIA.Notas'],
 'perezdearrilucea_2026_genai_ethics': ['EticoModJPGinvent',
                                        'EticoModJPGQoEst',
                                        'EticoGenJPGfake',
                                        'EticoRedacEmailW',
                                        'EticoRedaEmailPers',
                                        'EticoRedacW',
                                        'EticoGenResumen',
                                        'EticoGenEsquema',
                                        'EticoAnalGráficosGenResu',
                                        'EticoTraducir',
                                        'Eticotext.vídeo',
                                        'EticoGenPPT'],
 'perezdearrilucea_2026_genai_attitudes': ['TengoCuriosidad',
                                           'PreocupaAbrumado',
                                           'QueriaHIA',
                                           'Sospecho',
                                           'AnsiaAprender',
                                           'Desconfio',
                                           'InteresHIA',
                                           'SustoMalhecho',
                                           'TengoConocimient',
                                           'OlvidoProblemas',
                                           'HIAesComodo',
                                           'HayRiesgo',
                                           'FacilEntenderHIA',
                                           'Actualizado',
                                           'OlvidoMundo',
                                           'MejoraTareas',
                                           'Peligrosa',
                                           'Sencilla',
                                           'Asequible',
                                           'MeInformo',
                                           'Participacion',
                                           'Pagaria',
                                           'AlteraRutina',
                                           'Complicada',
                                           'Accesible',
                                           'ActualizadoAvances',
                                           'OtroMundoHIA',
                                           'AyudaDiaria',
                                           'HIAdesventaja',
                                           'FacilAdquisicion']}
# (lo, hi) response range per table
RANGES = {'perezdearrilucea_2026_genai_use': (1, 5),
 'perezdearrilucea_2026_genai_perceptions': (1, 5),
 'perezdearrilucea_2026_genai_ethics': (1, 3),
 'perezdearrilucea_2026_genai_attitudes': (1, 7)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Otros': 'free text',
 'UsoOtras': 'single item, filter or composite score',
 'PorQue': 'free text',
 'INV_Complicada': 'reverse-coded copy',
 'filter_$': 'single item, filter or composite score',
 'FullHIA': 'single item, filter or composite score',
 'CURIOSIDAD': 'single item, filter or composite score',
 'ANSIEDAD': 'single item, filter or composite score',
 'INTERES': 'single item, filter or composite score',
 'FACILIDAD': 'single item, filter or composite score',
 'INMERSION': 'single item, filter or composite score',
 'ESCEPTICISMO': 'single item, filter or composite score',
 'ACCESIBILIDAD': 'single item, filter or composite score'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    import pyreadstat, tempfile
    with tempfile.NamedTemporaryFile(suffix=".sav") as f:
        f.write(content); f.flush()
        d, _ = pyreadstat.read_sav(f.name, user_missing=False)
    return d


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    return d


def main():
    r = requests.get(URL, timeout=300, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    d = prep(d)
    assert len(d) == N_ROWS, len(d)
    if ID_COL:
        assert (d[[ID_COL, "wave"]] if "wave" in d else d[ID_COL]).duplicated().sum() == 0, "duplicate ids"
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        if cov in COV_MAPS:
            d[src] = d[src].map(lambda v: v.strip() if isinstance(v, str) else v)
            d[cov] = d[src].map(COV_MAPS[cov])
            assert d[cov].notna().sum() == d[src].notna().sum(), (cov, set(d[src].dropna()) - set(COV_MAPS[cov]))
        else:
            d[cov] = d[src]
    covs = list(dict.fromkeys(COVS.values()))
    items_all = [c for v in BLOCKS.values() for c in v]
    assert len(items_all) == len(set(items_all)), "item in two tables"
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id", "wave"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        wv = ["wave"] if name in WAVE_TABLES else []
        src = d if (wv or "wave" not in d) else d[d["wave"] == WAVE_BASE]
        t = src[["id"] + wv + covs + items].melt(id_vars=["id"] + wv + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        if name in DROP_VALUES:
            t.loc[t["resp"].isin(DROP_VALUES[name]), "resp"] = np.nan
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + wv + covs].sort_values(["id"] + wv + ["item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
