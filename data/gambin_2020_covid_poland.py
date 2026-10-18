#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/0NP102 (Harvard Dataverse)
# Gambin, M. (2020). Generalized anxiety and depressive symptoms in various age groups during the COVID-19 lockdown in
#   Poland [Data set]. University of Warsaw, Harvard Dataverse.
# Data: University_of_Warsaw_anxiety_depressive_symptoms_COVID-19_database.tab, original format .sav
#   (1,115 Polish adults aged 18-85, nationally representative online sample, 62 columns incl. derived sums/means).
# Tables:
#   gambin_2020_phq9            PHQ-9, 9 items, 0-3 (Not at all .. Nearly every day), value labels in the .sav.
#   gambin_2020_pandemic_diff   Pandemic-related difficulties, 16 items, 1-4 (1 = not a problem at all .. 4 = definitely a
#                               problem for me), value labels in the .sav.
# Not shipped: GAD-7 (7 items), COVID-19 risk (6), social support (5): each under the 8-item floor. PHQ9_sum, GAD7_sum,
#   the four difficulty subscale scores and the two means are derived columns and are dropped.
# Covariates: cov_age, cov_education (6 labelled levels). Sex is NOT shipped: the .sav labels 1 = woman, 2 = man but the
#   data hold 0/1, so the direction is undocumented.
# Reverse keying: none. PHQ-9 and difficulty items all correlate positively (min r 0.35 and 0.14), and the labels agree
#   with the data, so nothing is flipped.
# id: the deposit's "Id number" (1..1115 study sequence), not a platform participant id.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none (age, education only).
import os
import sys
import time
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_N_2026-10-16"
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


def long(d: pd.DataFrame, items: list, names: list) -> pd.DataFrame:
    sub = d[["id", "cov_age", "cov_education"] + items].copy()
    sub.columns = ["id", "cov_age", "cov_education"] + names
    t = sub.melt(id_vars=["id", "cov_age", "cov_education"], value_vars=names, var_name="item", value_name="resp")
    t = t[t["resp"].notna()].copy()
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=names, ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    return t[["id", "item", "resp", "cov_age", "cov_education"]]


def main() -> None:
    p = dv_fetch("10.7910/DVN/0NP102",
                 "University_of_Warsaw_anxiety_depressive_symptoms_COVID-19_database.sav",
                 RAW_ROOT, "0np102.orig")
    d, _ = pyreadstat.read_sav(str(p))
    assert d.shape == (1115, 62) and d["Id"].is_unique
    d = d.rename(columns={"Id": "id", "Age": "cov_age", "Education": "cov_education"})
    d["id"] = d["id"].astype(int)
    assert d["cov_age"].min() >= 18
    phq = [f"Phq9_{k}" for k in range(1, 10)]
    dif = [f"Pandemic_Difficulties_{k}" for k in range(1, 17)]
    assert d[phq].stack().isin([0, 1, 2, 3]).all() and d[dif].stack().isin([1, 2, 3, 4]).all()
    emit({
        "gambin_2020_phq9": (long(d, phq, [f"phq9_{k}" for k in range(1, 10)]),
                             {f"phq9_{k}": {0, 1, 2, 3} for k in range(1, 10)}),
        "gambin_2020_pandemic_diff": (long(d, dif, [f"diff_{k}" for k in range(1, 17)]),
                                      {f"diff_{k}": {1, 2, 3, 4} for k in range(1, 17)}),
    })


if __name__ == "__main__":
    main()
