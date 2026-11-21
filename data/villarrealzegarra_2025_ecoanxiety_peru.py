#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/32810570
# DOI: 10.6084/m9.figshare.32810570 (data)
#   Villarreal-Zegarra D (2025). Validity and reliability of the Hogg Eco-Anxiety Scale and the Eco-Guilt
#   Questionnaire [Data set]. figshare.
# License: CC BY 4.0 (figshare record metadata)
# Data: database.RData (object "copiaa"), 583 Peruvian university students (Lima, 2024-2025; the paper analyses the
#   553 aged 18-30, all rows are kept here). The record describes the Spanish HEAS-13, the Eco-Guilt Questionnaire
#   (EGuiQ-11), GAD-2 and PHQ-2; "Analysis plan.R" in the record fits the HEAS as four factors and the EGuiQ as one.
#   Observed ranges: HEAS and GAD-2/PHQ-2 items 0-3 (the published 0-3 frequency scales), EGuiQ items 1-4. The record
#   gives no anchors for the EGuiQ, so its range is the observed 1-4.
# Tables (item = the file's variable name, e.g. heas_nervioso): _heas (13 items, 0-3), _eguiq (11 items, 1-4), _phq4
#   (gad_nervio, gad_preocupar, phq_triste, phq_placer; GAD-2 + PHQ-2 = the PHQ-4, 0-3). id = the file's Participante.
# Covariates: cov_age (one recorded age of 212 set missing). sexo, carrera and the other 0/1 background codes carry
#   no labels in the file or the analysis script and are not carried.
# Item text: not shipped -- variable names only; the Spanish versions are third-party instruments (register rows
#   needed).
import io
import sys
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
from irw_validate._checks import run_qc  # noqa: E402

OUT = REPO_ROOT / "automated_finding" / "irw_output"
URL = 'https://ndownloader.figshare.com/files/65989940'
N_ROWS = 583
ID_COL = 'Participante'
COVS = {'age_clean': 'cov_age'}
COV_MAPS = {}
RENAME = {}
BLOCKS = {'villarrealzegarra_2025_heas': ['heas_nervioso', 'heas_detener', 'heas_preocupación', 'heas_miedo', 'heas_pensar', 'heas_sucesos', 'heas_perdidas', 'heas_dormir', 'heas_familia', 'heas_trabajo', 'heas_comportamiento', 'heas_resolver', 'heas_angustia'], 'villarrealzegarra_2025_eguiq': ['egui_negativo', 'egui_repercusion', 'egui_culpa', 'egui_estilo', 'egui_hipo', 'egui_atencion', 'egui_causa', 'egui_enfado', 'egui_incomoda', 'egui_necesidad', 'egui_actividad'], 'villarrealzegarra_2025_phq4': ['gad_nervio', 'gad_preocupar', 'phq_triste', 'phq_placer']}
LO, HI = 0, 4
DROP_COLS = []


def load(content):
    import os, tempfile
    import pyreadr
    with tempfile.NamedTemporaryFile(suffix=".RData", delete=False) as f:
        f.write(content)
    try:
        objs = pyreadr.read_r(f.name)
    finally:
        os.unlink(f.name)
    assert list(objs) == ["copiaa"]
    return objs["copiaa"]


def keep_rows(d):
    # One recorded age of 212 is a typo and is set missing. The paper keeps ages 18-30; all rows are kept here.
    d["age_clean"] = d["edad"].where(d["edad"] < 100)
    assert (d["edad"] >= 100).sum() == 1
    for c in BLOCKS["villarrealzegarra_2025_heas"] + BLOCKS["villarrealzegarra_2025_phq4"]:
        assert d[c].dropna().between(0, 3).all(), c
    for c in BLOCKS["villarrealzegarra_2025_eguiq"]:
        assert d[c].dropna().between(1, 4).all(), c
    return d


def main():
    r = requests.get(URL, timeout=180, headers={"User-Agent": "irw-pipeline/1.0"})
    r.raise_for_status()
    d = load(r.content)
    d.columns = [str(c).strip() for c in d.columns]
    d = d.rename(columns=RENAME)
    assert len(d) == N_ROWS, len(d)
    d = d.drop(columns=[c for c in DROP_COLS if c in d.columns])
    d = keep_rows(d)
    if ID_COL:
        assert d[ID_COL].is_unique
        d["id"] = d[ID_COL]
    else:
        d["id"] = range(1, len(d) + 1)
    for src, cov in COVS.items():
        d[cov] = d[src].map(COV_MAPS[cov]) if cov in COV_MAPS else d[src]
        if cov in COV_MAPS:
            assert d[cov].notna().sum() == d[src].notna().sum(), cov
    covs = list(COVS.values())
    shipped = set()
    for name, items in BLOCKS.items():
        assert all(c in d for c in items), [c for c in items if c not in d]
        t = d[["id"] + covs + items].melt(id_vars=["id"] + covs, var_name="item", value_name="resp")
        t["resp"] = pd.to_numeric(t["resp"], errors="raise")
        t = t.dropna(subset=["resp"])
        assert t["resp"].between(LO, HI).all() and (t["resp"] % 1 == 0).all(), name
        t["resp"] = t["resp"].astype(int)
        t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"])
        fails = [c for c in run_qc(t, permitted_values=range(LO, HI + 1)) if c.status == "fail"]
        assert not fails, (name, fails)
        assert name not in shipped
        shipped.add(name)
        t.to_csv(OUT / f"{name}.csv", index=False)
        print(name, len(t), t.id.nunique(), t.item.nunique())
    used = set(sum(BLOCKS.values(), [])) | set(COVS) | {ID_COL}
    print("source columns not shipped:", [c for c in d.columns if c not in used and c != "id" and c not in covs])


if __name__ == "__main__":
    main()
