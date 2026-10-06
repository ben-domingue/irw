#!/usr/bin/env python3
# Source: https://zenodo.org/records/20418454
# DOI: 10.5281/zenodo.20418454 (dataset; no paper DOI found)
#   Cordova Ruelas, Jakeline (2026). "Carga de trabajo, autoeficacia profesional y
#   bienestar en suboficiales de la Policia Nacional del Peru" [data set], Zenodo.
# Data: "DATOS PNP (2).xlsx": sheet Hoja1 (250 non-commissioned officers of the
#       Peruvian National Police x 28 columns, header on row 2, block titles on
#       row 1: DATOS SOCIODEMOGRAFICOS / BIENESTAR GENERAL (WHO-5 WBI) / CARGA DE
#       TRABAJO / AUTOEFICACIA); sheet Hoja2 is the codebook (category labels for
#       the demographics and the three response scales).
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. Levels checked: xlsx, no variable labels; Hoja2 gives
#   the response-option labels for each block but no item stems.
#
# Tables (Hoja2 anchors):
#   cordova_2026_who5           BG1-5   0-3  Nunca / A veces / Muchas veces / Siempre
#                                            (a 4-point WHO-5 adaptation, not the 0-5 original)
#   cordova_2026_workload       CT1-6   0-4  Nunca / Raramente / A veces / Frecuentemente /
#                                            Muy frecuentemente
#   cordova_2026_self_efficacy  A1-10   0-6  Nunca .. seguramente (7 options)
# One missing A4 dropped.
# Covariates (Hoja2): sexo 1 female 2 male; estado civil 1 single 2 cohabiting
#   3 married 4 divorced 5 widowed; grado policial 1 SS 2 SB 3 ST1 4 ST2 5 ST3 6 S1
#   7 S2 8 S3; unidad 1 Comisaria Juliaca 2 USE 3 Comisaria SB (4 emergencia unused);
#   edad and anos de servicio as reported.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "cordova_2026"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = "https://zenodo.org/api/records/20418454/files/DATOS%20PNP%20(2).xlsx/content"

TABLES = {
    "cordova_2026_who5": ([f"BG{i}" for i in range(1, 6)], range(0, 4)),
    "cordova_2026_workload": ([f"CT{i}" for i in range(1, 7)], range(0, 5)),
    "cordova_2026_self_efficacy": ([f"A{i}" for i in range(1, 11)], range(0, 7)),
}
COVS = {"edad": "cov_age", "sexo": "cov_sex", "estado civil": "cov_marital_status",
        "grado policial": "cov_rank", "años de servicio": "cov_years_service",
        "unidad de servicio": "cov_unit"}


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="Hoja1", header=1)
    d.columns = [str(c).strip() for c in d.columns]
    assert d.shape == (250, 28), d.shape
    items = [c for its, _ in TABLES.values() for c in its]
    assert set(d.columns) == {"partcipante"} | set(items) | set(COVS), set(d.columns)
    assert d["partcipante"].is_unique
    d = d.rename(columns={"partcipante": "id", **COVS})
    covs = list(COVS.values())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (its, rng) in TABLES.items():
        t = d.melt(id_vars=["id"] + covs, value_vars=its, var_name="item",
                   value_name="resp").dropna(subset=["resp"])
        assert t["resp"].isin(list(rng)).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
        assert not t.duplicated(["id", "item"]).any() and t["id"].nunique() >= 100
        pv = {i: set(rng) for i in its}
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
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
