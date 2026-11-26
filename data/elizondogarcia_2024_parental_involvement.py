#!/usr/bin/env python3
# Source: https://zenodo.org/records/12587820
# DOI: 10.5281/zenodo.12587820 (data)
#   Elizondo-Garcia J (2024). DataSet Parental Involvement & Students' Self-Regulation [Data set]. Zenodo.
# License: CC BY 4.0 (Zenodo record metadata)
# Data: "Base de datos Final.xlsx", 119 Mexican primary pupils (grades 1-3; the deposit's ID ALUMNO), each with a
#   teacher's 10-item self-regulation rating and a parent's involvement questionnaire. Spanish text; headers carry
#   DOS (cp437) mojibake, read as stored.
# Tables:
#   _self_regulation: the 10 teacher-rated statements ("El niño escucha y sigue instrucciones." ...), observed 1-5;
#     the deposit's MEDIA AUTORREGULACIÓN equals their row mean in every row (checked). The headers are the full
#     statements, so item = sr1..sr10 in header order; RENAME holds each statement.
#   _involvement_barriers: 9 "how much of a problem is ..." items (trust in communicating with the school, school
#     openness, information, staff availability, other adults' treatment, belonging, own schedule, transport, teacher
#     communication), item = the deposit's own short code; resp = the deposit's "(escala)" column, 0 = "No es un
#     problema" ... 4 = "Es un problema muy grande/grave", checked against the text column item by item.
#   The three involvement-frequency questions (meetings, conferences, helping at school) each have their own response
#   set (0-3 or 0-4) and are not shipped; nor are the dichotomised "(poca o mucha)" copies or the three yes/no
#   questions.
# Covariates: cov_grade (1ro/2do/3ro).
# PII: none (28 text columns screened; all are response labels).
# Item text: not shipped -- the Spanish stems are the headers, but the deposit names no instrument and gives anchors
#   only for the barrier items.
import io
import re
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://zenodo.org/api/records/12587820/files/Base%20de%20datos%20Final.xlsx/content'
N_ROWS = 119
ID_COL = 'ID ALUMNO'
COVS = {'Grado del alumno': 'cov_grade'}
COV_MAPS = {'cov_grade': {'1ro': 1, '2do': 2, '3ro': 3}}
RENAME = {'El niño escucha y sigue instrucciones.': 'sr1',
 'Completa las actividades asignadas.': 'sr2',
 'Sabe concentrarse mientras trabaja, se distrae pocas veces.': 'sr3',
 'Identifica y corrige sus errores.': 'sr4',
 'Sabe esperar su turno.': 'sr5',
 'Sabe mantenerse bajo control y esperar cuando no tiene la atención de la maestra.': 'sr6',
 'Intenta resolver problemas antes de pedir ayuda.': 'sr7',
 'Siente satisfacción cuando resuelve situaciones o termina trabajos sol@.': 'sr8',
 'Sabe lidiar con corrección y retroalimentación.': 'sr9',
 'Se interesa por realizar actividades nuevas para él/ella.': 'sr10',
 'confianza (escala)': 'confianza',
 'apertura (escala)': 'apertura',
 'informacion (escala)': 'informacion',
 'personal (escala)': 'personal',
 'adultos (escala)': 'adultos',
 'pertenencia (escala)': 'pertenencia',
 'agenda (escala)': 'agenda',
 'transporte (escala)': 'transporte',
 'maestros (escala)': 'maestros'}
BLOCKS = {'elizondogarcia_2024_self_regulation': ['sr1', 'sr2', 'sr3', 'sr4', 'sr5', 'sr6', 'sr7', 'sr8', 'sr9', 'sr10'],
 'elizondogarcia_2024_involvement_barriers': ['confianza',
                                              'apertura',
                                              'informacion',
                                              'personal',
                                              'adultos',
                                              'pertenencia',
                                              'agenda',
                                              'transporte',
                                              'maestros']}
# (lo, hi) response range per table
RANGES = {'elizondogarcia_2024_self_regulation': (1, 5), 'elizondogarcia_2024_involvement_barriers': (0, 4)}
# source columns deliberately not shipped, with the reason
NOT_CARRIED = {'MEDIA AUTORREGULACIÓN': 'composite mean',
 '¨Con qu‚ frecuencia se re£ne con el maestro/a de la escuela de su hijo/a?': 'text twin or dichotomised copy of a '
                                                                              'shipped item, the three '
                                                                              'involvement-frequency questions (each '
                                                                              'with its own response set), or a '
                                                                              'yes/no question',
 'Reune (poca y mucha)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                         'questions (each with its own response set), or a yes/no question',
 'Reune (escala)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency questions '
                   '(each with its own response set), or a yes/no question',
 '¨Qu‚ tanto asiste a las conferencias para padres y los eventos familiares del colegio?': 'text twin or '
                                                                                           'dichotomised copy of a '
                                                                                           'shipped item, the three '
                                                                                           'involvement-frequency '
                                                                                           'questions (each with its '
                                                                                           'own response set), or a '
                                                                                           'yes/no question',
 'conferencias (poca o mucha)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                                'questions (each with its own response set), or a yes/no question',
 'conferencias (escala)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                          'questions (each with its own response set), or a yes/no question',
 'Durante el £ltimo a¤o, ¨con qu‚ frecuencia ha ayudado dentro de la escuela de su hijo/a?': 'text twin or '
                                                                                             'dichotomised copy of a '
                                                                                             'shipped item, the '
                                                                                             'three '
                                                                                             'involvement-frequency '
                                                                                             'questions (each with '
                                                                                             'its own response set), '
                                                                                             'or a yes/no question',
 'frecuencia ayuda (poca o mucha)': 'text twin or dichotomised copy of a shipped item, the three '
                                    'involvement-frequency questions (each with its own response set), or a yes/no '
                                    'question',
 'frecuencia ayuda (escala)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                              'questions (each with its own response set), or a yes/no question',
 'Confianza para comunicarme con la escuela.': 'text twin or dichotomised copy of a shipped item, the three '
                                               'involvement-frequency questions (each with its own response set), or '
                                               'a yes/no question',
 'confianza (poca o mucha)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                             'questions (each with its own response set), or a yes/no question',
 'Apertura de la escuela hacia los padres y madres de familia.': 'text twin or dichotomised copy of a shipped item, '
                                                                 'the three involvement-frequency questions (each '
                                                                 'with its own response set), or a yes/no question',
 'apertura (poca o mucha)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                            'questions (each with its own response set), or a yes/no question',
 'La escuela proporciona poca informaci¢n sobre actividades dirigidas a los padres de familia.': 'text twin or '
                                                                                                 'dichotomised copy '
                                                                                                 'of a shipped item, '
                                                                                                 'the three '
                                                                                                 'involvement-frequency '
                                                                                                 'questions (each '
                                                                                                 'with its own '
                                                                                                 'response set), or '
                                                                                                 'a yes/no question',
 'informacion (poca o mucha)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                               'questions (each with its own response set), or a yes/no question',
 'Disponibilidad del personal de la escuela.': 'text twin or dichotomised copy of a shipped item, the three '
                                               'involvement-frequency questions (each with its own response set), or '
                                               'a yes/no question',
 'personal (poca o mucha)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                            'questions (each with its own response set), or a yes/no question',
 'Le preocupa que otros adultos en la escuela traten a su hijo/a de manera diferente si usted comunica alguna inquietud.': 'text '
                                                                                                                           'twin '
                                                                                                                           'or '
                                                                                                                           'dichotomised '
                                                                                                                           'copy '
                                                                                                                           'of '
                                                                                                                           'a '
                                                                                                                           'shipped '
                                                                                                                           'item, '
                                                                                                                           'the '
                                                                                                                           'three '
                                                                                                                           'involvement-frequency '
                                                                                                                           'questions '
                                                                                                                           '(each '
                                                                                                                           'with '
                                                                                                                           'its '
                                                                                                                           'own '
                                                                                                                           'response '
                                                                                                                           'set), '
                                                                                                                           'or '
                                                                                                                           'a '
                                                                                                                           'yes/no '
                                                                                                                           'question',
 'adultos (poca o mucha)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                           'questions (each with its own response set), or a yes/no question',
 'Tiene un sentido de pertenencia con la comunidad escolar de su hijo/a.': 'text twin or dichotomised copy of a '
                                                                           'shipped item, the three '
                                                                           'involvement-frequency questions (each '
                                                                           'with its own response set), or a yes/no '
                                                                           'question',
 'pertenencia (poca o mucha)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                               'questions (each with its own response set), or a yes/no question',
 'Disponibilidad de mi agenda.': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                                 'questions (each with its own response set), or a yes/no question',
 'agenda (poca o mucha)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                          'questions (each with its own response set), or a yes/no question',
 'Dificultad para el transporte.': 'text twin or dichotomised copy of a shipped item, the three '
                                   'involvement-frequency questions (each with its own response set), or a yes/no '
                                   'question',
 'transporte (poca o mucha)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                              'questions (each with its own response set), or a yes/no question',
 'Comunicaci¢n con los maestros de mis hijos.': 'text twin or dichotomised copy of a shipped item, the three '
                                                'involvement-frequency questions (each with its own response set), '
                                                'or a yes/no question',
 'maestros (poca o mucha)': 'text twin or dichotomised copy of a shipped item, the three involvement-frequency '
                            'questions (each with its own response set), or a yes/no question',
 '¨Tiene preocupaciones de que el trayecto de camino a la escuela sea inseguro? (zonas peligrosas e inseguras)': 'text '
                                                                                                                 'twin '
                                                                                                                 'or '
                                                                                                                 'dichotomised '
                                                                                                                 'copy '
                                                                                                                 'of '
                                                                                                                 'a '
                                                                                                                 'shipped '
                                                                                                                 'item, '
                                                                                                                 'the '
                                                                                                                 'three '
                                                                                                                 'involvement-frequency '
                                                                                                                 'questions '
                                                                                                                 '(each '
                                                                                                                 'with '
                                                                                                                 'its '
                                                                                                                 'own '
                                                                                                                 'response '
                                                                                                                 'set), '
                                                                                                                 'or '
                                                                                                                 'a '
                                                                                                                 'yes/no '
                                                                                                                 'question',
 '¨Su hijo/a muestra resistencia a que usted se ponga en contacto con la escuela?': 'text twin or dichotomised copy '
                                                                                    'of a shipped item, the three '
                                                                                    'involvement-frequency questions '
                                                                                    '(each with its own response '
                                                                                    'set), or a yes/no question',
 '¨Tiene malos recuerdos de su propia experiencia en la escuela?': 'text twin or dichotomised copy of a shipped '
                                                                   'item, the three involvement-frequency questions '
                                                                   '(each with its own response set), or a yes/no '
                                                                   'question'}


def load(content):
    return pd.read_excel(io.BytesIO(content))


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
    assert len(d) == N_ROWS, len(d)
    d = d.rename(columns=RENAME)
    d = prep(d)
    if ID_COL:
        assert d[ID_COL].is_unique, "duplicate ids"
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
    covs = list(COVS.values())
    items_all = [c for v in BLOCKS.values() for c in v]
    assert len(items_all) == len(set(items_all)), "item in two tables"
    used = set(items_all) | set(COVS) | set(NOT_CARRIED) | {ID_COL, "id"} | set(covs)
    unbalanced = [c for c in d.columns if c not in used]
    assert not unbalanced, ("source columns neither shipped nor explained", unbalanced)
    shipped = set()
    total = 0
    for name, items in BLOCKS.items():
        assert len(name) <= 40 and name not in shipped, name
        assert all(c in d for c in items), [c for c in items if c not in d]
        lo, hi = RANGES[name]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(lo, hi).all(), (name, sorted(t.resp.unique()))
        assert (t["resp"] % 1 == 0).all(), (name, "non-integer resp")
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(lo, hi + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        total += len(t)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    print("total responses", total)


if __name__ == "__main__":
    main()
