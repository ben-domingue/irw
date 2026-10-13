#!/usr/bin/env python3
# Source: https://zenodo.org/records/21901190
# DOI: 10.1109/IAICT71158.2026.11620932 (paper; the Zenodo record carries the paper's DOI)
#   Naulia, Mega; Tjhin, Viany Utami (2026). The Utilization of ChatGPT as a Component of a
#   Digital Learning System and Its Impact on Students' Learning Motivation: A Case Study of
#   SMP Negeri 5 South Tangerang. IEEE IAICT 2026. Data: Zenodo record 21901190.
# Data: "OLDAT BAB 4_MOTIVASI.xlsx": 354 junior-high (grade 8) students; sheet "VARIABEL X"
#       = ChatGPT utilisation, 15 items; sheet "VARIABEL Y" = learning motivation, 20 items;
#       both 1-5; sheet "karakteristik responden" = age (13/14), gender, class. The
#       "VALIDITAS" sheet is a 30-61 row pilot and is not shipped.
# License: CC BY 4.0 (Zenodo record; the IEEE paper itself is not open).
#
# Item text: not shipped. Headers are X1..X15 / Y1..Y20; the questionnaire is only in the
#   (closed) IEEE paper. Checked: all four sheets.
#
# Tables: naulia_2026_chatgpt_use (X1-X15), naulia_2026_learning_motivation (Y1-Y20); 1-5.
#   Rows of the three sheets are aligned by position (354 each, no id column in X/Y).
# Covariates: cov_age (13/14), cov_gender (Perempuan/Laki-laki), cov_class (8A..).
# id: the characteristics sheet's "No" (1..354).

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

RAW_DIR = RAW_ROOT / "10_5281_zenodo_21901190"
FNAME = "OLDAT BAB 4_MOTIVASI.xlsx"


def main() -> None:
    p = zenodo_fetch(21901190, FNAME, RAW_DIR)
    x = pd.read_excel(p, sheet_name="VARIABEL X")
    y = pd.read_excel(p, sheet_name="VARIABEL Y")
    k = pd.read_excel(p, sheet_name="karakteristik responden")
    assert len(x) == len(y) == len(k) == 354 and k["No"].is_unique
    xi = [f"X{i}" for i in range(1, 16)]
    yi = [f"Y{i}" for i in range(1, 21)]
    assert (x[xi].sum(axis=1) == x[[c for c in x.columns if str(c).strip().lower() == "jumlah"][0]]).all() and (y[yi].sum(axis=1) == y[[c for c in y.columns if str(c).strip().lower() == "jumlah"][0]]).all()
    d = pd.DataFrame({"id": k["No"].astype(int), "cov_age": k["Usia"].astype(int),
                      "cov_gender": k["Jenis Kelamin"], "cov_class": k["Kelas"]})
    d = pd.concat([d, x[xi], y[yi]], axis=1)
    covs = ["cov_age", "cov_gender", "cov_class"]
    emit({"naulia_2026_chatgpt_use": (long(d, xi, covs, valid=range(1, 6)), pv_for(xi, range(1, 6))),
          "naulia_2026_learning_motivation": (long(d, yi, covs, valid=range(1, 6)), pv_for(yi, range(1, 6)))})


if __name__ == "__main__":
    main()
