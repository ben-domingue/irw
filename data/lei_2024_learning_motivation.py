#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/MB7OH8
# DOI: 10.1057/s41599-024-02666-6
#   Lei, H., Chen, C., & Luo, L. (2024). The examination of the relationship between
#   learning motivation and learning effectiveness: a mediation model of learning
#   engagement. Humanities and Social Sciences Communications, 11(1), 137.
# Data: Harvard Dataverse 10.7910/DVN/MB7OH8 (Chen, Chiwei; 2024-01-10).
#       dataset-20231029EN1.sav (format=original): 251 Chinese university students x 41
#       columns -- index, totalseconds, Gender, Grade, ProfessionMajor, Origin, 32
#       five-point items (value labels 1 very disagreeable .. 5 very agreeable) and nine
#       composites. dataset-20231029.sav is the same file with Chinese names and labels
#       (asserted equal below). PersonalityTraitsENG.sav/.xls is a different sample
#       (394 x PT1-PT10) with no item labels at all, so its items cannot be identified;
#       not used.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Variable labels are construct names with a number ("Internal
#   learning motivation 1"), not stems, in both language versions; value labels give
#   the five anchors. The questionnaire is not in the deposit.
#
# Tables (1-5 as stored; item = the deposit's variable name):
#   lei_2024_internal_motivation  ILM1-ILM5
#   lei_2024_external_motivation  ELM1-ELM5
#   lei_2024_engagement           BLE1-BLE3 (behavioural) + ELE1-ELE5 (emotional): the
#                                 article's two-dimension learning engagement, one
#                                 construct, so the multi_scale prefix warning is expected
#   lei_2024_effectiveness        EFF1-EFF9  learning effectiveness
# Skipped: V, ILM, ELM, LEG, LEFF, LEM, BLEM, ELEM (composites).
# Covariates: cov_gender (1 male, 2 female), cov_grade (1 freshman .. 4 senior),
#   cov_major (1 science and engineering, 2 literature and history, 3 art and sports),
#   cov_origin (1 village, 2 city and town), cov_completion_time_s (totalseconds, the
#   whole-survey completion time in seconds).
# id: `index` (the survey's response number, unique).

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
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


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
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any()
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


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=()) -> pd.DataFrame:
    """Melt, drop missing, check integer codes inside `valid`, order columns."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", "item"]).reset_index(drop=True)


def dv_fetch(doi: str, fname: str, raw_dir: Path, host: str = "dataverse.harvard.edu") -> Path:
    """Download one file of a Dataverse dataset in its original format."""
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://{host}/api/datasets/:persistentId/",
                         params={"persistentId": "doi:" + doi}, headers=UA, timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"].get("originalFileName", f["dataFile"]["filename"]) == fname][0]
        download(f"https://{host}/api/access/datafile/{fid}?format=original", p)
    return p


def dryad_file(path: Path) -> Path:
    """Dryad file downloads need a browser session (an Anubis challenge, then a 403 to
    plain HTTP clients), so the file is placed by hand: open the dataset page in a
    browser, download the file, and put it at `path`."""
    if not path.exists():
        raise SystemExit(f"missing {path}: download it from the Dryad dataset page "
                         "(plain HTTP downloads are refused) and rerun")
    return path
import pyreadstat

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_mb7oh8"
P = "lei_2024_"
TABLES = {"internal_motivation": [f"ILM{i}" for i in range(1, 6)],
          "external_motivation": [f"ELM{i}" for i in range(1, 6)],
          "engagement": [f"BLE{i}" for i in range(1, 4)] + [f"ELE{i}" for i in range(1, 6)],
          "effectiveness": [f"EFF{i}" for i in range(1, 10)]}
COVS = {"Gender": "cov_gender", "Grade": "cov_grade", "ProfessionMajor": "cov_major",
        "Origin": "cov_origin", "totalseconds": "cov_completion_time_s"}
COMPOSITES = ["V", "ILM", "ELM", "LEG", "LEFF", "LEM", "BLEM", "ELEM"]


def main() -> None:
    en, _ = pyreadstat.read_sav(str(dv_fetch("10.7910/DVN/MB7OH8", "dataset-20231029EN1.sav", RAW_DIR)))
    zh, _ = pyreadstat.read_sav(str(dv_fetch("10.7910/DVN/MB7OH8", "dataset-20231029.sav", RAW_DIR)))
    assert en.shape == zh.shape == (251, 41)
    assert (en.iloc[:, 6:33].to_numpy() == zh.iloc[:, 6:33].to_numpy()).all()
    d = en
    items = [c for its in TABLES.values() for c in its]
    assert set(items) | set(COVS) | set(COMPOSITES) | {"index"} == set(d.columns)
    assert d["index"].is_unique
    d["id"] = d["index"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = pd.to_numeric(d[c]).astype("Int64")
    out = {}
    for suf, its in TABLES.items():
        out[P + suf] = (long(d, its, covs, valid=range(1, 6)), {i: set(range(1, 6)) for i in its})
    emit(out)


if __name__ == "__main__":
    main()
