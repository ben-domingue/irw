#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/SRC9HN
# DOI: 10.7910/DVN/SRC9HN (replication data; paper 10.1017/S0007123416000600)
#   Kellstedt, P. M., Ramirez, M. D., Vedlitz, A., & Zahran, S. (2019). Does political
#   sophistication minimize value conflict? Evidence from a heteroskedastic graded IRT model of
#   opinions toward climate change. British Journal of Political Science, 49(4), 1309-1332.
# Data: noaasammy.dta, a 2004 US national telephone survey of 1,093 adults on climate change
#       (one row per respondent, Stata variable + value labels; don't-know/refused already missing).
#       Thirteen blocks of same-format items ship as one table each (see TABLES); single
#       items, open-ended codes, split-ballot experiments (q16-q19, q104) and demographics do not.
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: shipped (the .dta variable labels are abbreviated stems, "concern now - social
#   security"; value labels give the anchors, 0-10 scales labelled at the endpoints only; English
#   administration). Built by automated_finding/itemtext_verification/make_itemtext_kellstedt_2017.py
#   from stems() below.
#
# Tables (id = resp_num, the deposit's respondent number):
#   kellstedt_2017_concern_now      q5_1-q5_13   0-10  concern about 13 national issues now
#   kellstedt_2017_concern_future   q6_1-q6_13   0-10  concern about the same issues in the future
#   kellstedt_2017_informed         q10_1-q10_13 0-10  how informed about the same issues
#   kellstedt_2017_science_quiz     q12-q15, q62-q67  0/1 true/false science and climate knowledge
#   kellstedt_2017_nep              q20-q35      1-4   New Ecological Paradigm agreement items
#   kellstedt_2017_eco_behavior     q36,q37,q39-q45 1-4 frequency of pro-environmental behaviours
#   kellstedt_2017_civic_action     q46-q57      0/1   political / environmental actions taken
#   kellstedt_2017_gwcc_attitudes   q68-q75      1-4   agreement with global warming statements
#   kellstedt_2017_info_source_use  q78_1-q78_14 0-10  use of information sources
#   kellstedt_2017_info_source_trust q79_1-q79_15 0-10 trust in information sources
#   kellstedt_2017_competence       q80_1-q80_10 0-10  competence of institutions on climate
#   kellstedt_2017_policy_support   q89-q92, q93 (v1/v2 merged, see note), q94-q100 1-4
#   kellstedt_2017_climate_effects  q101-q103, q106-q108 1-4 expected climate effects
#   q93 was a split ballot (q93_v1 "higher prices for environmental bads" / q93_v2 "lower prices
#   for environmental goods"); each ships under its own item code, so the table carries 13 codes.
# Covariates: cov_gender (0 female, 1 male), cov_age (years), cov_education (1-6),
#   cov_ideology (1 strongly liberal .. 7 strongly conservative), cov_income (1-11 bands).
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

RAW_DIR = RAW_ROOT / "10_7910_DVN_SRC9HN"
FNAME = "noaasammy.dta"
COVS = {"gender": "cov_gender", "q117": "cov_age", "q116": "cov_education", "q118": "cov_ideology",
        "q122": "cov_income"}
R11 = range(0, 11)
TABLES = {
    "kellstedt_2017_concern_now": ([f"q5_{i}" for i in range(1, 14)], R11),
    "kellstedt_2017_concern_future": ([f"q6_{i}" for i in range(1, 14)], R11),
    "kellstedt_2017_informed": ([f"q10_{i}" for i in range(1, 14)], R11),
    "kellstedt_2017_science_quiz": ([f"q{i}" for i in (12, 13, 14, 15, 62, 63, 64, 65, 66, 67)], (0, 1)),
    "kellstedt_2017_nep": ([f"q{i}" for i in range(20, 36)], range(1, 5)),
    "kellstedt_2017_eco_behavior": ([f"q{i}" for i in (36, 37, 39, 40, 41, 42, 43, 44, 45)], range(1, 5)),
    "kellstedt_2017_civic_action": ([f"q{i}" for i in range(46, 58)], (0, 1)),
    "kellstedt_2017_gwcc_attitudes": ([f"q{i}" for i in range(68, 76)], range(1, 5)),
    "kellstedt_2017_info_source_use": ([f"q78_{i}" for i in range(1, 15)], R11),
    "kellstedt_2017_info_source_trust": ([f"q79_{i}" for i in range(1, 16)], R11),
    "kellstedt_2017_competence": ([f"q80_{i}" for i in range(1, 11)], R11),
    "kellstedt_2017_policy_support": ([f"q{i}" for i in (89, 90, 91, 92)] + ["q93_v1", "q93_v2"]
                                     + [f"q{i}" for i in range(94, 101)], range(1, 5)),
    "kellstedt_2017_climate_effects": ([f"q{i}" for i in (101, 102, 103, 106, 107, 108)], range(1, 5)),
}


def load():
    return pyreadstat.read_dta(str(dv_fetch("10.7910/DVN/SRC9HN", FNAME, RAW_DIR)))


def stems() -> dict:
    """table -> [(item code, variable label, {value: label})], from the .dta metadata."""
    _, meta = pyreadstat.read_dta(str(dv_fetch("10.7910/DVN/SRC9HN", FNAME, RAW_DIR)), metadataonly=True)
    out = {}
    for table, (items, valid) in TABLES.items():
        out[table] = [(c, meta.column_names_to_labels[c].strip(),
                       {int(k): v for k, v in meta.variable_value_labels[c].items() if int(k) in valid})
                      for c in items]
    return out


def main() -> None:
    d, meta = load()
    assert len(d) == 1093 and d["resp_num"].is_unique
    d = d.rename(columns={"resp_num": "id", **COVS})
    covs = list(COVS.values())
    d.loc[d["cov_age"] >= 998, "cov_age"] = pd.NA
    for c in covs:
        d[c] = d[c].astype("Int64")
    used = set()
    out = {}
    for table, (items, valid) in TABLES.items():
        assert not used & set(items), table
        used |= set(items)
        out[table] = (long(d, items, covs, valid=valid), pv_for(items, valid))
    emit(out)


if __name__ == "__main__":
    main()
