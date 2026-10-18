#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/71JL1U (Harvard Dataverse)
# DOI: 10.7910/DVN/71JL1U (dataset, 2020; Mesaric, Jasna; Simic, Diana; Katic, Milica; Tveter Deilkas, Ellen Catharina;
#   Hofoss, Dag; Bondevik, Gunnar Tschudi). Safety Attitudes Questionnaire - Ambulatory Version (SAQ-AV), 185 health
#   professionals in out-of-hours primary care services in Croatia, collected 2015-06-29 to 2015-09-01.
# Data: SAQ.tab (one row per respondent, SAQ1..SAQ62, 1 = disagree strongly .. 5 = agree strongly) and
#   SAQ_codebook.tab (item wording). Blank cells are missing (not applicable / skipped) and are dropped.
# Raw responses are shipped as stored. The questionnaire mixes positively and negatively worded items (e.g. SAQ12,
#   SAQ24); they are NOT recoded (datastandard.md). Item wording is in the codebook, not shipped here.
# Table: mesaric_2020_saq_primary_care, 62 items, 1-5.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-16).
# PII: none. The file has no identifier column; id is the 1..N row index. No covariates in the deposit.
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

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_F_2026-10-16"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) IRW-lead-check"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset (ingested tab)."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        time.sleep(4)
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"] if f["dataFile"]["filename"] == fname][0]
        r = requests.get(f"https://{host}/api/access/datafile/{fid}", headers=UA, timeout=600)
        r.raise_for_status()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
        time.sleep(4)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values). QC, validate, write."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert max(map(len, tables)) <= 40, name
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any(), name
        assert t["id"].nunique() >= 100 and t["item"].nunique() >= 8, name
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
        t.to_csv(OUT_DIR / f"{name}.csv", index=False)
        print(f"{name}.csv: rows={len(t)} ids={t['id'].nunique()} items={t['item'].nunique()} "
              f"resp={t['resp'].min():g}-{t['resp'].max():g}")


def main() -> None:
    p = dv_fetch("10.7910/DVN/71JL1U", "SAQ.tab", RAW_ROOT / "71jl1u")
    d = pd.read_csv(p, sep="\t")
    cols = [f"SAQ{i}" for i in range(1, 63)]
    assert list(d.columns) == cols and len(d) == 185
    d = d.reset_index(drop=True)
    d["id"] = range(1, len(d) + 1)
    t = d.melt(id_vars=["id"], value_vars=cols, var_name="item", value_name="resp")
    t = t[t["resp"].notna()]
    assert (t["resp"] % 1 == 0).all() and t["resp"].between(1, 5).all(), sorted(t["resp"].unique())
    t["resp"] = t["resp"].astype(int)
    t["item"] = pd.Categorical(t["item"].str.lower(), categories=[c.lower() for c in cols], ordered=True)
    t = t.sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    emit({"mesaric_2020_saq_primary_care": (t, {c.lower(): {1, 2, 3, 4, 5} for c in cols})})


if __name__ == "__main__":
    main()
