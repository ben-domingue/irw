#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/thmf63pbzr
# DOI: 10.17632/thmf63pbzr (dataset; the record names no published paper)
#   Esteves (2026). Sexual Disgust as a Moderator of Mating Strategy in the Dark Triad.
#   Mendeley Data, V1.
# Data: SDSD_DT_22_02_23_Total.sav: 600 Brazilian adults (Portuguese administration): the
#       31-item Sexual Disgust Inventory (SDI_01..SDI_31, 1-7) for all 600, and the 12-item
#       Dirty Dozen Dark Triad (DD_01..DD_12, 1-5) for the first 300 (Sujeito 1-300; the
#       deposit stacks two samples, the second without the DD). Two single-item mating
#       orientation ratings (short, long), sexual satisfaction, relationship length and the
#       authors' subscale means (Maq, Psico, Nar, Taboo, BDSM, ..., Nojo) are not shipped.
#       Estado / Cidade are empty columns.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: shipped for both tables (the .sav variable labels are the Portuguese stems,
#   "1- Sexo com animais."; no value labels at any level -- the 1-7 / 1-5 anchors are not in
#   the file, so option_text is blank; built by
#   automated_finding/itemtext_verification/make_itemtext_esteves_2026.py, which imports
#   stems() below). Neither instrument is in itemtext/instrument_rights_register.csv.
#
# Tables: esteves_2026_sdi (600 x 31, 1-7), esteves_2026_dddt (300 x 12, 1-5).
# Covariates (numeric codes as deposited; the .sav carries no value labels): cov_sex (1/2),
#   cov_sexual_orientation (1-5), cov_age (years), cov_marital_status (1-7), cov_education
#   (1-8), cov_religiosity (1-7), cov_political_orientation (1-7).
# id: the deposit's Sujeito.
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
import pyreadstat  # noqa: E402

RAW_DIR = RAW_ROOT / "mendeley_thmf63pbzr"
COVS = {"Sexo": "cov_sex", "Orientação_Sexual": "cov_sexual_orientation", "Idade": "cov_age",
        "Estado_Civil": "cov_marital_status", "Escolaridade": "cov_education",
        "Religiosidade": "cov_religiosity", "Orientação_Política": "cov_political_orientation"}
SDI = [f"SDI_{i:02d}" for i in range(1, 32)]
DD = [f"DD_{i:02d}" for i in range(1, 13)]


def stems(block: str) -> list:
    """(item code, Portuguese stem) pairs from the .sav variable labels, numbering stripped."""
    _, meta = pyreadstat.read_sav(str(mendeley_fetch("thmf63pbzr", "SDSD_DT_22_02_23_Total.sav", RAW_DIR)),
                                  metadataonly=True)
    import re
    out = []
    for c in {"sdi": SDI, "dddt": DD}[block]:
        lab = meta.column_names_to_labels[c]
        out.append((c, re.sub(r"^\d+\s*-\s*", "", lab).strip()))
    return out


def main() -> None:
    d, meta = pyreadstat.read_sav(str(mendeley_fetch("thmf63pbzr", "SDSD_DT_22_02_23_Total.sav", RAW_DIR)))
    assert len(d) == 600 and d["Sujeito"].is_unique
    d["id"] = d["Sujeito"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    assert d[DD].notna().any(axis=1).sum() == 300
    emit({
        "esteves_2026_sdi": (long(d, SDI, covs, valid=range(1, 8)), pv_for(SDI, range(1, 8))),
        "esteves_2026_dddt": (long(d, DD, covs, valid=range(1, 6)), pv_for(DD, range(1, 6))),
    })


if __name__ == "__main__":
    main()
