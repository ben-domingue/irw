#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/t3t4z976tp/1
# DOI: 10.1016/j.maturitas.2018.02.010
#   Blumel, J. E., Arteaga, E., Parra, J., Monsalve, C., Reyes, V., Vallejo, M. S., &
#   Chea, R. (2018). Decision-making for the treatment of climacteric symptoms using
#   the Menopause Rating Scale. Maturitas, 111, 15-19.
# Data: Mendeley Data 10.17632/t3t4z976tp.1 (Blumel, Monsalve, Reyes Rios, Chea, Vallejo,
#       Arteaga, Parra; 2018). "Punto Sin Estrog.sav" -- 427 Chilean women aged 40-59 not
#       using hormones or oral contraceptives (the file's own filter_$ selects them; all
#       427 rows are selected) x 50 columns: background, MRS1A-MRS11A (the eleven MRS
#       symptoms, 0-4), MRS1B-MRS11B (a 0/1 per symptom), domain and total sums, and
#       treatment-decision flags.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: not shipped. The .sav variable labels name each symptom in Spanish at the
#   variable-label level (MRS2A "Palpitaciones", MRS3A "Insomnio"; MRS1A "SVM", MRS4A "MOM"
#   are abbreviations); there are no value labels on any item. The MRS wording is the
#   published instrument's (Heinemann et al.), not deposited.
#
# Table:
#   blumel_2018_mrs   MRS1A-MRS11A, 0-4 (none .. very severe), as the MRS scores them.
# Skipped: MRS1B-MRS11B -- a 0/1 per symptom whose sum is the file's TRTotal and which rises
#   with severity (presumably "this symptom warrants / she wants treatment"), but neither
#   the file nor the record says what was asked, so its meaning is unconfirmed.
#   Somato/Psico/Uro/MRSTotal (sums, checked), TRTotal, MalaCV, Tienebuenasalud,
#   RequiereTr, NuevoPuntoCorte (derived flags), filter_$ and the two hormone-use columns
#   (constant), and the sensitive medical-history flags (psychotropics, psychiatric
#   treatment, history of rape, church attendance), which are not needed to use the table.
# Covariates (codes as stored; no value labels in the file): cov_age (Edad), cov_schooling
#   (Anosdeestudio, years), cov_care_type (Tipodeatenciondesalud, 1/2),
#   cov_stable_partner (0/1), cov_menses (Actualmentesusmenstruacionesson, 1-3),
#   cov_hysterectomy, cov_oophorectomy (0/1), cov_years_amenorrhea (Anossinmenstruar).
# id: row index (the file has no identifier).

import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "m_t3t4z976tp"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://data.mendeley.com/public-files/datasets/t3t4z976tp/files/"
       "81bc143e-cd14-4d83-9183-7a6bef280cd1/file_downloaded")
NAME = "blumel_2018_mrs"
A = [f"MRS{i}A" for i in range(1, 12)]
B = [f"MRS{i}B" for i in range(1, 12)]
COVS = {"Edad": "cov_age", "Añosdeestudio": "cov_schooling",
        "Tipodeatencióndesalud": "cov_care_type", "Tieneparejaestable": "cov_stable_partner",
        "Actualmentesusmenstruacionesson": "cov_menses", "Histerectomía": "cov_hysterectomy",
        "Ooferectomíabilateral": "cov_oophorectomy", "Añossinmenstruar": "cov_years_amenorrhea"}
SKIP = {**{b: "0/1 per symptom, question undocumented" for b in B},
        "Somato": "sum", "Psico": "sum", "Uro": "sum", "MRSTotal": "sum", "TRTotal": "sum of B",
        "MalaCV": "derived flag", "Tienebuenasalud": "derived flag",
        "RequiereTr": "derived flag", "NuevoPuntoCorte": "derived flag",
        "filter_$": "constant filter", "Anticonceptivosorales": "constant 0",
        "Usahormonasparalamenopausia": "constant 0",
        "Dejademenstruarconhisterectomía": "detail of hysterectomy",
        "EnelúltimoañoHatenidorelaciones": "sensitive history, not needed",
        "UsaDIU": "contraception detail", "Usaterapiaalternativa": "treatment detail",
        "Usapsicofármacos": "sensitive history, not needed",
        "Asisteregularmentealaiglesia": "not needed",
        "Haseguidotratamientoconpsiquiatra": "sensitive history, not needed",
        "Antecedentesdeviolación": "sensitive history, not needed"}


def fetch() -> Path:
    p = RAW_DIR / "data.sav"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d, _ = pyreadstat.read_sav(str(fetch()))
    assert d.shape == (427, 50)
    accounted = set(A) | set(COVS) | set(SKIP)
    assert accounted == set(d.columns), set(d.columns) ^ accounted
    for c, why in SKIP.items():
        print(f"  [skip] {c}: {why}")
    assert (d["filter_$"] == 1).all()
    assert (d[A].sum(axis=1) == d["MRSTotal"]).all() and (d[B].sum(axis=1) == d["TRTotal"]).all()
    d = d.reset_index(drop=True)
    d.insert(0, "id", d.index + 1)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        if (d[c].dropna() % 1 == 0).all():
            d[c] = d[c].astype("Int64")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t = d.melt(id_vars=["id"] + covs, value_vars=A, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    assert t["resp"].isin(range(0, 5)).all()
    t["resp"] = t["resp"].astype(int)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    assert set(t["item"]) == set(A) and not t.duplicated(["id", "item"]).any()
    assert t["id"].nunique() >= 100 and len(t) == int(d[A].notna().sum().sum())
    pv = {i: set(range(0, 5)) for i in A}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    for f in report.warnings:
        print(f"    [validate warn] {f.check}: {f.message[:160]}")
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
