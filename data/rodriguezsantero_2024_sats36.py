"""Survey of Attitudes Toward Statistics (SATS-36), Spanish education students.

Source: Rodriguez-Santero & Gil-Flores (2024), Zenodo 10.5281/zenodo.10546410,
CC BY 4.0 -- "Instrument and database used in the article: Attitudes towards
statistics of Education Sciences students" (RELIEVE). 318 respondents.

Ships the 36 SATS-36 items (`Item1`..`Item36`) on the instrument's 1-7 scale.

`Item40`..`Item43` are numbered like items but are not. Their SPSS labels are
"40. Sexo", "41. Edad", "42. Tipo de Bachillerato" and "43. Cuantas materias
de Matematicas o Estadistica..." -- sex, age, school track and a subject count.
The source has no Item37-39 at all. Reading the block as "every column called
Item*" would have put a 0-54 age variable into a 1-7 item set; the labels, not
the naming pattern, decide.

`Item42`/`Item43` look like duplicates of the named `Tipo_Bachillerato` and
`Numero_materias` columns but are not -- an assert established that rather than
the docstring assuming it. `Item42` holds the raw 5-category track response for
all 318 respondents; `Tipo_Bachillerato` is a 2-category recode with 175
missing. `Item43` is the raw 0-5 count; `Numero_materias` a 0-3 recode with 166
missing. Both the raw and recoded forms ship as covariates, since the recode
rule is not recoverable from the raw codes and the raw form is the complete
one.

Seven further columns are the SATS-36 subscale scores plus a total (Afecto,
Competencia, Dificultad, Valores, Interes, Esfuerzo, Total) and are dropped as
composites.
"""
import os
import re

import pandas as pd
import pyreadstat
import requests

RECORD = 10546410
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "automated_finding", "irw_output")
TABLE = "rodriguezsantero_2024_sats36"

COMPOSITES = ["Afecto", "Competencia", "Dificultad", "Valores", "Interés",
              "Esfuerzo", "Total"]
COVARIATES = {
    "Item40": "cov_sex",
    "Item41": "cov_age",
    "Item42": "cov_track",
    "Item43": "cov_n_math_subjects",
    "Grupo": "cov_group",
    "Conv.Agot": "cov_exam_sitting",
    "Rendimiento_escolarç": "cov_school_achievement",
    "Autocoencepto": "cov_self_concept",
    "Rendimiento_previo": "cov_prior_achievement",
    "Expectativas": "cov_expectations",
    "Tipo_Bachillerato": "cov_track_recoded",
    "Número_materias": "cov_n_math_subjects_recoded",
}


def fetch_raw(path=None):
    if path and os.path.exists(path):
        return path
    rec = requests.get(f"https://zenodo.org/api/records/{RECORD}",
                       timeout=120).json()
    f = next(x for x in rec["files"] if x["key"].lower().endswith(".sav"))
    r = requests.get(f["links"]["self"], timeout=600)
    r.raise_for_status()
    local = os.path.join("/tmp", f["key"])
    with open(local, "wb") as fh:
        fh.write(r.content)
    return local


def main(path=None):
    src = fetch_raw(path)
    try:
        df, meta = pyreadstat.read_sav(src, apply_value_formats=False)
    except Exception:
        df, meta = pyreadstat.read_sav(src, apply_value_formats=False,
                                       encoding="latin1")

    items = [c for c in df.columns
             if re.match(r"^Item\d+$", str(c))
             and c not in COVARIATES]
    assert len(items) == 36, f"expected 36 SATS items, found {len(items)}"

    accounted = set(items) | set(COVARIATES) | set(COMPOSITES)
    unaccounted = [c for c in df.columns if c not in accounted]
    assert not unaccounted, f"unaccounted source columns: {unaccounted}"

    df = df.rename(columns=COVARIATES)
    covs = [v for v in COVARIATES.values() if v in df.columns]
    df = df.reset_index(drop=True)
    df["id"] = df.index + 1

    long = (df.melt(id_vars=["id"] + covs, value_vars=items,
                    var_name="item", value_name="resp")
              .dropna(subset=["resp"]))
    long["resp"] = long["resp"].astype(int)
    long = long[["id", "item", "resp"] + covs]

    assert long["id"].nunique() >= 100
    assert long["item"].nunique() == 36
    assert long["resp"].between(1, 7).all(), "SATS-36 is a 1-7 scale"

    os.makedirs(OUT_DIR, exist_ok=True)
    long.to_csv(os.path.join(OUT_DIR, f"{TABLE}.csv"), index=False)
    print(f"{TABLE}: {len(long):,} rows, {long['id'].nunique():,} ids, "
          f"{long['item'].nunique()} items")


if __name__ == "__main__":
    main()
