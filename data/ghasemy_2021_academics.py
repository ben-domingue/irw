#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/ILLJEW
# DOI: 10.7910/DVN/ILLJEW (dataset; the record names no paper, and none matching its
#   title was found)
#   Ghasemy, Majid (2021). "Replication Data for: A comparative study between academics
#   in Malaysia and Japan in terms of satisfaction, motivation, and OCBI". Harvard
#   Dataverse.
# Data: "replication data for a comparative study between Malaysia and Japan.csv"
#       (format=original): 658 academics x 18 columns -- Gender, Age, Country, Tenure
#       and 14 five-point items: S4-S7 (job satisfaction), M1, M3-M6 (motivation),
#       OCBI1-OCBI5 (organizational citizenship behaviour toward individuals). The gaps
#       in the numbering (no S1-S3, no M2) are the deposit's: items retained after the
#       measurement model. No codebook; the record description says only "the variables
#       to estimate the nexus of satisfaction-motivation-OCBI".
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Plain CSV: no variable labels and no value labels; headers
#   are positional codes (S4, M1, OCBI1); no questionnaire in the deposit.
#
# Tables (1-5 as stored; anchors undocumented):
#   ghasemy_2021_job_satisfaction  S4-S7
#   ghasemy_2021_motivation        M1, M3, M4, M5, M6
#   ghasemy_2021_ocbi              OCBI1-OCBI5
# Covariates as the deposit codes them, labels undocumented: cov_gender (1/2),
#   cov_age_band (bands 1-5), cov_country (1/2: Malaysia and Japan, order unstated),
#   cov_tenure (bands 1-4).
# id: row index (no id column).

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

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_illjew"
FNAME = "replication data for a comparative study between Malaysia and Japan.csv"
P = "ghasemy_2021_"
TABLES = {"job_satisfaction": ["S4", "S5", "S6", "S7"],
          "motivation": ["M1", "M3", "M4", "M5", "M6"],
          "ocbi": [f"OCBI{i}" for i in range(1, 6)]}
COVS = {"Gender": "cov_gender", "Age": "cov_age_band", "Country": "cov_country",
        "Tenure": "cov_tenure"}


def fetch() -> Path:
    p = RAW_DIR / FNAME
    if not p.exists():
        j = requests.get("https://dataverse.harvard.edu/api/datasets/:persistentId/",
                         params={"persistentId": "doi:10.7910/DVN/ILLJEW"}, headers=UA,
                         timeout=120).json()
        fid = [f["dataFile"]["id"] for f in j["data"]["latestVersion"]["files"]
               if f["dataFile"].get("originalFileName") == FNAME][0]
        download(f"https://dataverse.harvard.edu/api/access/datafile/{fid}?format=original", p)
    return p


def main() -> None:
    d = pd.read_csv(fetch(), encoding="utf-8-sig")
    assert d.shape == (658, 18)
    items = [c for its in TABLES.values() for c in its]
    assert set(items) | set(COVS) == set(d.columns)
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    out = {}
    for suf, its in TABLES.items():
        out[P + suf] = (long(d, its, covs, valid=range(1, 6)), {i: set(range(1, 6)) for i in its})
    emit(out)


if __name__ == "__main__":
    main()
