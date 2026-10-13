#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/252r6gdx48
# DOI: 10.17632/252r6gdx48 (dataset; the record names no published paper)
#   Yang, G., Kim, J., Chen, J., Hao, K., & Li, N. (2026). AI Literacy, Epistemic Beliefs, and
#   Academic Dishonesty Across Institutional Contexts. Mendeley Data, V1.
# Data: "(2) Dataset.xlsx", sheet Sheet2: 972 Chinese university and technical-vocational
#       college students, 60 seven-point items in three instruments; "(1) Questionnaire.docx"
#       lists every item stem with its source scale (Chiu et al. 2013 epistemic beliefs about AI
#       tools; Ng et al. 2024 AI literacy; Akbulut et al. 2008 / Chan 2025 academic dishonesty).
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: shipped (deposit questionnaire docx, English stems; the docx lists "BI4" where the
#   data column is BL4, mapped by position within the BL block). No option labels anywhere in
#   the deposit (docx carries no anchors; xlsx has no value labels), so option_text is blank.
#   The administration language is not stated in the record (Chinese sample, English
#   questionnaire deposited).
#
# Tables: yang_2026_epistemic_beliefs (972 x 12: SO, CE, JUS, SP), yang_2026_ai_literacy
#   (972 x 34: AL, BL, CL, EL), yang_2026_academic_dishonesty (972 x 14: PLA, FAL, DEL, UAH); all 1-7.
# Covariates: cov_institution_type (0/1 as deposited; the record says university vs
#   technical-vocational college but does not say which is which), cov_age, cov_gender (1/2,
#   uncoded in the deposit), cov_major (1/2, uncoded).
# id: the deposit's Participant number (P1 ... P972).
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


RAW_DIR = RAW_ROOT / "mendeley_252r6gdx48"
COVS = {"Institution type": "cov_institution_type", "Age": "cov_age", "Gender": "cov_gender", "Major": "cov_major"}
EB = [f"{b}{i}" for b in ("SO", "CE", "JUS", "SP") for i in (1, 2, 3)]
AIL = [f"AL{i}" for i in range(1, 13)] + [f"BL{i}" for i in range(1, 9)] + \
      [f"CL{i}" for i in range(1, 8)] + [f"EL{i}" for i in range(1, 8)]
AD = [f"PLA{i}" for i in range(1, 6)] + [f"FAL{i}" for i in range(1, 4)] + \
     [f"DEL{i}" for i in range(1, 4)] + [f"UAH{i}" for i in range(1, 4)]
TABLES = {"yang_2026_epistemic_beliefs": EB, "yang_2026_ai_literacy": AIL, "yang_2026_academic_dishonesty": AD}


def stems() -> dict:
    """code -> English stem from the deposit's questionnaire docx (table rows; BI4 -> BL4)."""
    from docx import Document
    doc = Document(mendeley_fetch("252r6gdx48", "(1) Questionnaire.docx", RAW_DIR))
    out = {}
    for row in doc.tables[0].rows:
        code, text = row.cells[0].text.strip(), row.cells[1].text.strip()
        if code == "BI4":
            code = "BL4"
        if code in EB + AIL + AD:
            out[code] = text
    assert set(out) == set(EB + AIL + AD), set(EB + AIL + AD) - set(out)
    return out


def main() -> None:
    d = pd.read_excel(mendeley_fetch("252r6gdx48", "(2) Dataset.xlsx", RAW_DIR), sheet_name="Sheet2")
    d.columns = [c.strip() for c in d.columns]   # one header carries trailing whitespace
    assert len(d) == 972 and d["Participant"].is_unique
    d["id"] = d["Participant"].str[1:].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    emit({name: (long(d, items, covs, valid=range(1, 8)), pv_for(items, range(1, 8)))
          for name, items in TABLES.items()})


if __name__ == "__main__":
    main()
