#!/usr/bin/env python3
# Source: https://zenodo.org/records/15375835
# DOI: 10.5281/zenodo.15375835 (dataset, 2025; Gomez Meza, Dora Noelia). "Base de Datos: Autoestima y
#   asertividad del estudiante de odontologia y su relacion con la comunicacion percibida por el
#   paciente en la atencion odontologica" (thesis data, UNMSM, Peru).
# Data: "Base SPSS.xlsx", 167 dental students each paired with one patient. AUTOEST1-10 Rosenberg
#       Self-Esteem Scale (1-4), ASERT1-30 Rathus Assertiveness Schedule (-3..+3, no 0, as
#       administered), both answered by the student; COM1-COM14, the patient's rating of the student's
#       communication (1-5). Totals, categories and z-scores are not shipped. COD_PAC/COD_EST are study
#       codes (PI1V, EI1V), not identifiers.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: not shipped -- the workbook has codes only; no questionnaire in the deposit (only the
#   informed-consent form). The Spanish RSES/Rathus wording used is not recorded.
#
# Tables: gomez_meza_2025_rses (10, 1-4), gomez_meza_2025_rathus (30, -3..3),
#   gomez_meza_2025_patient_communication (14, 1-5; id = the student, the patient is the rater).
# Covariates (student): cov_age, cov_sex (1/2), cov_year (1-3), cov_origin (PROCEDENCIA 1/2),
#   cov_works (1/2); patient table adds cov_patient_age, cov_patient_sex, cov_patient_education (1-4).
# id: row index (one student-patient pair per row).
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


def osf_fetch(node: str, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.osf.io/v2/nodes/{node}/files/osfstorage/", headers=UA, timeout=120).json()
        url = [f["links"]["download"] for f in j["data"] if f["attributes"]["name"] == fname][0]
        download(url, p)
    return p

RAW_DIR = RAW_ROOT / "zen_15375835"


def main() -> None:
    d = pd.read_excel(zenodo_fetch(15375835, "Base SPSS.xlsx", RAW_DIR), sheet_name="Base SPSS")
    assert len(d) == 167
    d["id"] = range(1, len(d) + 1)
    d["cov_age"] = d["EDAD_est"].astype(int); d["cov_sex"] = d["SEXO_est"].astype(int)
    d["cov_year"] = d["AÑO_EST"].astype(int); d["cov_origin"] = d["PROCEDENCIA_est"].astype(int)
    d["cov_works"] = d["Labora_est"].astype(int)
    d["cov_patient_age"] = d["EDAD_pac"].astype(int); d["cov_patient_sex"] = d["SEXO_pac"].astype(int)
    d["cov_patient_education"] = d["NIVELDEINSTRUCCIÓN"].astype(int)
    st = ["cov_age", "cov_sex", "cov_year", "cov_origin", "cov_works"]
    pt = st + ["cov_patient_age", "cov_patient_sex", "cov_patient_education"]
    rses = [f"AUTOEST{i}" for i in range(1, 11)]
    rat = [f"ASERT{i}" for i in range(1, 31)]
    com = [f"COM{i}" for i in range(1, 15)]
    emit({"gomez_meza_2025_rses": (long(d, rses, st, valid=range(1, 5)), pv_for(rses, range(1, 5))),
          "gomez_meza_2025_rathus": (long(d, rat, st, valid=[-3, -2, -1, 1, 2, 3]), pv_for(rat, [-3, -2, -1, 1, 2, 3])),
          "gomez_meza_2025_patient_communication": (long(d, com, pt, valid=range(1, 6)), pv_for(com, range(1, 6)))})


if __name__ == "__main__":
    main()
