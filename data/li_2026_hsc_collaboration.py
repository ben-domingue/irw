#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/A9NUD7
# DOI: 10.7910/DVN/A9NUD7 (dataset, 2026; the record names no published paper)
#   Li, Yanling (2026). From Awareness to Competence: A Cognitive-Affective-Contextual Model of
#   Teachers' Collaborative Competence Development in Home-School-Community Collaboration.
#   Harvard Dataverse (Geely University of China).
# Data: the xlsx (1,351 Chinese schoolteachers; one column per question, the full Chinese
#       stem as header, options coded 1-5 in the order the .docx questionnaire lists them) is the
#       source. 数据(2).sav holds the same respondents under AW1-6 / RD1-4 / ID1-6 / CO1-5 but is
#       the authors' recode: mostly 6 - x, with ~2-4% of cells changed in other ways and the ID
#       block re-ordered (sav 3 = 有, 1 = 没有, 2 = 不清楚) -- so the as-administered xlsx coding
#       ships and the sav codes are used only as item names (Q7-12 -> AW1-6, Q13-16 -> RD1-4,
#       Q17-22 -> ID1-6, Q31-35 -> CO1-5). Q23-30 (single items, multi-select) and Q36 (free text)
#       do not ship.
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: shipped (Chinese stems from the xlsx column headers, anchors from the .docx
#   questionnaire; the .sav has no labels on the AW/RD/ID/CO columns, both levels empty). IRW
#   English translations in *_translated. Built by
#   automated_finding/itemtext_verification/make_itemtext_li_2026_hsc.py from stems().
#
# Tables: li_2026_hsc_awareness (AW1-6, 1 非常认同 .. 5 非常不认同), li_2026_hsc_recognition
#   (RD1-4, 1 非常重要 .. 5 非常不重要), li_2026_hsc_implementation (ID1-6, deposited 1 有 / 2 没有 /
#   3 不清楚; shipped as 1 = yes, 0 = no, with 不清楚 "unclear" set missing because it is not an
#   ordinal point), li_2026_hsc_competence (CO1-5, 1 完全能 .. 5 完全不能).
# Covariates: cov_gender (1 male, 2 female), cov_age (1 21-30, 2 31-40, 3 41-50, 4 >50),
#   cov_education (1-6, per value labels), cov_teaching_years (1 1-4, 2 5-9, 3 10+),
#   cov_head_teacher (1 yes incl. formerly, 2 no), cov_title (1 none .. 6 senior-high).
# id: 序号, the deposit's row number (the xlsx and sav share it).
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

RAW_DIR = RAW_ROOT / "10_7910_DVN_A9NUD7"
XLSX = "家校社协同育人教师调查问卷（1351份）-处理版(2).xlsx"
COVS = {1: "cov_gender", 2: "cov_age", 3: "cov_education", 4: "cov_teaching_years", 5: "cov_head_teacher",
        6: "cov_title"}
BLOCKS = {"li_2026_hsc_awareness": ([f"AW{i}" for i in range(1, 7)], range(7, 13)),
          "li_2026_hsc_recognition": ([f"RD{i}" for i in range(1, 5)], range(13, 17)),
          "li_2026_hsc_implementation": ([f"ID{i}" for i in range(1, 7)], range(17, 23)),
          "li_2026_hsc_competence": ([f"CO{i}" for i in range(1, 6)], range(31, 36))}


def qcol(x: pd.DataFrame, q: int) -> str:
    return [c for c in x.columns if c.startswith(f"{q}.")][0]


def stems() -> dict:
    """table -> [(code, Chinese stem)] with the stem read from the xlsx header of question k."""
    x = pd.read_excel(dv_fetch("10.7910/DVN/A9NUD7", XLSX, RAW_DIR), nrows=0)
    return {t: [(code, qcol(x, q).split(".", 1)[1].strip()) for code, q in zip(items, qs)]
            for t, (items, qs) in BLOCKS.items()}


def main() -> None:
    x = pd.read_excel(dv_fetch("10.7910/DVN/A9NUD7", XLSX, RAW_DIR))
    assert len(x) == 1351 and x["序号"].is_unique
    d = pd.DataFrame({"id": x["序号"].astype(int)})
    for q, name in COVS.items():
        d[name] = x[qcol(x, q)].astype("Int64")
    covs = list(COVS.values())
    out = {}
    for table, (items, qs) in BLOCKS.items():
        for code, q in zip(items, qs):
            d[code] = x[qcol(x, q)]
        if table.endswith("implementation"):
            for c in items:
                d[c] = d[c].map({1: 1, 2: 0})  # 3 = 不清楚 -> missing
            out[table] = (long(d, items, covs, valid=(0, 1)), pv_for(items, (0, 1)))
        else:
            out[table] = (long(d, items, covs, valid=range(1, 6)), pv_for(items, range(1, 6)))
    emit(out)


if __name__ == "__main__":
    main()
