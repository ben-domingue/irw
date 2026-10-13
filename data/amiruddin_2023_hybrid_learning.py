#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Might_student-centered_principles_affect_active_learning_and_its_counterpart_An_empirical_study_of_Indonesian_Curriculum_Implementation/23214797
# DOI: 10.1177/21582440231214375
#   Amiruddin, Baharuddin, et al. (2023). May student-centered principles affect active learning
#   and its counterpart? An empirical study of Indonesian curriculum implementation. SAGE Open.
#   (The figshare record is deposited under "Anonym Anonym"; the author is read from the paper
#   Crossref returns for the title.)
# Data: Research Data.xlsx, sheet "Data WD3 2": 555 Indonesian vocational high-school students
#       with six 1-5 Likert blocks on hybrid-learning approaches and active learning: PED
#       pedagogy (7), AND andragogy (6), PEER peeragogy (5), Cyb cybergogy (7), HEU heutagogy
#       (6) and SRL self-regulated learning (12). MAH (a Mahalanobis distance) is not shipped.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped -- the column headers are positional codes (PED1, SRL1); the file has
#   no labels and no questionnaire; the stems are in the SAGE Open paper (CC BY), not fetched.
#
# Tables (item = the deposit's column name, resp 1-5): amiruddin_2023_pedagogy, _andragogy,
#   _peeragogy, _cybergogy, _heutagogy, _srl.
# Covariates (the deposit's dummies): cov_grade (Kelas, 10-13), cov_south_sulawesi (Sulsel),
#   cov_vocational_3yr (SMK3Tahun, 3-year vs 4-year programme), cov_male (Laki),
#   cov_first_child (Anak_Pertama), cov_internship_done (Telah_PKL).
# id: the deposit's Resp.
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
RAW_DIR = RAW_ROOT / "figshare_23214797"
COVS = {"Kelas": "cov_grade", "Sulsel": "cov_south_sulawesi", "SMK3Tahun": "cov_vocational_3yr",
        "Laki": "cov_male", "Anak_Pertama": "cov_first_child", "Telah_PKL": "cov_internship_done"}
BLOCKS = {"pedagogy": ("PED", 7), "andragogy": ("AND", 6), "peeragogy": ("PEER", 5),
          "cybergogy": ("Cyb", 7), "heutagogy": ("HEU", 6), "srl": ("SRL", 12)}


def main() -> None:
    d = pd.read_excel(figshare_fetch(23214797, "Research Data.xlsx", RAW_DIR))
    assert len(d) == 555 and d["Resp"].is_unique
    d["id"] = d["Resp"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    out = {}
    for suffix, (prefix, n) in BLOCKS.items():
        items = [f"{prefix}{k}" for k in range(1, n + 1)]
        out[f"amiruddin_2023_{suffix}"] = (long(d, items, covs, valid=range(1, 6)), pv_for(items, range(1, 6)))
    emit(out)


if __name__ == "__main__":
    main()
