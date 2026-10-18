#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/L5D0ST (Harvard Dataverse)
# DOI: 10.7910/DVN/L5D0ST (dataset, 2026; Baysan, Aydan). "Dataset for 'Nursing Students' Attitudes Toward Artificial
#   Intelligence: The Roles of Self-Directed Learning and AI Usage'" -- Turkish nursing students (N = 403).
# Data: dataset.tab (an SPSS file served as original; read with pyreadstat). Two Likert scales, both stored as integer
#   codes 1-5 with SPSS value labels (Turkish):
#     oyobo1-21 (column names oyobo*, written with Turkish characters in the file): self-directed learning, 1 never
#       ... 5 always (hicbir zaman / nadiren / bazen / genellikle / her zaman); 21 items.
#     yzygto1-20: attitude toward artificial intelligence, 1 strongly disagree ... 5 strongly agree for items 1-12 and
#       the REVERSED label set for items 13-20 (code 1 = strongly agree, 5 = strongly disagree), as the SPSS value labels
#       state. Items 13-20 correlate about -0.3 with items 1-12 and about +0.6 with each other, so the data point the same
#       way as the labels. They are flipped (resp = 6 - code) so all 20 items run the same direction.
#   Subscale sums/totals (ozizleme, gudulenme, ozkontrol, ozguven, oyoboToplam, yzygtpozitif, yzygtnegatif) not shipped.
#   Multi-response "purpose of AI use" checkboxes and the empty 'universite' column not shipped.
# License: CC0 1.0 (Dataverse API licence field, checked 2026-10-15).
# PII: none (no names, ids, contact fields). The file has no respondent id; id = row index (1-based).
# Item text: not in the deposit (no questionnaire file).
#
# Tables: baysan_2026_self_directed_learning (21 items, 1-5), baysan_2026_ai_attitudes (20 items, 1-5).
# Covariates: cov_age (years), cov_gender (1 female, 2 male), cov_grade (1-4 year of study),
#   cov_ai_use (1 uses AI tools, 2 does not), cov_ai_frequency (1 daily ... 4 a few times a year, 5 does not use).
import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

RUN_DIR = REPO_ROOT / "automated_finding" / "runs" / "leads_fork_A_2026-10-15"
OUT_DIR = Path(os.environ.get("IRW_OUT_DIR", RUN_DIR / "out"))
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", RUN_DIR / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset in its original format."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"] if f["label"] == fname][0]
        r = requests.get(f"https://{host}/api/access/datafile/{fid}", params={"format": "original"},
                         headers=UA, timeout=300)
        r.raise_for_status()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(r.content)
    return p


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values). QC, validate, write."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert max(map(len, tables)) <= 40, name
        assert not t.duplicated(["id", "item"]).any(), name
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


def long(d: pd.DataFrame, cols: dict, covs: list, valid) -> pd.DataFrame:
    """cols: source column -> item code."""
    t = d.melt(id_vars=["id"] + covs, value_vars=list(cols), var_name="item", value_name="resp")
    t = t.dropna(subset=["resp"])
    t["item"] = t["item"].map(cols)
    assert (t["resp"] % 1 == 0).all()
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].isin(list(valid)).all(), t["resp"].value_counts().to_dict()
    t["item"] = pd.Categorical(t["item"], categories=list(cols.values()), ordered=True)
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    t["item"] = t["item"].astype(str)
    return t


def main() -> None:
    p = dv_fetch("10.7910/DVN/L5D0ST", "dataset.tab", RAW_ROOT / "l5d0st")
    d, _ = pyreadstat.read_sav(str(p))
    assert len(d) == 403
    d["id"] = range(1, len(d) + 1)
    d = d.rename(columns={"yas": "cov_age", "cinsiyet": "cov_gender", "sınıfdüzeyi": "cov_grade",
                          "yzkullanma": "cov_ai_use", "yzsıklık": "cov_ai_frequency"})
    covs = ["cov_age", "cov_gender", "cov_grade", "cov_ai_use", "cov_ai_frequency"]
    d[covs] = d[covs].astype("Int64")
    sdl = {c: f"sdl_{i}" for i, c in enumerate([c for c in d.columns if c.startswith("öyöbö") and c[5:].isdigit()], 1)}
    ai = {c: f"ai_{i}" for i, c in enumerate([c for c in d.columns if c.startswith("yzygtö") and c[6:].isdigit()], 1)}
    assert len(sdl) == 21 and len(ai) == 20
    valid = range(1, 6)
    t1, t2 = long(d, sdl, covs, valid), long(d, ai, covs, valid)
    # Items 13-20 carry reversed SPSS value labels (code 1 = strongly agree); flip to match items 1-12.
    rev = [f"ai_{i}" for i in range(13, 21)]
    m = t2["item"].isin(rev)
    t2.loc[m, "resp"] = 6 - t2.loc[m, "resp"]
    emit({"baysan_2026_self_directed_learning": (t1, {i: set(valid) for i in sdl.values()}),
          "baysan_2026_ai_attitudes": (t2, {i: set(valid) for i in ai.values()})})


if __name__ == "__main__":
    main()
