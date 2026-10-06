#!/usr/bin/env python3
# Source: https://zenodo.org/records/15328068
# DOI: 10.5281/zenodo.15328068 (dataset; no paper DOI found)
#   Morales, Juan & Eguia, Cesar A. (2025). "Alfabetizacion en eSalud en usuarios de
#   servicios de salud: Construccion y validacion de un instrumento de medicion"
#   [data set, "Base de datos para el AFE de Alfabetizacion en eSalud (eHealth-Much)"],
#   Zenodo.
# Data: "alfabetizacion en eSalud. eHealth-Much.xlsx": sheet "Respuestas de
#       formulario 1" (1068 health-service users x ID + Q1-Q21) and sheet "Leyenda"
#       (the 21 Spanish item stems q1-q21 and the five response options).
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped. Levels checked: xlsx, no variable/value labels; the
#   deposit's "Leyenda" sheet ties every code q1-q21 to its Spanish (administered)
#   stem and gives the 1-5 option labels, so it is cheap (data_labels +
#   study_materials) -- left for a later pass because the English `_translated`
#   column would be IRW-generated (an issues-page entry).
#
# Shipped: morales_2025_ehealth_much -- Q1-Q21, 1 = Totalmente en desacuerdo ..
#   5 = Totalmente de acuerdo. Q8 ("my health actions are based only on social
#   media information") is negatively keyed; not reversed.
# Sample: Peruvian health-service users (Spanish administration); no covariates
#   in the deposit.

import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_DIR = REPO_ROOT / "automated_finding" / "runs" / "raw" / "morales_2025"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}
URL = ("https://zenodo.org/api/records/15328068/files/"
       "alfabetizaci%C3%B3n%20en%20eSalud.%20eHealth-Much.xlsx/content")
NAME = "morales_2025_ehealth_much"


def fetch() -> Path:
    p = RAW_DIR / "data.xlsx"
    if not p.exists():
        r = requests.get(URL, headers=UA, timeout=300)
        r.raise_for_status()
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def main() -> None:
    d = pd.read_excel(fetch(), sheet_name="Respuestas de formulario 1")
    items = [f"Q{i}" for i in range(1, 22)]
    assert d.columns.tolist() == ["ID"] + items and d.shape == (1068, 22)
    assert d["ID"].is_unique
    t = d.rename(columns={"ID": "id"}).melt(id_vars=["id"], var_name="item", value_name="resp")
    assert t["resp"].isin(range(1, 6)).all()
    t["resp"] = t["resp"].astype(int)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    pv = {i: {1, 2, 3, 4, 5} for i in items}
    checks = run_qc(t, permitted_values=pv)
    fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
    assert not fails, fails
    for c in checks:
        if c.status == "warn":
            print(f"    [qc warn] {c.name}: {c.detail[:200]}")
    report = irw_validate.validate_frame(t, label=NAME, profile="upload",
                                         context={"permitted_values": pv})
    assert report.conforms and not report.errors, [(f.check, f.message) for f in report.errors]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT_DIR / f"{NAME}.csv", index=False)
    print(f"{NAME}.csv: rows={len(t)} ids={t['id'].nunique()} "
          f"items={t['item'].nunique()} resp={t['resp'].min()}-{t['resp'].max()}")


if __name__ == "__main__":
    main()
