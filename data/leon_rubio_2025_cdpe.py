#!/usr/bin/env python3
# Source: https://zenodo.org/records/17899509
# DOI: 10.5281/zenodo.17899509 (dataset; no paper DOI)
#   Leon-Rubio, J. M., & Leon-Perez, J. M. (2025). "Professional burnout in nursing:
#   Organizational background, dispositional and mediating factors, and
#   consequences" [data set], Zenodo. Instrument: Moreno Jimenez, Garrosa Hernandez
#   & Gonzalez Gutierrez (2000), Cuestionario de Desgaste Profesional de Enfermeria
#   (CDPE), Archivos de Prevencion de Riesgos Laborales 3(1), 18-28.
# Data: CDPE_DATOS.csv (semicolon-delimited): 648 Spanish nurses x 192 columns (ID,
#       17 sociodemographic/work variables, CDPE1-CDPE174). Also in the deposit:
#       README_CDPE_dataset.pdf, CDPE_CODEBOOK.pdf (SPSS codebook export: value
#       labels for every column; CDPE items 1 = totalmente en desacuerdo ..
#       4 = totalmente de acuerdo; 999 = no responde, 998 = no procede),
#       CDPE_CUESTIONARIO.pdf (the full Spanish questionnaire, items numbered 1-174,
#       followed by the scoring key and the factor structure), CDPE_ESTRUCTURA.pdf,
#       CDPE_CLAVES DE CORRECCION.pdf.
# License: CC BY-NC 4.0 (Zenodo record and README).
#
# Item text: shipped -- Spanish stems from CDPE_CUESTIONARIO.pdf (CDPEk = questionnaire
#   item k; the codebook's item label is "Conforme a la redaccion del item original"),
#   anchors from the codebook, English translation IRW-generated
#   (automated_finding/itemtext_verification/make_itemtext_leon_rubio_2025.py).
#
# Tables, one per conceptual block of the CDPE (block ranges from the scoring key,
#   whose item numbers match the questionnaire's):
#   leon_rubio_2025_cdpe_antecedents   CDPE1-62    organisational antecedents
#   leon_rubio_2025_cdpe_burnout       CDPE63-91   burnout (exhaustion,
#                                                  depersonalisation, lack of
#                                                  personal accomplishment)
#   leon_rubio_2025_cdpe_hardiness     CDPE92-112  hardy personality
#   leon_rubio_2025_cdpe_coping        CDPE113-123 coping
#   leon_rubio_2025_cdpe_consequences  CDPE124-174 psychological, organisational,
#                                                  socio-family and physical
#   All 1-4. itemcov_subscale = the key's subscale (Spanish name). The key has two
#   typos, fixed here by matching its item wording to the questionnaire: the first
#   "45" under Sobrecarga is item 46, and "176" under Consecuencias psicologicas is
#   item 156.
# Reverse-keyed items: the codebook says reversed items are "ya invertidos" in the
#   file, but the six items the key marks (I) (4, 6, 13, 18, 39, 56) all correlate
#   NEGATIVELY with their subscale siblings (e.g. 56 "tasks are well planned" vs 35
#   "orders are vague and ambiguous": r = -0.43), i.e. they are stored as worded.
#   Shipped as stored; nothing reversed here.
# Header "CDPE03" is item 93 (the only item header out of sequence) -> CDPE93.
# Missing: 999 (237 item cells) and 998 dropped.
# Covariates: the codebook's numeric codes (labels in CDPE_CODEBOOK.pdf); 999/998 ->
#   missing; exprofes/expcateg (years of experience) use a decimal comma.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "leon_rubio_2025"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/17899509/files/CDPE_DATOS.csv/content"

# scoring key (CDPE_CLAVES DE CORRECCION.pdf), typos fixed as described above
KEY = {
    "Interaccion conflictiva": [48, 47, 28, 52, 27, 2, 26, 51, 55, 8, 22, 1],
    "Sobrecarga": [54, 53, 15, 21, 50, 20, 34, 62, 49, 46, 16, 17, 41, 45, 42],
    "Contacto con la muerte y el dolor": [37, 58, 32, 57, 29, 31, 43, 30],
    "Ambiguedad de rol": [35, 36, 56, 33, 18, 5],
    "Monotonia de la tarea": [59, 9, 7, 60],
    "Falta de cohesion": [12, 19, 4, 40, 13, 3],
    "Supervision": [24, 10, 11, 6, 25, 39, 23, 61, 38, 14, 44],
    "Agotamiento emocional": [79, 89, 80, 82, 83, 66, 78, 69, 67, 72, 88, 71],
    "Despersonalizacion": [74, 76, 73, 65, 84, 81, 90, 70, 86, 77, 75, 68],
    "Falta de realizacion personal": [91, 85, 87, 63, 64],
    "Compromiso": [104, 95, 99, 94, 96, 105, 103, 98],
    "Reto": [100, 109, 101, 108, 112, 93, 92],
    "Control": [106, 102, 97, 110, 107, 111],
    "Busqueda de apoyo social": [120, 117, 121],
    "Afrontamiento directo": [116, 113, 115, 118],
    "Evitacion": [122, 123, 119, 114],
    "Consecuencias psicologicas": [160, 151, 157, 164, 165, 169, 171, 156, 168, 155,
                                   152, 159, 161, 166, 167, 162, 172, 170, 154, 174,
                                   173, 153, 163],
    "Consecuencias organizacionales": [138, 129, 136, 133, 137, 124, 128, 132, 131,
                                       139, 134, 125, 130],
    "Consecuencias socio-familiares": [141, 135, 127, 140, 126],
    "Consecuencias fisicas": [150, 149, 143, 142, 145, 148, 146, 144, 158, 147],
}
BLOCKS = {
    "leon_rubio_2025_cdpe_antecedents": range(1, 63),
    "leon_rubio_2025_cdpe_burnout": range(63, 92),
    "leon_rubio_2025_cdpe_hardiness": range(92, 113),
    "leon_rubio_2025_cdpe_coping": range(113, 124),
    "leon_rubio_2025_cdpe_consequences": range(124, 175),
}
COVS = {"sexo": "cov_sex", "edad": "cov_age", "relación": "cov_relationship",
        "hijos": "cov_n_children", "estudios": "cov_education",
        "especial": "cov_nursing_specialty", "cual": "cov_which_specialty",
        "otraform": "cov_other_training", "exprofes": "cov_years_experience",
        "categori": "cov_job_category", "expcateg": "cov_years_in_category",
        "situació": "cov_employment_status", "servicio": "cov_service",
        "horario": "cov_shift", "pacientes": "cov_patients_per_day",
        "horas": "cov_hours_per_week", "porcenta": "cov_pct_time_with_patients"}


def fetch() -> Path:
    p = RAW_DIR / "CDPE_DATOS.csv"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_csv(fetch(), sep=";", encoding="utf-8-sig", decimal=",")
    assert d.shape == (648, 192), d.shape
    d = d.rename(columns={"CDPE03": "CDPE93"})
    items = [f"CDPE{i}" for i in range(1, 175)]
    assert set(d.columns) == {"ID"} | set(COVS) | set(items)
    sub = {f"CDPE{i}": s for s, its in KEY.items() for i in its}
    assert sorted(int(k[4:]) for k in sub) == list(range(1, 175))  # key covers 1-174 once
    for s, its in KEY.items():  # every subscale sits inside one block
        assert sum(set(its) <= set(r) for r in BLOCKS.values()) == 1, s
    assert d["ID"].is_unique
    d = d.rename(columns={"ID": "id", **COVS})
    covs = list(COVS.values())
    for c in covs:
        d[c] = pd.to_numeric(d[c], errors="raise")
        d.loc[d[c].isin([998, 999]), c] = pd.NA
    names = list(BLOCKS)
    assert len(set(names)) == len(names)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, rng in BLOCKS.items():
        its = [f"CDPE{i}" for i in rng]
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item", value_name="resp")
        n_miss = t["resp"].isin([998, 999]).sum()
        t = t[~t["resp"].isin([998, 999])].dropna(subset=["resp"])
        assert t["resp"].isin(range(1, 5)).all(), name
        t["resp"] = t["resp"].astype(int)
        t["itemcov_subscale"] = t["item"].map(sub)
        t = t[["id", "item", "resp"] + covs + ["itemcov_subscale"]]
        t = t.sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: set(range(1, 5)) for i in its}
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv})
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min()}-{t['resp'].max()} (dropped {n_miss} 998/999)")


if __name__ == "__main__":
    main()
