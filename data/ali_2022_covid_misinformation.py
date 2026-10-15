#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/ZOAKLW
# DOI: 10.7910/DVN/ZOAKLW (data); paper: Ali & Qazi (2022), "Cognitive reflection is associated with
#   greater truth discernment for COVID-19 headlines ...", HKS Misinformation Review.
# Data: covid-dataset.csv, 621 Pakistani social-media users (online survey): ten COVID-19 headline
#       statements each rated for agreement (0 / 0.5 / 1 in the file -> 0-2 here; the headline wording
#       and true/false status are not in the deposit -- the notebook only aggregates them into
#       true_acc/false_acc), and ten information-source use-frequency items freq_* (0 / .33 / .67 / 1
#       -> 0-3). The trust_* items have skip-pattern missingness (asked only for sources used) and the
#       two CRT items are not shipped.
# License: CC0 1.0 (Harvard Dataverse).
#
# Item text: not shipped -- the ten headlines are column-less ("To what an extent do you agree with the
#   statement?" x10); their wording is in the paper's appendix, not the deposit. The freq_* stems are
#   only the source names.
#
# Tables: ali_2022_covid_headlines (621 x 10, 0 disagree / 1 / 2 agree; item = headline_01..10 in
#   file order), ali_2022_info_source_freq (616 x 10, 0-3; item = source name).
# Covariates: cov_age, cov_gender (0/1 as deposited), cov_education (1-3), cov_crt_score (0, 0.5, 1).
# id: id_num from the file.
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

RAW_DIR = RAW_ROOT / "dv_ZOAKLW"
FNAME = "covid-dataset.csv"
FREQ = ["freq_channels", "freq_urdunews", "freq_englishnews", "freq_govt", "freq_radio", "freq_who",
        "freq_whatsapp", "freq_facebook", "freq_twitter", "freq_youtube"]


def main() -> None:
    d = pd.read_csv(dv_fetch("10.7910/DVN/ZOAKLW", FNAME, RAW_DIR))
    assert len(d) == 621 and d["id_num"].is_unique
    d["id"] = d["id_num"].astype(int)
    d["cov_age"] = d["age"].astype("Int64")
    d["cov_gender"] = d["gender"].astype("Int64")
    d["cov_education"] = d["edu"].astype("Int64")
    d["cov_crt_score"] = d["crt_score"]
    covs = ["cov_age", "cov_gender", "cov_education", "cov_crt_score"]
    agree = [c for c in d.columns if c.startswith("To what an extent do you agree")]
    assert len(agree) == 10
    ren = {c: f"headline_{i:02d}" for i, c in enumerate(agree, 1)}
    for c in agree:
        d[c] = (d[c] * 2).round()
    for c in FREQ:
        d[c] = (d[c] * 3).round()
    h = long(d, agree, covs, valid=range(0, 3), rename=ren)
    f = long(d, FREQ, covs, valid=range(0, 4), rename={c: c.replace("freq_", "") for c in FREQ})
    emit({"ali_2022_covid_headlines": (h, pv_for(sorted(h["item"].unique()), range(0, 3))),
          "ali_2022_info_source_freq": (f, pv_for(sorted(f["item"].unique()), range(0, 4)))})


if __name__ == "__main__":
    main()
