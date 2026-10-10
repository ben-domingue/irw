#!/usr/bin/env python3
# Source: https://doi.org/10.6084/m9.figshare.24100509.v1
# DOI: 10.2147/PRBM.S428167
#   Lin, W., Liang, H., Jiang, H., Mohd Nasir, M. A., & Zhou, H. (2023). Why is smartphone
#   addiction more common in adolescents with harsh parenting? Depression and
#   experiential avoidance's multiple mediating roles. Psychology Research and Behavior
#   Management, 16, 4817-4828.
# Data: figshare 24100509 (deposited by wanqimg lin, 2023-09-07), HP-D-EA-SA.sav (file
#       42285156): 456 students at a public junior high school in China x 38 columns --
#       T1序号 (serial number), T1性别 (gender), T1年级 (grade), T1年龄 (age) and four
#       scales whose variable labels are the Chinese item stems.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped. Variable labels carry every Chinese stem; value labels are
#   empty for every column, so the anchors are not in the file. The AAQ-II and the
#   SCL-90 are `block` rows in itemtext/instrument_rights_register.csv in any case.
#
# Tables (as stored; the record names the instruments):
#   lin_2023_smartphone_addiction  SA1-SA10  Smartphone Addiction Scale-Short Version, 1-6
#   lin_2023_harsh_parenting       HP1-HP4   harsh discipline scale, 1-5
#   lin_2023_exp_avoidance         EA1-EA7   Acceptance and Action Questionnaire-II, 1-7
#   lin_2023_depression            D1-D13    depression subscale of the 90-item Hopkins
#                                            symptom checklist (SCL-90), 1-5
# Covariates (codes as stored, no value labels): cov_gender (1/2; 240 vs 216, and the
#   record reports 52.6% female, so 1 is most likely female), cov_grade (1-3), cov_age.
# id: T1序号, the study's serial number (unique, 1-460).

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.6084_m9.figshare.24100509.v1"
URL = "https://ndownloader.figshare.com/files/42285156"
P = "lin_2023_"
TABLES = {"smartphone_addiction": ([f"SA{i}" for i in range(1, 11)], range(1, 7)),
          "harsh_parenting": ([f"HP{i}" for i in range(1, 5)], range(1, 6)),
          "exp_avoidance": ([f"EA{i}" for i in range(1, 8)], range(1, 8)),
          "depression": ([f"D{i}" for i in range(1, 14)], range(1, 6))}
COVS = {"T1性别": "cov_gender", "T1年级": "cov_grade", "T1年龄（周岁）": "cov_age"}


def main() -> None:
    d, _ = pyreadstat.read_sav(str(download(URL, RAW_DIR / "HP-D-EA-SA.sav")))
    assert d.shape == (456, 38) and d["T1序号"].is_unique
    items = [c for its, _ in TABLES.values() for c in its]
    assert set(items) | set(COVS) | {"T1序号"} == set(d.columns)
    d["id"] = d["T1序号"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    out = {}
    for suf, (its, valid) in TABLES.items():
        out[P + suf] = (long(d, its, covs, valid=valid), {i: set(valid) for i in its})
    emit(out)


if __name__ == "__main__":
    main()
