#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/84tz3jkhr3
# DOI: 10.17632/84tz3jkhr3 (Mendeley Data, 2022; Scattolin, Marina; Panasiti, Maria Serena; Aglioti,
#   Salvatore Maria). Data for Scattolin, Panasiti & Aglioti (2022), "Morality in the flesh: on the
#   link between bodily self-consciousness, moral identity and (dis)honest behaviour", Royal Society
#   Open Science, doi:10.1098/rsos.220061.
# Data: For_Testing_Study1_eH_WP1_L1.xlsx sheet "S1 - Raw Questionnaires" (626 Italian adults) and
#       For_Testing_Study2_eH_WP1_L1.xlsx sheet "S2 - Raw Questionnaires" (606), the two online samples
#       the README releases for new hypotheses (the For_Replication files are not public). Same seven
#       questionnaires in both studies: BCQ_1-5 Body Consciousness Questionnaire private-body subscale
#       (0-4), ESSS_1-9 Embodied Sense of Self Scale (1-5), SA_1-11 Sense of Agency Scale (1-7),
#       MIS_1-33 Monetary Intelligence Scale (1-5), SoP_1-8 Sense of Power (1-7), PMDS_1-8 Propensity
#       to Morally Disengage (1-7), MIM_1-10 Moral Identity Measure (1-5). Pooled with cov_study; the
#       Temptation-to-Lie card task (two trials per person, "STDT" sheets), Study 2's Reason_1-12 and
#       COVID items, SES and the scored/centered sheets are not shipped. README_eH_WP1_L1.txt documents
#       every column and names each instrument's source.
# License: CC BY 4.0 (Mendeley record).
#
# Item text: not shipped -- the workbooks carry codes only (BCQ_1 ...); the README names the
#   instruments but not the wording, and the Italian administration wording is not in the deposit.
#
# Tables: scattolin_2022_bcq (5, 0-4), scattolin_2022_esss (9, 1-5), scattolin_2022_sa (11, 1-7),
#   scattolin_2022_mis (33, 1-5), scattolin_2022_sop (8, 1-7), scattolin_2022_pmds (8, 1-7),
#   scattolin_2022_mim (10, 1-5); each pooled over the two studies, N = 1,232.
# Covariates: cov_study (1, 2), cov_sex (1 male, 2 female, 3 other -- Study 2 only), cov_age,
#   cov_education (1 no diploma .. 7 PhD).
# id: Study 1 keeps its S1_n number; Study 2 ids are offset by 1000 (S2_n -> 1000 + n).
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
import re

RAW_DIR = RAW_ROOT / "mdl_84tz3jkhr3"
FILES = {1: ("For_Testing_Study1_eH_WP1_L1.xlsx", "S1 - Raw Questionnaires"),
         2: ("For_Testing_Study2_eH_WP1_L1.xlsx", "S2 - Raw Questionnaires")}
BLOCKS = {"scattolin_2022_bcq": ("BCQ", range(0, 5)), "scattolin_2022_esss": ("ESSS", range(1, 6)),
          "scattolin_2022_sa": ("SA", range(1, 8)), "scattolin_2022_mis": ("MIS", range(1, 6)),
          "scattolin_2022_sop": ("SoP", range(1, 8)), "scattolin_2022_pmds": ("PMDS", range(1, 8)),
          "scattolin_2022_mim": ("MIM", range(1, 6))}


def main() -> None:
    parts = []
    for study, (fn, sheet) in FILES.items():
        d = pd.read_excel(mendeley_fetch("84tz3jkhr3", fn, RAW_DIR), sheet_name=sheet)
        n = d["ID"].str.extract(rf"^S{study}_(\d+)$")[0].astype(int)
        assert n.notna().all() and n.is_unique and n.max() < 1000
        d["id"] = n + (0 if study == 1 else 1000)
        d["cov_study"] = study
        parts.append(d)
    d = pd.concat(parts, ignore_index=True)
    assert len(d) == 626 + 606 and d["id"].is_unique
    d["cov_sex"] = d["Sex"].astype("Int64"); d["cov_age"] = d["Age"].astype("Int64")
    d["cov_education"] = d["Education"].astype("Int64")
    covs = ["cov_study", "cov_sex", "cov_age", "cov_education"]
    out = {}
    for table, (pre, valid) in BLOCKS.items():
        its = [c for c in d.columns if re.fullmatch(rf"{pre}_\d+", c)]
        out[table] = (long(d, its, covs, valid=valid), pv_for(its, valid))
    assert [len(set(t[0]["item"])) for t in out.values()] == [5, 9, 11, 33, 8, 8, 10]
    emit(out)


if __name__ == "__main__":
    main()
