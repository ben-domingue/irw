#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Cultural_Participation_Practices_Cultural_Apprisal_and_Subjective_Well-being_in_Cluj-Napoca_Metro_Area_2022/23614611
# DOI: 10.6084/m9.figshare.23614611 (dataset; the Metadata.txt names the paper "The Mediating
#   Role of Cultural Appraisal in the Relationship Between Cultural Participation Practices and
#   Subjective Well-being: Cultural Commons in Cluj Metro Area, Romania" without a DOI)
#   Petrovici, N., Pop, C., & Zbranca, R. (2025). Cultural Participation Practices, Cultural
#   Apprisal and Subjective Well-being in Cluj-Napoca Metro Area, 2022. figshare.
# Data: data.csv: 735 adults of the Cluj-Napoca metropolitan area (telephone survey, Jan 2022,
#       Romanian). Three item blocks: cultural participation in the last 12 months (A1-A15,
#       1 Never .. 6 Five or more times), associations with art and cultural experiences
#       (B1-B8, 1/2 as deposited -- the codebook says 1 Yes / 0 No but the file holds 1 and 2,
#       so 2 is read as No), and the four-item personal well-being block of Benson et al. 2019
#       (C1-C4, 1 Total agreement .. 4 Totally disagree). 9/99 (don't know / no answer) are
#       dropped. The CPCA scores, Benson score and other derived columns are not shipped.
# License: CC BY 4.0 (figshare record).
#
# Item text: shipped for all three tables from the deposit's own questionnaire files -- the
#   Romanian administered wording ("Questionnaire in Romanian language.txt") with the authors'
#   English translation ("Questionnaire in English language (translated).txt"); anchors from
#   the same files. The B block's 2 = No reading is IRW's, from the data (see above).
#
# Tables: petrovici_2025_cultural_participation (735 x 15, 1-6),
#   petrovici_2025_culture_appreciation (735 x 8, 1/2), petrovici_2025_wellbeing (735 x 4, 1-4).
# Covariates: cov_female, cov_age, cov_education, cov_professional_status, cov_ethnicity,
#   cov_minority, cov_culture_work, cov_municipality, cov_weight (the authors' post-stratification weight).
# id: the deposit's id column.
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


import re  # noqa: E402

RAW_DIR = RAW_ROOT / "figshare_23614611"
COVS = {"Female": "cov_female", "Age": "cov_age", "Education8": "cov_education",
        "Professional_Status": "cov_professional_status", "Etnicity": "cov_ethnicity", "Minority": "cov_minority",
        "CultureAuto": "cov_culture_work", "Municipality": "cov_municipality", "Weight": "cov_weight"}
A = [f"A{i}" for i in range(1, 16)]
B = [f"B{i}" for i in range(1, 9)]
C = [f"C{i}" for i in range(1, 5)]
TABLES = {"petrovici_2025_cultural_participation": (A, range(1, 7)),
          "petrovici_2025_culture_appreciation": (B, (1, 2)),
          "petrovici_2025_wellbeing": (C, range(1, 5))}
Q_EN = "Questionnaire in English language (translated).txt"
Q_RO = "Questionnaire in Romanian language.txt"


def stems(lang: str) -> dict:
    """code -> stem from the deposit's questionnaire text (lang 'en' or 'ro')."""
    txt = figshare_fetch(23614611, Q_EN if lang == "en" else Q_RO, RAW_DIR).read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^([ABC]\d+)\.\s+(.+?)\s*$", txt, flags=re.M):
        if m.group(1) in A + B + C:
            out.setdefault(m.group(1), m.group(2))
    assert set(out) == set(A + B + C), set(A + B + C) - set(out)
    return out


def main() -> None:
    d = pd.read_csv(figshare_fetch(23614611, "data.csv", RAW_DIR))
    assert len(d) == 735 and d["id"].is_unique
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in A + B + C:
        d.loc[d[c].isin([9, 99]), c] = pd.NA   # don't know / no answer
    tables = {}
    for name, (items, valid) in TABLES.items():
        tables[name] = (long(d, items, covs, valid=valid), pv_for(items, valid))
    emit(tables)


if __name__ == "__main__":
    main()
