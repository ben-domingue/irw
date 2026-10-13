#!/usr/bin/env python3
# Source: https://zenodo.org/records/21383291
# DOI: 10.5281/zenodo.21383291 (dataset; the record names no paper)
#   Rosado Cobos, G. A., & Escobar Moreno, F. (2026). Dataset sobre percepción estudiantil
#   del modelo 5E-STEAM y resultados del Cuestionario ¡EUREKA, EUREKA! de Melo et al. (2026):
#   Ciclos 2025-2026 [Data set]. Zenodo.
# Data: "2026_Dataset_Instrumentos_CuantiCuali.csv.xlsx", sheet "Cualitativos 2025": 115
#       Mexican upper-secondary physics students (three sections) with the eleven items of
#       the ¡EUREKA, EUREKA! questionnaire (Pregunta 1-11, 1-5) and a perception survey
#       (option labels and free text). The two "Cuantitativos" sheets are post-test marks
#       per student, not item responses. The item wording is in the deposit's
#       2026_Documentacion_Validacion_Datos.pdf, not in the sheet.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped -- the sheet headers are positional ("Pregunta 1"); the Spanish
#   wording is in 2026_Documentacion_Validacion_Datos.pdf in the deposit (a PDF read, not a
#   label), and the README GARC.pdf describes the files.
#
# Tables (item = the sheet header with the space removed, pregunta_1 .. pregunta_11):
#   rosado_2026_eureka   11 items, 1-5.
# Skipped: the perception questions (single option-label items and free text), the marks.
# Covariates: cov_section (the deposit's "3° 5" / "3° 11" / "3° 12").
# id: the deposit's Identificador Estudiante (E1 .. E115).

import os
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5281_zenodo.21383291"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
FNAME = "2026_Dataset_Instrumentos_CuantiCuali.csv.xlsx"
URL = "https://zenodo.org/api/records/21383291/files/" + requests.utils.quote(FNAME) + "/content"
T = "rosado_2026_eureka"
ITEMS = {f"Pregunta {k}": f"pregunta_{k}" for k in range(1, 12)}
COVS = ["cov_section"]


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"]).any()
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 2, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload",
                                             context={"permitted_values": pv} if pv else None)
        assert report.conforms and not report.errors, \
            (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} "
              f"items={t['item'].nunique()} resp={t['resp'].min():g}-{t['resp'].max():g}")


def main() -> None:
    d = pd.read_excel(download(URL, RAW_DIR / FNAME), "Cualitativos 2025")
    d.columns = [str(c).strip() for c in d.columns]
    assert len(d) == 115 and d["Identificador Estudiante"].is_unique
    d = d.rename(columns={"Identificador Estudiante": "id", "¿Cuál es tu sección?": "cov_section", **ITEMS})
    t = d.melt(id_vars=["id"] + COVS, value_vars=list(ITEMS.values()), var_name="item",
               value_name="resp").dropna(subset=["resp"])
    assert (t["resp"] % 1 == 0).all()
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 5).all()
    t = t[["id", "item", "resp"] + COVS].sort_values(["id", "item"]).reset_index(drop=True)
    emit({T: (t, {i: set(range(1, 6)) for i in ITEMS.values()})})


if __name__ == "__main__":
    main()
