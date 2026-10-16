#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/tzv223xgsr
# DOI: 10.17632/tzv223xgsr.2 (dataset, 2020; Kessler, Erica). "Materials for: Assessing Epistemic Beliefs Regarding
#   the Co-construction of Knowledge" -- development of the Epistemic Beliefs about the Co-Construction of
#   Knowledge (EB-CCK) inventory in US adult samples.
# Data: four response workbooks and the three item lists. Study1_Sample1 (n = 280) answered the 30-item pool,
#       Study1_Sample2 (n = 219) the 22-item pool, Study2_Sample1 (n = 579) and Study2_Sample2 (n = 295) the final
#       18-item inventory; all 1-7 agreement. Item codes are the workbooks' positional Item_k, and the three pools
#       are numbered differently (Item_1 of the 30-item pool is not Item_1 of the 18-item inventory), so each pool
#       is its own table; the two 18-item samples are pooled with cov_sample. Study3_DataFile holds factor
#       averages only and is not shipped.
# License: CC BY 4.0 (Mendeley Data).
#
# Item text: shipped -- EB-CCK_30item.docx / _22item.docx / _18item.docx list the items in order, k-th paragraph =
#   Item_k (paper_order; the 30- and 22-item lists are numbered, the 18-item list is not). Mapping checked by item
#   polarity (itemtext_verification/verify_kessler_2020_ebcck.R).
#
# Tables: kessler_2020_ebcck_30 (30, N = 280), kessler_2020_ebcck_22 (22, N = 219), kessler_2020_ebcck_18 (18,
#   N = 874).
# Covariates: cov_age, cov_gender (1 male, 2 female, 3 other; one Sample-2 file also carries a 0 as deposited),
#   cov_ethnicity (coded as in the column header of each workbook), cov_sample (18-item table: 1/2).
# id: the workbooks' ID column (18-item table: 10000 * sample + ID).
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
import zipfile

RAW_DIR = RAW_ROOT / "mendeley_tzv223xgsr"
FILES = {"s1s1": "Study1_Sample1_DataFile.xlsx", "s1s2": "Study1_Sample2_DataFile.xlsx",
         "s2s1": "Study2_Sample1_DataFile.xlsx", "s2s2": "Study2_Sample2_DataFile.xlsx"}
DOCX = {30: "EB-CCK_30item.docx", 22: "EB-CCK_22item.docx", 18: "EB-CCK_18item.docx"}


def docx_items(n: int) -> list:
    """The n item stems, in document order, numbering stripped."""
    x = zipfile.ZipFile(mendeley_fetch("tzv223xgsr", DOCX[n], RAW_DIR)).read("word/document.xml").decode()
    paras = [re.sub(r"<[^>]+>", "", p) for p in re.findall(r"<w:p[ >].*?</w:p>", x, flags=re.S)]
    paras = [re.sub(r"^\d+\.\s*", "", p).strip() for p in paras if p.strip()]
    assert len(paras) == n, (n, len(paras))
    return paras


def load(key: str) -> pd.DataFrame:
    d = pd.read_excel(mendeley_fetch("tzv223xgsr", FILES[key], RAW_DIR))
    d.columns = [c.strip() for c in d.columns]
    d["cov_age"] = d["Age (in years)"]
    d["cov_gender"] = d[[c for c in d.columns if c.startswith("Gender")][0]]
    d["cov_ethnicity"] = d[[c for c in d.columns if c.startswith("Ethnicity")][0]]
    return d


def items(d):
    return [c for c in d.columns if re.fullmatch(r"Item_\d+", c)]


def main() -> None:
    f = {k: load(k) for k in FILES}
    assert {k: len(v) for k, v in f.items()} == {"s1s1": 280, "s1s2": 219, "s2s1": 579, "s2s2": 295}
    assert (len(items(f["s1s1"])), len(items(f["s1s2"])), len(items(f["s2s1"])), len(items(f["s2s2"]))) == (30, 22, 18, 18)
    for k in f:
        f[k]["id"] = f[k]["ID"].astype(int)
        assert f[k]["id"].is_unique
    f["s2s1"]["cov_sample"], f["s2s2"]["cov_sample"] = 1, 2
    f["s2s1"]["id"] += 10000
    f["s2s2"]["id"] += 20000
    s2 = pd.concat([f["s2s1"], f["s2s2"]], ignore_index=True)
    covs = ["cov_age", "cov_gender", "cov_ethnicity"]
    r = range(1, 8)
    emit({"kessler_2020_ebcck_30": (long(f["s1s1"], items(f["s1s1"]), covs, valid=r), pv_for(items(f["s1s1"]), r)),
          "kessler_2020_ebcck_22": (long(f["s1s2"], items(f["s1s2"]), covs, valid=r), pv_for(items(f["s1s2"]), r)),
          "kessler_2020_ebcck_18": (long(s2, items(s2), covs + ["cov_sample"], valid=r), pv_for(items(s2), r))})


if __name__ == "__main__":
    main()
