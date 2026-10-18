#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/AW7YNA (Harvard Dataverse)
# Espinoza, F. Mental Well-being and tourism experience DASS21 [Data set]. Harvard Dataverse, deposited 2024-11-10.
#   University of Cuenca (Ecuador). Survey of university students at two Ecuadorian universities. The deposit cites only
#   "peer review paper" (no DOI), so the year 2024 is the deposit year, not a confirmed publication year.
# Data: BASE_1 BIENESTAR.xlsx, sheet 'first time' (214 rows, 77 columns). Sheet 'Second and third time' (57 rows, headers V1..V75
#   unlabelled, no id linking to the first sheet) is not shipped.
# Tables:
#   espinoza_2024_dass21   DASS-21, 21 items (DASS1..DASS21), 0-3, first administration (before the tourism experience).
#                          Direction: the deposit has no codebook, but its TOTAL_SUM_DASS column equals 2 * sum of the 21 raw items
#                          for every row (asserted below) and the deposit labels the sums with severity bands (Normal ... Extremadamente
#                          Severo), so higher = more symptoms, unreversed. That is the deposit's own scoring.
# Not shipped: totals/severity columns (derived), second/third administrations, ENC_1..10 (undocumented), gender (codes 1/2/3 not
#   labelled in the deposit), health/work/COVID flags.
# id: the deposit has no participant id; id is the row index of the sheet (1..214).
# Covariates: cov_age (18-39, adults only), cov_semester (university semester, 0-11).
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-17).
# PII: none (age, semester only).
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_Q_2026-10-17"
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
    p = dv_fetch("10.7910/DVN/AW7YNA", "BASE_1 BIENESTAR.xlsx", RAW_ROOT / "aw7yna", "BASE_1 BIENESTAR.xlsx")
    d = pd.read_excel(p, sheet_name="first time")
    assert d.shape == (214, 77), d.shape
    src = [f"DASS{i}" for i in range(1, 22)]
    names = [f"dass21_{i}" for i in range(1, 22)]
    assert d[src].notna().all().all() and d[src].stack().isin([0, 1, 2, 3]).all()
    assert ((d[src].sum(axis=1) * 2) == d["TOTAL_SUM_DASS"]).all(), "deposit total is not 2 * sum of items"
    assert d["AGE"].min() >= 18
    corr = d[src].corr().values
    assert (corr[~(corr == 1)] > 0).all(), "negative inter-item correlation: check keying"
    sub = pd.DataFrame({"id": range(1, len(d) + 1), "cov_age": d["AGE"], "cov_semester": d["COD_SEMES"]})
    sub[names] = d[src].values
    t = sub.melt(id_vars=["id", "cov_age", "cov_semester"], value_vars=names, var_name="item", value_name="resp")
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=names, ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    t = t[["id", "item", "resp", "cov_age", "cov_semester"]]
    emit({"espinoza_2024_dass21": (t, {n: {0, 1, 2, 3} for n in names})})


if __name__ == "__main__":
    main()
