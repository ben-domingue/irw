#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/CQJGFH (Harvard Dataverse)
# Munoz-Troncoso, F., Halberstadt, A., Cuadrado-Gordillo, I., Riquelme-Mella, E., et al. (2024). Data of: Validation of
#   the questionnaire to measure Chilean Teachers' Perception of School Violence and Coexistence Management (VI+GEC)
#   [Data set]. Harvard Dataverse.
# Data: bbdd.tab, original format bbdd.sav (1,072 Chilean school teachers, age 22-76). scales_items.pdf (same deposit)
#   lists the 21 item wordings in Spanish against the variable names.
# Table: munoztroncoso_2024_vi_gec  21 items, one questionnaire (VI+GEC), 1-6. The SPSS value labels document the scale:
#   1 Nunca, 2 Casi nunca, 3 Algunas veces, 4 Varias veces, 5 Casi siempre, 6 Siempre.
#   VEE01-10 (5) student-on-student violence, VPE01-07 (6) teacher-on-student violence, VEP01-05 (4) student-on-teacher
#   violence, GCE01-09 (6) school management of coexistence. Prefixes and wording are in scales_items.pdf. The two
#   blocks are one published questionnaire and the management block (6 items) is under the 8-item floor on its own, so
#   they are kept in one table.
# Direction: items are kept as administered. The violence items correlate positively with each other (0.2-0.8) and
#   negatively (-0.1 to -0.3) with the management items, as the wording implies; nothing is flipped.
# Covariates: cov_gender (1 female, 2 male; labels from the SPSS file, no other code occurs), cov_age (years),
#   cov_years_service (SERV; the sentinel -9 is set to missing), cov_school_level (1 pre-basic, 2 basic, 3 secondary),
#   cov_school_zone (1 urban, 2 rural). School name and region are not shipped.
# License: CC BY 4.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none. ID is a 9-digit respondent id; id is the row index.
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_L_2026-10-16"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, saveas: str, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset (original format) and save it as `saveas`."""
    p = raw_dir / saveas
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        time.sleep(4)
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"] if f["label"] == fname][0]
        r = requests.get(f"https://{host}/api/access/datafile/{fid}", params={"format": "original"}, headers=UA, timeout=600)
        r.raise_for_status()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
        time.sleep(4)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values). QC, validate, write."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert len(name) <= 40, name
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any(), name
        assert t["id"].nunique() >= 100 and 8 <= t["item"].nunique() <= 700, name
        checks = run_qc(t, permitted_values=pv)
        fails = [(c.name, c.detail) for c in checks if c.status == "fail"]
        assert not fails, (name, fails)
        for c in checks:
            if c.status == "warn":
                print(f"    [qc warn] {name} {c.name}: {c.detail[:200]}")
        report = irw_validate.validate_frame(t, label=name, profile="upload", context={"permitted_values": pv})
        assert report.conforms and not report.errors, (name, [(f.check, f.message) for f in report.errors])
        for f in report.warnings:
            print(f"    [validate warn] {name} {f.check}: {f.message[:160]}")
        t.to_csv(OUT_DIR / f"{name}.csv", index=False, float_format="%.10g")
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


def main() -> None:
    p = dv_fetch("10.7910/DVN/CQJGFH", "bbdd.tab", RAW_ROOT / "cqjgfh", "bbdd.sav")
    d, meta = pyreadstat.read_sav(str(p))
    assert d.shape == (1072, 34) and d["ID"].is_unique
    items = [c for c in d.columns if c[:3] in ("VEE", "VPE", "VEP", "GCE")]
    assert len(items) == 21
    assert d[items].notna().all().all() and d[items].stack().isin([1, 2, 3, 4, 5, 6]).all()
    assert meta.variable_value_labels["VEE01"][6.0] == "Siempre"
    d = d.reset_index(drop=True)
    d["id"] = range(1, len(d) + 1)
    assert set(d["GENE"].unique()) <= {1.0, 2.0}
    d["cov_gender"] = d["GENE"].astype(int)
    d["cov_age"] = d["EDAD"].astype(int)
    d["cov_years_service"] = d["SERV"].where(d["SERV"] != -9).astype("Int64")
    assert (d["cov_years_service"].dropna() >= 0).all()
    d["cov_school_level"] = d["NIVEL"].astype(int)
    d["cov_school_zone"] = d["ZONA"].astype(int)
    covs = ["cov_gender", "cov_age", "cov_years_service", "cov_school_level", "cov_school_zone"]
    cc = d[items].corr().to_numpy()
    viol = [i for i, c in enumerate(items) if c[:3] != "GCE"]
    assert (cc[np.ix_(viol, viol)] > 0).all() and (cc[np.ix_(viol, [i for i in range(21) if i not in viol])] < 0).all()
    t = d.melt(id_vars=["id"] + covs, value_vars=items, var_name="item", value_name="resp")
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=items, ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    emit({"munoztroncoso_2024_vi_gec": (t[["id", "item", "resp"] + covs], {c: {1, 2, 3, 4, 5, 6} for c in items})})


if __name__ == "__main__":
    main()
