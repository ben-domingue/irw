#!/usr/bin/env python3
# Source: https://zenodo.org/records/19196911
# DOI: 10.5281/zenodo.19196911 (data; no paper on the record)
#   Hernandez-Amaro, P., Lozano, F., & Gomez Garcia, L. (2026). "FCD
#   Questionnaire." Zenodo.
# Data: FCD_datos_protegidos.csv (217 respondents x 76 columns), a Spanish
#   online survey of crime victims: crime context, a 25-statement block on
#   thoughts, emotions and habits since the crime (1-5), then open questions
#   on reparation and reporting.
# License: CC BY 4.0 (Zenodo record).
# Codebook: none (the column headers are the item wording).
#
# Item text: not shipped -- the Spanish stems are the column headers (below),
#   but no rights-register row exists for the FCD; left for an itemtext pass.
#
# Table: hernandezamaro_2026_fcd -- the 25-statement block, one table: the
#   deposit names no subscales and there is no paper to supply a structure.
#   Items kept as deposited (no reverse-scoring).
# Item codes: the headers are full sentences, so items are coded fcd_01 ..
#   fcd_25 in column order; ITEMS below maps each code to its header and the
#   script asserts the header text, so the code-to-wording tie is checked, not
#   positional.
# Not shipped: the 4-item "what would help" block (therapy, telling others,
#   helping others, nothing can help -- not one construct), two single-item
#   reparation ratings, and every free-text column (crime narratives, reasons),
#   none of which is carried in any form.
# PII: no names, emails, dates, locations or IDs. The free text is victims'
#   accounts and is dropped.
# Covariates: cov_direct_victim (first question, yes/no), cov_reported (crime
#   reported to the authorities, yes/no), cov_age_at_crime (only where the
#   free-typed answer is a plain whole number 1-99; ranges and prose -> NA).
# id = row index.

import sys
from pathlib import Path

import pandas as pd
import requests
import io

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
UA = {"User-Agent": "IRW-Finder/1.0"}
DATA_URL = ("https://zenodo.org/api/records/19196911/files/"
            "FCD_datos_protegidos.csv/content")
TABLE = "hernandezamaro_2026_fcd"
STEMS = [
    "Siento enfado conmigo mismo/a por mis errores percibidos relacionados con el delito.",
    "He reducido significativamente mis actividades de ocio o las realizo en horarios específicos.",
    "Creo que nadie tiene la culpa de sufrir un delito.",
    "He implementado nuevas medidas de seguridad en mi vida.",
    "Me siento tonto/a por no haber visto las señales de advertencia.",
    "Dedico tiempo a analizar qué hice mal que me condujo al delito.",
    "Desde el delito presto atención a detalles que antes no atendía.",
    "Desde que sufrí el delito he aprendido a dejarme llevar/disfrutar de la vida.",
    "Desde el delito siento que me encuentro en permanente alerta.",
    "Creo que merecía mejor protección de la que me di a mí mismo/a.",
    "Experimento vergüenza al pensar en cómo manejé la situación.",
    "Evito ciertos lugares, situaciones o personas desde el delito.",
    "Desde el delito necesito compañía para la mayoría de actividades que antes hacía de manera autónoma.",
    "A menudo pienso en acciones específicas que podría haber tomado para evitar convertirme en víctima.",
    "Evito asistir a reuniones sociales o eventos públicos que antes disfrutaba.",
    "Me culpo a mí mismo/a por lo que ocurrió.",
    "He cambiado la forma en la que me relaciono con los demás.",
    "Creo que cualquier persona puede ser víctima de un delito y no se puede evitar.",
    "Siento ansiedad cuando pienso en cómo podría haber prevenido el delito.",
    "Creo que podría haber evitado el delito si hubiera actuado de manera diferente.",
    "Desde el delito tengo más dificultades para realizar mis tareas cotidianas de manera eficiente.",
    "Siento una desconexión emocional que me impide sentir emociones intensas.",
    "Me siento responsable por no haber anticipado el delito.",
    "Frecuentemente verifico posibles amenazas en mi entorno.",
    "Creo que mis decisiones o acciones contribuyeron a convertirme en víctima.",
]
ITEMS = {f"fcd_{i:02d}": s for i, s in enumerate(STEMS, 1)}
ALLOWED = {1, 2, 3, 4, 5}
YESNO = {"Sí": "yes", "No": "no"}


def age(v):
    v = str(v).strip()
    return int(v) if v.isdigit() and 1 <= int(v) <= 99 else pd.NA


def main():
    r = requests.get(DATA_URL, headers=UA, timeout=300)
    r.raise_for_status()
    d = pd.read_csv(io.BytesIO(r.content), encoding="utf-8")
    assert d.shape == (217, 76), d.shape
    cols = list(d.columns)
    # the 25 statements sit at columns 11..35, in this order
    assert cols[11:36] == STEMS
    d = d.rename(columns={s: k for k, s in ITEMS.items()})
    d["id"] = range(1, len(d) + 1)
    d["cov_direct_victim"] = d[cols[0]].map(YESNO)
    assert d["cov_direct_victim"].notna().all()
    d["cov_reported"] = d[cols[4]].map(YESNO)
    d["cov_age_at_crime"] = d[cols[3]].map(age).astype("Int64")
    covs = ["cov_direct_victim", "cov_reported", "cov_age_at_crime"]
    long = d.melt(id_vars=["id"] + covs, value_vars=list(ITEMS),
                  var_name="item", value_name="resp").dropna(subset=["resp"])
    long["resp"] = long["resp"].astype(int)
    assert not set(long["resp"]) - ALLOWED
    long = long[["id", "item", "resp"] + covs]
    long = long.sort_values(["id", "item"]).reset_index(drop=True)
    assert not long.duplicated(["id", "item"]).any()
    checks = run_qc(long, permitted_values={c: ALLOWED for c in ITEMS})
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"[warn] {c.name}: {c.detail[:130]}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{TABLE}.csv").write_text(long.to_csv(index=False))
    print(f"[write] {TABLE}: {len(long)} responses, "
          f"{long['id'].nunique()} ids x {long['item'].nunique()} items")


if __name__ == "__main__":
    main()
