#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/Z1BVYB
# DOI: 10.7910/DVN/Z1BVYB (Harvard Dataverse, 2024; Oskooii, Kassra A. R.; Lajevardi, Nazita). Data
#   and code for "Anti-Muslim Policy Preferences and Boundaries of American Identity Across
#   Partisanship"; paper DOI not on the record.
# Data: three US samples (format=original): 2018_10_CCES_final_weight.dta (721, CCES team module),
#       2019_6_Lucid_final_weight.dta (3,736) and 2020_8_Lucid_final_weight.dta (1,876). AMID1, AMID2,
#       AMID4, AMID5 boundaries-of-American-identity items (1-5; AMID5 absent in 2020), mar2/mar4/mar6
#       Muslim-American resentment items (1-5), and the anti-Muslim policy items (banmuslims, sharia,
#       registry, patrol, noweapon, restrictmosques), deposited rescaled to 0-1 in quarter steps and
#       mapped back to 0-4 here (x4). Pooled with cov_study; weights and the authors' indices are not
#       shipped. No codebook; item wording is in the paper only.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped -- codes only in the .dta files (no variable labels on the items); the stems
#   are in the published article, not the deposit.
#
# Tables: oskooii_2024_amid (4, 1-5), oskooii_2024_muslim_resentment (3, 1-5),
#   oskooii_2024_anti_muslim_policy (6 items, 0-4; each sample asked 3-5 of them); N = 6,333.
# Covariates: cov_study (2018 CCES, 2019 Lucid, 2020 Lucid), cov_age, cov_female, cov_white,
#   cov_black, cov_hispanic, cov_asian, cov_income (0-1 in fifths), cov_education (0-1 in fifths),
#   cov_democrat, cov_republican, cov_ideology (0-1 in sixths), cov_trump_approval (0-1).
# id: 10000 x sample index + row number.
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

RAW_DIR = RAW_ROOT / "dvn_Z1BVYB"
FILES = {"2018_cces": "2018_10_CCES_final_weight.dta", "2019_lucid": "2019_6_Lucid_final_weight.dta",
         "2020_lucid": "2020_8_Lucid_final_weight.dta"}
POLICY = ["banmuslims", "sharia", "registry", "patrol", "noweapon", "restrictmosques"]
COV = {"cov_age": "age", "cov_female": "female", "cov_white": "white", "cov_black": "black",
       "cov_hispanic": "hispanic", "cov_asian": "asian", "cov_income": "income", "cov_education": "educ",
       "cov_democrat": "democrat", "cov_republican": "republican", "cov_ideology": "ideology_7pt",
       "cov_trump_approval": "presapp"}


def main() -> None:
    parts = []
    for k, (study, fn) in enumerate(FILES.items(), 1):
        d = pd.read_stata(dv_fetch("10.7910/DVN/Z1BVYB", fn, RAW_DIR), convert_categoricals=False)
        d["id"] = 10000 * k + pd.Series(range(1, len(d) + 1))
        d["cov_study"] = study
        for p in POLICY:
            if p in d:
                v = d[p] * 4
                assert ((v.dropna() % 1) == 0).all(), p
                d[p] = v.round()
        parts.append(d)
    d = pd.concat(parts, ignore_index=True)
    assert len(d) == 721 + 3736 + 1876
    for c, v in COV.items():
        d[c] = d[v]
    covs = ["cov_study"] + list(COV)
    amid = [c for c in ["AMID1", "AMID2", "AMID4", "AMID5"]]
    mar = ["mar2", "mar4", "mar6"]
    emit({"oskooii_2024_amid": (long(d, amid, covs, valid=range(1, 6)), pv_for(amid, range(1, 6))),
          "oskooii_2024_muslim_resentment": (long(d, mar, covs, valid=range(1, 6)), pv_for(mar, range(1, 6))),
          "oskooii_2024_anti_muslim_policy": (long(d, POLICY, covs, valid=range(0, 5)), pv_for(POLICY, range(0, 5)))})


if __name__ == "__main__":
    main()
