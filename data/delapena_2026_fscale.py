#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/WM7IXF (Harvard Dataverse)
# "Base de datos de las encuestas nacionales sobre personalidad autoritaria de los mexicanos (2021-2024)" [Data set],
#   de la Pena, Ricardo, deposited 2026-08-18; supplement to "Sobre la personalidad autoritaria de los mexicanos (2021-2024)"
#   (preliminary version under review, Revista Mexicana de Opinion Publica). Year 2026 = deposit / manuscript year.
# Data: ISMXPA2124p.tab (format=original -> ISMXPA2124p.sav): two independent national household surveys of Mexico
#   (round 0 = Aug 2021, N=1080; round 1 = Sep 2024, N=1070), 61 columns.
# Tables:
#   delapena_2026_fscale   30 F-scale (authoritarian personality) statements F01-F30, six agreement categories. The .sav
#                          stores them as 0, .2, .4, .6, .8, 1 with value labels (0 'Totalmente en desacuerdo' ... 1
#                          'Totalmente de acuerdo'); shipped as 0-5 (= value * 5). Higher = more agreement. No item is
#                          reverse-coded (the deposit's own F, puntaje and grupo columns are the plain mean/sum of the 30
#                          columns, asserted below). Derived F, puntaje, grupo and the weights are not shipped.
# Minors: the 2021 round samples ages 15+ with a '15 a 20' band that cannot be split at 18, so that band (153 rows) is
#   dropped; the 2024 round is 18+.
# id: the deposit's folio is an interview number repeated across rounds; id is the row index of the shipped rows.
#   The rounds are independent cross-sections, so the round is cov_year, not wave.
# Covariates: cov_year, cov_sex, cov_age_band (the round-specific cohort bands, labelled), cov_education, cov_region.
#   Electoral section, state, interview dates/times and the party/ideology items are not shipped.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-17).
# PII: none shipped.
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

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_W_2026-10-17"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, saveas: str, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset by its label or original name, in original format."""
    p = raw_dir / saveas
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        time.sleep(4)
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if fname in (f["label"], f["dataFile"].get("originalFileName"))][0]
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
    p = dv_fetch("10.7910/DVN/WM7IXF", "ISMXPA2124p.tab", RAW_ROOT, "wm7ixf.sav")
    d, meta = pyreadstat.read_sav(str(p))
    assert d.shape == (2150, 61), d.shape
    F = [f"F{i:02d}" for i in range(1, 31)]
    assert d[F].notna().all().all()
    lab = meta.variable_value_labels["F01"]
    assert lab[0.0].startswith("Totalmente en") and "desacuerdo" in lab[0.0] and lab[1.0].startswith("Totalmente de acuerdo")
    x = (d[F] * 5).round()
    assert ((d[F] * 5 - x).abs() < 1e-9).all().all() and x.stack().isin(range(6)).all()
    assert (d[F].mean(axis=1) - d["F"]).abs().max() < 1e-9 and (d[F].sum(axis=1) - d["puntaje"]).abs().max() < 1e-9
    keep = ~((d["ronda"] == 0) & (d["edad"] == 1))  # '15 a 20 anos' band includes minors
    assert (~keep).sum() == 153
    d, x = d[keep].reset_index(drop=True), x[keep].reset_index(drop=True)
    assert d.loc[d["ronda"] == 1, "edad"].isin([11, 12, 13, 14, 15]).all()
    names = [f"fscale_{i}" for i in range(1, 31)]
    sub = pd.DataFrame({"id": np.arange(1, len(d) + 1),
                        "cov_year": d["ronda"].map({0.0: 2021, 1.0: 2024}),
                        "cov_sex": d["sexo"].map({1.0: "male", 2.0: "female"}),
                        "cov_age_band": d["edad"].map(meta.variable_value_labels["edad"]),
                        "cov_education": d["D01"].map({1.0: "primary or less", 2.0: "lower secondary",
                                                       3.0: "upper secondary", 4.0: "tertiary"}),
                        "cov_region": d["region"].map(meta.variable_value_labels["region"])})
    sub[names] = x.values
    cov = ["cov_year", "cov_sex", "cov_age_band", "cov_education", "cov_region"]
    t = sub.melt(id_vars=["id"] + cov, value_vars=names, var_name="item", value_name="resp")
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=names, ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    t = t[["id", "item", "resp"] + cov]
    c = x.corr().values
    print(f"    [note] inter-item r: min {c.min():.2f} mean {c.mean():.2f}")
    emit({"delapena_2026_fscale": (t, {n: set(range(6)) for n in names})})


if __name__ == "__main__":
    main()
