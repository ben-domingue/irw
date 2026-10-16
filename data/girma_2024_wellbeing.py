#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/jgsv7pcrs8
# DOI: 10.17632/jgsv7pcrs8 (Mendeley Data, 2024; Girma, Samuel; Mihrka, Adamu; Werku, Anteneh).
#   "mental well-being, moral identity, meaning in life, hope"; no linked article.
# Data: "SPSS- MII, MIL, HP and MW(595).sav", 595 Ethiopian university students (GPA on a 4-point
#       scale). Four blocks: hop1p..hop8a Adult Hope Scale (Snyder; 8 items, 1-8; p = pathways, a =
#       agency); MII1..MII10 Moral Identity (Aquino & Reed 2002; 1-7; internalization / symbolization,
#       MII4 and MII7 labelled "(R)"); MILP1..MILS10 Meaning in Life Questionnaire (Steger; 1-7;
#       presence / search); MW1-MW14 Warwick-Edinburgh Mental Well-being Scale (1-5). Sums and means
#       are not shipped. Three cells sit outside their item's scale (MII4 = 8, MILP1 = 8, MILS3 = 8 on
#       1-7 instruments; each isolated to one item) and are dropped as entry errors (see data_notes).
#       The variable labels of the (R) items read as the original stems and the data run 1-7 with
#       the bulk at the top, so they are stored as answered, not reverse-coded.
# License: CC BY 4.0 (Mendeley record).
#
# Item text: shipped (the .sav variable labels are the English stems for all 42 items; the file has
#   no value labels for any item, so option_text is blank). Built by
#   automated_finding/itemtext_verification/make_itemtext_girma_2024.py from stems(). English
#   instrument; administered language not stated (left blank).
#
# Tables: girma_2024_hope (8, 1-8), girma_2024_moral_identity (10, 1-7), girma_2024_mlq (10, 1-7),
#   girma_2024_wemwbs (14, 1-5).
# Covariates: cov_gender (1 male, 2 female), cov_age (years; the file's age_classified column holds
#   the raw ages and Age_raw the 1-2 class, swapped labels), cov_marital_status (1 single, 2 married),
#   cov_gpa.
# id: row index (no identifier in the file).
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

RAW_DIR = RAW_ROOT / "mdl_jgsv7pcrs8"
FNAME = "SPSS- MII, MIL, HP and MW(595).sav"
BLOCKS = {"girma_2024_hope": (r"hop\d+[pa]", range(1, 9)), "girma_2024_moral_identity": (r"MI[IS]\d+", range(1, 8)),
          "girma_2024_mlq": (r"MIL[PS]\d+", range(1, 8)), "girma_2024_wemwbs": (r"MW\d+", range(1, 6))}


def load():
    import pyreadstat
    return pyreadstat.read_sav(str(mendeley_fetch("jgsv7pcrs8", FNAME, RAW_DIR)))


def stems():
    d, meta = load()
    for table, (pat, valid) in BLOCKS.items():
        for c in d.columns:
            if re.fullmatch(pat, c):
                assert c not in meta.variable_value_labels
                yield table, c, meta.column_names_to_labels[c].strip(), list(valid)


def main() -> None:
    d, meta = load()
    assert len(d) == 595
    d["id"] = range(1, len(d) + 1)
    d["cov_gender"] = d["Gender"].astype(int); d["cov_age"] = d["age_classified"].astype(int)
    d["cov_marital_status"] = d["marital_stat"].astype(int); d["cov_gpa"] = d["GPA"]
    covs = ["cov_gender", "cov_age", "cov_marital_status", "cov_gpa"]
    out = {}
    for table, (pat, valid) in BLOCKS.items():
        its = [c for c in d.columns if re.fullmatch(pat, c)]
        for c in its:
            bad = ~d[c].isin(list(valid)) & d[c].notna()
            if bad.any():
                print(f"    dropping {int(bad.sum())} out-of-range cell(s) in {c}: {sorted(d.loc[bad, c].unique())}")
                d.loc[bad, c] = pd.NA
        out[table] = (long(d, its, covs, valid=valid), pv_for(its, valid))
    assert [len(set(t[0]["item"])) for t in out.values()] == [8, 10, 10, 14]
    emit(out)


if __name__ == "__main__":
    main()
