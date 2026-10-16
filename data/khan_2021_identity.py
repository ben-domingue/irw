#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/GQEFOI
# DOI: 10.7910/DVN/GQEFOI (Harvard Dataverse, 2021; Khan, Shazia). "Replication Data for: Different and
#   Better than You: The Interplay between Social Identity ..."; the record names no paper DOI.
# Data: New_Study_Social_Comparison_2021_Cleaned.sav (format=original), 309 Pakistani adults
#       (education labels Matric/O-levels .. ; places of worship Mosque/Imam-Bargah). Four 7-point
#       agreement/importance blocks: Place1-6 place identity (N 309); MID1-10 Moral Identity (Aquino &
#       Reed 2002; N 242); SI1..PI16 Aspects-of-Identity style importance items (social vs personal
#       identity, 1 not at all important .. 7; N 242); R1_I1..R14_I8_Rev Religious Orientation
#       (intrinsic / extrinsic-personal / extrinsic-social; N 242). The composite means
#       (Social_Comparison, Moral_Identity, ... Religious_Extrinsic), the single SID7-SID11 group items
#       (mixed anchors), the GB*/GD* multi-select text columns and MAH_1/COO_1 are not shipped.
#       Columns whose variable label ends "(R)"/"(Reversed)" (MID4, MID7, R3, R10, R14) carry value
#       labels running Strongly Agree = 1 .. Strongly Disagree = 7, i.e. the file stores them already
#       reverse-coded; shipped as stored (see data_notes).
# License: CC0 1.0 (Dataverse record).
#
# Item text: shipped (the .sav variable labels are the English stems and the value labels the seven
#   anchors, both levels present for every item). Built by
#   automated_finding/itemtext_verification/make_itemtext_khan_2021.py from stems().
#
# Tables: khan_2021_place_identity (6), khan_2021_moral_identity (10), khan_2021_identity_importance
#   (16), khan_2021_religious_orientation (14); all 1-7.
# Covariates: cov_gender (1 male, 2 female, 4 prefer not to say), cov_age_group (1 <18 .. 6),
#   cov_education (1-7), cov_place_type (1 rural, 2 urban, ...).
# id: the file's ID column.
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

RAW_DIR = RAW_ROOT / "dvn_GQEFOI"
FNAME = "New_Study_Social_Comparison_2021_Cleaned.sav"
BLOCKS = {"khan_2021_place_identity": r"Place\d+", "khan_2021_moral_identity": r"MID\d+",
          "khan_2021_identity_importance": r"[SP]I\d+", "khan_2021_religious_orientation": r"R\d+_.*"}


def load():
    import pyreadstat
    return pyreadstat.read_sav(str(dv_fetch("10.7910/DVN/GQEFOI", FNAME, RAW_DIR)))


def stems():
    """(table, code, stem, {resp: label}) for every shipped item."""
    d, meta = load()
    for table, pat in BLOCKS.items():
        for c in d.columns:
            if re.fullmatch(pat, c):
                yield table, c, meta.column_names_to_labels[c].strip(), \
                    {int(k): v for k, v in meta.variable_value_labels[c].items()}


def main() -> None:
    d, meta = load()
    assert len(d) == 309 and d["ID"].is_unique
    d["id"] = d["ID"].astype(int)
    d["cov_gender"] = d["Gender"].astype("Int64"); d["cov_age_group"] = d["Age"].astype("Int64")
    d["cov_education"] = d["Education"].astype("Int64"); d["cov_place_type"] = d["Place"].astype("Int64")
    covs = ["cov_gender", "cov_age_group", "cov_education", "cov_place_type"]
    out = {}
    for table, pat in BLOCKS.items():
        its = [c for c in d.columns if re.fullmatch(pat, c)]
        out[table] = (long(d, its, covs, valid=range(1, 8)), pv_for(its, range(1, 8)))
    assert [len(set(t[0]["item"])) for t in out.values()] == [6, 10, 16, 14]
    emit(out)


if __name__ == "__main__":
    main()
