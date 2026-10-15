#!/usr/bin/env python3
# Source: https://doi.org/10.17026/dans-z9b-7fej (DANS Data Station SSH)
# DOI: 10.17026/dans-z9b-7fej (dataset, deposited 2022-09-15, collected 2020-12; Hendrikx, K., Open
#   Universiteit). "Availability norms and burnout symptoms: The role of autonomy and telepressure".
# Data: "Data social norm, telepressure, autonomy, burnout.sav" (format=original), 229 Dutch employees:
#       TP1-TP8 telepressure (1-5), UTP1-8 / DIST1-5 / EMO1-5 / COGN1-5 = the 23 core Burnout Assessment
#       Tool items (exhaustion, mental distance, emotional and cognitive impairment; 1-5), AUT1-4 job
#       autonomy (1-5), NORM1-4 availability (social) norms (1-5). TP/Uitputting/.../Socnorm are sums.
# License: CC BY 4.0 (DANS record).
#
# Item text: not shipped -- variable labels name the block only ("Telepressure", "Uitputting"), no value
#   labels on any item, no instrument in the deposit. The BAT is a rights-register block in any case.
#
# Tables: hendrikx_2022_telepressure (8), hendrikx_2022_bat (23; codes utp1..cogn5 lower-cased),
#   hendrikx_2022_autonomy (4), hendrikx_2022_availability_norms (4); 229 ids (row index).
# Covariates: cov_gender (1 vrouw, 2 man, 3 as coded), cov_age, cov_sector (1 (semi)overheid,
#   2 bedrijfsleven), cov_contract_hours, cov_education (1 VMBO/MAVO - 5 WO), cov_telework (1 volledig,
#   2 gedeeltelijk, 3 niet), cov_hours_outside_worktime.
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
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "raw"))
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def zenodo_fetch(record: int, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://zenodo.org/api/records/{record}", headers=UA, timeout=120).json()
        url = [f["links"]["self"] for f in j["files"] if f["key"] == fname][0]
        download(url, p)
    return p


def figshare_fetch(article: int, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.figshare.com/v2/articles/{article}", headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == fname][0]
        download(url, p)
    return p


def mendeley_fetch(dataset: str, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://data.mendeley.com/public-api/datasets/{dataset}", headers=UA, timeout=120).json()
        url = [f["content_details"]["download_url"] for f in j["files"] if f["filename"] == fname][0]
        download(url, p)
    return p


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


def emit(tables: dict) -> None:
    """tables: name -> (long frame, permitted_values or None). QC, validate, write."""
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        keys = ["id", "item"] + [c for c in ("wave", "rater") if c in t]
        assert not t.duplicated(keys).any(), name
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


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=(),
         rename: dict | None = None) -> pd.DataFrame:
    """Melt `items` to long, drop missing, check integer codes inside `valid`, order columns.
    `rename` maps a source column to the `item` code it ships under (default: the column name)."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    if rename:
        t["item"] = t["item"].map(lambda c: rename.get(c, c))
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", *extra, "item"]).reset_index(drop=True)


def pv_for(items, valid) -> dict:
    return {i: set(valid) for i in items}


def dans_fetch(doi: str, fname: str, raw_dir: Path) -> Path:
    """Download one original-format file of a DANS Data Station (Dataverse) dataset."""
    return dv_fetch(doi, fname, raw_dir, host="ssh.datastations.nl")
import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "C_56_10_17026_dans_z9b_7fej"
FNAME = "Data social norm, telepressure, autonomy, burnout.sav"
COVS = {"Geslacht": "cov_gender", "Leeftijd": "cov_age", "Sector": "cov_sector",
        "Uren_arbeidscontract": "cov_contract_hours", "Opleidingsniveau": "cov_education",
        "Thuiswerk": "cov_telework", "Werk_buitenwerktijd": "cov_hours_outside_worktime"}
BLOCKS = {"telepressure": [f"TP{i}" for i in range(1, 9)],
          "bat": [f"UTP{i}" for i in range(1, 9)] + [f"DIST{i}" for i in range(1, 6)]
                 + [f"EMO{i}" for i in range(1, 6)] + [f"COGN{i}" for i in range(1, 6)],
          "autonomy": [f"AUT{i}" for i in range(1, 5)],
          "availability_norms": [f"NORM{i}" for i in range(1, 5)]}


def main() -> None:
    d, meta = pyreadstat.read_sav(str(dans_fetch("10.17026/dans-z9b-7fej", FNAME, RAW_DIR)))
    assert len(d) == 229
    d["id"] = d.index + 1
    for s, c in COVS.items():
        d[c] = d[s].astype("Int64")
    out = {}
    for k, cols in BLOCKS.items():
        ren = {c: c.lower() for c in cols}
        t = long(d, cols, list(COVS.values()), valid=range(1, 6), rename=ren)
        out[f"hendrikx_2022_{k}"] = (t, pv_for(ren.values(), range(1, 6)))
    emit(out)


if __name__ == "__main__":
    main()
