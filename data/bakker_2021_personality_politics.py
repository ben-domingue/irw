#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/WZI945
# DOI: 10.7910/DVN/WZI945 (dataset, 2021; Bakker, Bert N.; Lelkes, Yphtach; Malka, Ariel). Replication data for
#   "Reconsidering the Link Between Self-Reported Personality Traits and Political Preferences" (American
#   Political Science Review, 2021, 10.1017/S0003055421000605).
# Data: two survey experiments on US adults in which the political questions were asked either before or after
#       the trait battery. Auth_experiment_data.Rdata (frame `both`, 2,020 rows, two samples pooled by the
#       authors as id = 1/2): the four child-rearing authoritarianism items (forced choice between two child
#       qualities, 1-5 with 3 = "Both"; stored as labelled strings, the leading digit is shipped), politicscondition
#       (1 = politics asked first). B5_experiment.Rdata (frame `merged`, 1,756 rows): a 15-item Big Five
#       battery (bfioriginal/artistic/imagination = openness, bfic1-3, bfie1-3, bfia1-3, bfin1-3; 1-5),
#       politics2nd (1 = politics asked second). The GSS and LISS panel files in the deposit are third-party
#       re-deposits and are not touched (ruling 2026-10-09).
# License: CC0 1.0 (Dataverse).
# Note: the .Rdata files are converted to CSV with Rscript inside the script (pyreadr segfaults on
#   B5_experiment.Rdata); R must be on PATH.
#
# Item text: not shipped -- the Big Five frame carries codes only; the authoritarianism frame carries the two
#   child qualities per item as value labels but not the stem (the stem is in the paper's appendix).
#
# Tables: bakker_2021_authoritarianism (4 items, N = 2,020, treat = politics first), bakker_2021_bfi15 (15 items,
#   N = 1,756, treat = politics second).
# Covariates: authoritarianism -- cov_sample (1/2), cov_pid7, cov_ideology (1-7), cov_race, cov_gender, cov_age,
#   cov_education; bfi15 -- cov_age, cov_gender, cov_education, cov_race, cov_ideology (1-7 from the labels),
#   cov_hispanic.
# id: row index within each frame.
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
import subprocess


def rdata_frame(path: Path, frame: str) -> pd.DataFrame:
    """Read one data.frame out of an .Rdata via Rscript (pyreadr segfaults on B5_experiment.Rdata)."""
    out = path.with_suffix(".csv")
    if not out.exists():
        subprocess.run(["Rscript", "-e", f'load("{path}"); write.csv({frame}, "{out}", row.names = FALSE)'], check=True)
    return pd.read_csv(out)

RAW_DIR = RAW_ROOT / "dvn_WZI945"
IDEO = ["Extremely liberal", "Liberal", "Slightly liberal", "Moderate; middle of the road", "Slightly conservative",
        "Conservative", "Extremely conservative"]


def main() -> None:
    both = rdata_frame(dv_fetch("10.7910/DVN/WZI945", "Auth_experiment_data.Rdata", RAW_DIR), "both")
    assert len(both) == 2020
    both["cov_sample"] = both["id"].astype(int)  # the authors' id column is a sample flag (1/2)
    both["id"] = range(1, len(both) + 1)
    both["treat"] = both["politicscondition"].astype(int)
    auth = ["auth1", "auth2", "auth3", "auth4"]
    for c in auth:
        both[c] = pd.to_numeric(both[c].astype(str).str.extract(r"^(\d)")[0], errors="coerce")
    cov = {"cov_pid7": "pid7", "cov_ideology": "ideology", "cov_race": "race",
           "cov_gender": "gender", "cov_age": "age", "cov_education": "education"}
    for k, v in cov.items():
        both[k] = both[v]
    cov["cov_sample"] = "cov_sample"
    covs_a = list(cov)
    merged = rdata_frame(dv_fetch("10.7910/DVN/WZI945", "B5_experiment.Rdata", RAW_DIR), "merged")
    assert len(merged) == 1756
    merged["id"] = range(1, len(merged) + 1)
    merged["treat"] = merged["politics2nd"].astype(int)
    bfi = ["bfioriginal", "bfiartistic", "bfiimagination", "bfic1", "bfic2", "bfic3", "bfie1", "bfie2", "bfie3",
           "bfia1", "bfia2", "bfia3", "bfin1", "bfin2", "bfin3"]
    merged["cov_age"] = pd.to_numeric(merged["Q4.6"], errors="coerce")
    merged["cov_gender"] = merged["Q4.3"]
    merged["cov_education"] = merged["Q4.7"]
    merged["cov_race"] = merged["Q4.5"]
    merged["cov_hispanic"] = merged["Q4.4"]
    merged["cov_ideology"] = merged["Q3.5"].map({s: i + 1 for i, s in enumerate(IDEO)})
    covs_b = ["cov_age", "cov_gender", "cov_education", "cov_race", "cov_hispanic", "cov_ideology"]
    emit({"bakker_2021_authoritarianism": (long(both, auth, covs_a, valid=range(1, 6), extra=["treat"]), pv_for(auth, range(1, 6))),
          "bakker_2021_bfi15": (long(merged, bfi, covs_b, valid=range(1, 6), extra=["treat"]), pv_for(bfi, range(1, 6)))})


if __name__ == "__main__":
    main()
