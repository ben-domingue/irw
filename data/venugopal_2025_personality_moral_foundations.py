#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/LQOADH
# DOI: 10.7910/DVN/LQOADH (Harvard Dataverse, 2025; Venugopal, Santhosh Kumar). "Personality and moral
#   foundations"; description "Survey - moral foundations and personality", no paper named.
# Data: excelfromstata.xls (format=original), 124 respondents. extra1-10 / agree1-10 / consc1-10 /
#       emoti1-10 / intel1-10: a 50-item Big Five marker inventory (1-5; Goldberg IPIP-50 layout, one
#       item per factor in rotation). harm1-6 / fair1-6 / loya1-6 / auth1-6 / purity1-6: the 30-item
#       Moral Foundations Questionnaire (0-5). sd1-sd27 (1-5) is an undocumented 27-item block (no
#       codebook; "sd" is not resolved -- social desirability? self-deception?) and is not shipped.
#       The only demographic is gender.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped -- codes only, no codebook or questionnaire in the deposit; the IPIP and MFQ
#   wording would have to be assumed from the code pattern.
#
# Tables: venugopal_2025_big_five (50, 1-5), venugopal_2025_mfq (30, 0-5); N = 124.
# Covariates: cov_gender (Male/Female).
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


def osf_fetch(node: str, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.osf.io/v2/nodes/{node}/files/osfstorage/", headers=UA, timeout=120).json()
        url = [f["links"]["download"] for f in j["data"] if f["attributes"]["name"] == fname][0]
        download(url, p)
    return p
import re

RAW_DIR = RAW_ROOT / "dvn_LQOADH"


def main() -> None:
    d = pd.read_excel(dv_fetch("10.7910/DVN/LQOADH", "excelfromstata.xls", RAW_DIR))
    assert len(d) == 124
    d["id"] = range(1, len(d) + 1)
    d["cov_gender"] = d["gen"]
    b5 = [c for c in d.columns if re.fullmatch(r"(extra|agree|consc|emoti|intel)\d+", c)]
    mfq = [c for c in d.columns if re.fullmatch(r"(harm|fair|loya|auth|purity)\d+", c)]
    sd = [c for c in d.columns if re.fullmatch(r"sd\d+", c)]
    assert len(b5) == 50 and len(mfq) == 30 and len(sd) == 27
    print(f"skipping undocumented block sd1-sd{len(sd)}")
    emit({"venugopal_2025_big_five": (long(d, b5, ["cov_gender"], valid=range(1, 6)), pv_for(b5, range(1, 6))),
          "venugopal_2025_mfq": (long(d, mfq, ["cov_gender"], valid=range(0, 6)), pv_for(mfq, range(0, 6)))})


if __name__ == "__main__":
    main()
