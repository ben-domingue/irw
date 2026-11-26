#!/usr/bin/env python3
# Source: https://zenodo.org/records/22308379
# DOI: 10.5281/zenodo.22308379 (data)
#   Trejo Vazquez K, Galvan-Tejada JI, Galvan-Tejada CE (2026). Sociodemographic, Academic, and Psychometric Dataset on Anxiety, Depression, and Academic Performance in High-School Adolescents [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22308379
# License: CC BY 4.0 (record metadata)
# Data: 'A&D&Adolescentes.xlsx', 252 Mexican upper-secondary students aged 16-18; id = row order. The 21 BAI symptoms are the headers with
#   text answers No/Leve/Moderado/Severo (one 'Leveo' typo read as Leve) -> 0-3. The 21 BDI-II items store the chosen option sentence
#   instead of a code and are not shipped.
# Item codes bai_k are positional (k-th BAI column).
# Covariates: age, sex, marital status, semester, GPA.
# Dropped: the BDI-II option texts, ~20 single descriptive questions.
# PII: none.
# Item text: BAI symptom words are the headers; published BAI.
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
URL = 'https://zenodo.org/api/records/22308379/files/A&D&Adolescentes.xlsx/content'
N_ROWS = 252
ID_COL = None
COVS = {'Edad': 'cov_age',
 'Sexo': 'cov_sex',
 'Estado Civil': 'cov_marital',
 'Ciclo que cursa actualmente': 'cov_semester',
 '¿Cuál es tu promedio general hasta este momento?': 'cov_gpa'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'trejovazquez_2026_bai': ['bai_1',
                           'bai_2',
                           'bai_3',
                           'bai_4',
                           'bai_5',
                           'bai_6',
                           'bai_7',
                           'bai_8',
                           'bai_9',
                           'bai_10',
                           'bai_11',
                           'bai_12',
                           'bai_13',
                           'bai_14',
                           'bai_15',
                           'bai_16',
                           'bai_17',
                           'bai_18',
                           'bai_19',
                           'bai_20',
                           'bai_21']}
# (lo, hi) response range per table
RANGES = {'trejovazquez_2026_bai': (0, 3)}
# values set to missing per table (documented sentinel / out-of-range codes)
DROP_VALUES = {}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'Grupo': 'single descriptive question / group letter',
 '¿Actualmente trabaja?': 'single descriptive question / group letter',
 '¿Cuenta con apoyo económico para sus estudios?': 'single descriptive question / group letter',
 '¿Cuál tipo de apoyo recibe?': 'single descriptive question / group letter',
 '¿Con quién vive actualmente?': 'single descriptive question / group letter',
 '¿Cómo te sientes al formar parte de esta gran familia universitaria?': 'single descriptive question / group letter',
 '¿Has tenido algún problema administrativo a partir de tu ingreso? EN SU CASO: ¿Lo has resuelto?': 'single '
                                                                                                    'descriptive '
                                                                                                    'question / '
                                                                                                    'group letter',
 '¿Cómo te sientes cursando el bachillerato que elegiste?': 'single descriptive question / group letter',
 '¿Por qué elegiste este bachillerato?': 'single descriptive question / group letter',
 '¿Satisface tus expectativas académicas?': 'single descriptive question / group letter',
 '¿Cómo te sientes en tus clases?': 'single descriptive question / group letter',
 '¿Hasta hoy cómo es tu rendimiento escolar? ¿Existe alguna dificultad en determinada materia? EN SU CASO: ¿Con cuál o cuáles y por qué?': 'single '
                                                                                                                                           'descriptive '
                                                                                                                                           'question '
                                                                                                                                           '/ '
                                                                                                                                           'group '
                                                                                                                                           'letter',
 '¿Qué has hecho para superar esas dificultades?': 'single descriptive question / group letter',
 '¿Cuáles son tus planes al terminar tu preparatoria?': 'single descriptive question / group letter',
 '¿Cuánto tiempo le dedicas a las clases?': 'single descriptive question / group letter',
 '¿Cuánto tiempo le dedicas a estudiar?': 'single descriptive question / group letter',
 '¿Cuánto tiempo le dedicas al deporte?': 'single descriptive question / group letter',
 '¿Cuánto tiempo le dedicas a la familia?': 'single descriptive question / group letter',
 'Problemas personales que consideras que influyen en tu estudio y en tu aprendizaje': 'single descriptive question '
                                                                                       '/ group letter',
 '¿Cómo se encuentra tu motivación personal hacia el estudio?': 'single descriptive question / group letter',
 '¿Cómo es la interacción con tus compañeros?': 'single descriptive question / group letter',
 '¿Cómo es la interacción con tus maestros?': 'single descriptive question / group letter',
 'Tristeza': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Pesimismo': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Fracaso pasado': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Pérdida de placer': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Sentimientos de culpabilidad': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not '
                                 'shipped)',
 'Sentimientos de castigo': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not '
                            'shipped)',
 'Desagrado hacia uno mismo/a': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not '
                                'shipped)',
 'Autocrítica': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Pensamientos o deseos de suicidio': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; '
                                      'not shipped)',
 'Llanto': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Agitación': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Pérdida de interés': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Indecisión': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Sentimientos de inutilidad': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not '
                               'shipped)',
 'Pérdida de energía': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Cambios en el sueño': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Irritabilidad': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Cambios en el apetito': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Dificultades de concentración': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not '
                                  'shipped)',
 'Cansancio o fatiga': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not shipped)',
 'Pérdida de interés por el sexo': 'BDI-II item stored as the full option sentence (needs the BDI-II option key; not '
                                   'shipped)'}
# long panels: prep() returns one row per person x wave in column "wave"; tables listed here keep the wave column,
# the rest use wave == WAVE_BASE rows only
WAVE_TABLES = set()
WAVE_BASE = 1


def load(content):
    return pd.read_excel(io.BytesIO(content), sheet_name=0, header=0)


def slug(v):
    """lower-case snake form of a text covariate value"""
    return v if pd.isna(v) else re.sub(r"[^0-9a-z]+", "_", str(v).strip().lower()).strip("_")


def prep(d):
    """BAI symptoms are the headers (Torpe o entumecido ... Con sudores); bai_k = k-th BAI column in file order; labels mapped No/Leve/Moderado/Severo = 0-3"""
    m = {"no": 0, "leve": 1, "leveo": 1, "moderado": 2, "severo": 3}
    bai = ['Torpe o entumecido', 'Acalorado', 'Con temblor en las piernas', 'Incapaz de relajarse', 'Con temor a que ocurra lo peor', 'Mareado, o que se le va la cabeza', 'Con latidos del corazón fuertes y acelerados', 'Inestable', 'Atemorizado o asustado', 'Nervioso', 'Con sensación de bloqueo', 'Con temblores en las manos', 'Inquieto, inseguro', 'Con miedo a perder el control', 'Con sensación de ahogo', 'Con temor a morir', 'Con miedo', 'Con problemas digestivos', 'Con desvanecimientos', 'Con rubor facial', 'Con sudores, fríos o calientes']
    for k, c in enumerate(bai, 1):
        d["bai_%d" % k] = d[c].map(lambda v: v if pd.isna(v) else m[str(v).strip().lower()])
    d = d.drop(columns=bai)
    for c in ["Sexo", "Estado Civil", "Ciclo que cursa actualmente"]:
        d[c] = d[c].map(slug)
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
