#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/UBRRHG (Harvard Dataverse)
# Stiglic, G. et al. Replication Data for: Validation of the Warwick-Edinburgh Mental Well-being Scale (WEMWBS) among
#   university student population in Slovenia [Data set]. Harvard Dataverse.
# Data: db_wemwbs_slo.tab, original format .sav (470 Slovenian university students, 45 columns), plus WEMWBS SLO.R.
# Tables:
#   stiglic_2019_wemwbs   WEMWBS, 14 items (WEMWBSa..n), 1-5. Value labels in the .sav are bare digits ('1'..'5'), so the
#                         anchors are not documented in the deposit; direction is documented by the deposit's R script,
#                         which sums all 14 items unreversed into WEMWBS_total (high = more well-being).
# Not shipped: the 8 psychosomatic symptom items (the R script reverses them with 6 - x but the anchors are not labelled,
#   so direction is not documented), general health, internet-use hours, free-text purpose, WEMWBS_total (derived).
# Reverse keying: none. All 14 items correlate positively (asserted below).
# id: the deposit has no participant id; id is the row index of the file (1..470).
# Covariates: cov_gender (labelled 1 = female, 2 = male; labels agree with the data), cov_age (18-49), cov_faculty (labelled).
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-17).
# PII: none (gender, age, faculty only; study programme / institution code columns are not shipped).
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

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_P_2026-10-17"
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
    p = dv_fetch("10.7910/DVN/UBRRHG", "db_wemwbs_slo.sav", RAW_ROOT, "ubrrhg.sav")
    d, _ = pyreadstat.read_sav(str(p))
    assert d.shape == (470, 45), d.shape
    src = [f"WEMWBS{c}" for c in "abcdefghijklmn"]
    names = [f"wemwbs_{k}" for k in range(1, 15)]
    assert d[src].stack().dropna().isin([1, 2, 3, 4, 5]).all()
    assert d["Age"].dropna().min() >= 18
    corr = d[src].corr().values
    assert (corr[~(corr == 1)] > 0).all(), "negative inter-item correlation: check keying"
    assert set(d["Gender"].dropna().unique()) <= {1.0, 2.0} and set(d["Faculty"].unique()) <= {1.0, 2.0}
    sub = pd.DataFrame({"id": range(1, len(d) + 1),
                        "cov_gender": d["Gender"].map({1.0: "female", 2.0: "male"}),
                        "cov_age": d["Age"],
                        "cov_faculty": d["Faculty"].map({1.0: "Nursing", 2.0: "Electrical Engineering and Computer Science"})})
    sub[names] = d[src].values
    t = sub.melt(id_vars=["id", "cov_gender", "cov_age", "cov_faculty"], value_vars=names, var_name="item", value_name="resp")
    t = t[t["resp"].notna()].copy()
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"], categories=names, ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    t = t[["id", "item", "resp", "cov_gender", "cov_age", "cov_faculty"]]
    emit({"stiglic_2019_wemwbs": (t, {n: {1, 2, 3, 4, 5} for n in names})})


if __name__ == "__main__":
    main()
