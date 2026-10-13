#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/33B2DP
# DOI: 10.7910/DVN/33B2DP (dataset; the record names no published paper)
#   Rajeev, P., & Sujatha (2025). Superstitious Beliefs and Their Psychological Correlates: The
#   Role of Affective States and Personality Traits in Young Adults. Harvard Dataverse, V1.
# Data: "Superstitious beliefs, Affect, and Personality.xlsx": 209 Indian young adults (18-27,
#       Google Forms survey) with a 17-statement superstitious-beliefs questionnaire (1-5), the
#       20-item PANAS (1-5) and a 30-statement Big Five inventory (1-5; IPIP-style "Trust
#       others" statements). The column headers are the statements. The factor sums, totals,
#       the reversed copy of superstition item 10, the consent column, the timestamp and an
#       "Initials" column (not shipped, not used) are dropped.
# License: CC0 1.0 (Harvard Dataverse record).
#
# Item text: shipped for all three tables (the column header IS the statement, English
#   administration; no option labels in the file, so option_text is blank; built by
#   automated_finding/itemtext_verification/make_itemtext_rajeev_2025.py, which imports
#   stems()). PANAS and IPIP are `ship` rows in itemtext/instrument_rights_register.csv.
#
# Tables (item = <prefix>_<k> in header order, the script asserts header number k == position):
#   rajeev_2025_superstition  sb_1..sb_17, 1-5      rajeev_2025_panas  panas_1..panas_20, 1-5
#   rajeev_2025_bigfive       bf_1..bf_30, 1-5
# Covariates: cov_age (years), cov_gender (Female/Male), cov_location (Rural/Urban), cov_ses
#   (Lower/Middle/Higher SES).
# id: row index.
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

RAW_DIR = RAW_ROOT / "10_7910_DVN_33B2DP"
FNAME = "Superstitious beliefs, Affect, and Personality.xlsx"
COVS = {"Age": "cov_age", "Gender": "cov_gender", "Geographical Location": "cov_location",
        "Socioeconomic Status (SES)": "cov_ses"}
BLOCKS = {  # suffix -> (column slice, code prefix, instrument)
    "superstition": (slice(7, 24), "sb", "Superstitious beliefs questionnaire (17 statements, study-specific)"),
    "panas": (slice(24, 44), "panas", "Positive and Negative Affect Schedule (PANAS)"),
    "bigfive": (slice(44, 74), "bf", "30-item Big Five (O.C.E.A.N.) inventory, IPIP-style statements"),
}


def load() -> pd.DataFrame:
    return pd.read_excel(dv_fetch("10.7910/DVN/33B2DP", FNAME, RAW_DIR))


def stems(block: str) -> list:
    """(item code, header statement) pairs: the header is the statement, code = prefix + its number."""
    d = load()
    sl, prefix, _ = BLOCKS[block]
    out = []
    for k, col in enumerate(d.columns[sl], 1):
        m = re.match(r"^\s*(\d+)\.\s*(.*?)\s*$", str(col))
        assert m and int(m.group(1)) == k, (block, k, col)
        out.append((f"{prefix}_{k}", m.group(2)))
    return out


def main() -> None:
    d = load()
    assert len(d) == 209
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    out = {}
    for block, (sl, prefix, _) in BLOCKS.items():
        cols = list(load().columns[sl])
        rename = {c: code for c, (code, _) in zip(cols, stems(block))}
        out[f"rajeev_2025_{block}"] = (long(d, cols, covs, valid=range(1, 6), rename=rename),
                                       pv_for(rename.values(), range(1, 6)))
    emit(out)


if __name__ == "__main__":
    main()
