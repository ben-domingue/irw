#!/usr/bin/env python3

# Source: https://zenodo.org/records/15628398
# DOI: 10.5281/zenodo.15628398 (dataset; the record names no published paper)
#   Maharani, Stefania Yuan; Asalla, Lydiawati Kosasih; Lesmana, Theresia (2025).
#   Questionnaire and Responses Supporting: A Study on UI/UX and E-Commerce
#   Profitability [Dataset]. Zenodo.
# Data: "How UI_UX Design Influences - suppl Material - Data.xlsx", sheet "Sheet1":
#       201 respondents, 27 TAM-based items on a 1-6 scale in seven blocks -- VD (4,
#       visual design), ND (4, navigation), EOU (4, ease of use), US (4, user
#       satisfaction), CR (3, conversion rate), AOV/AVO (4, average order value),
#       CLV (4, customer lifetime value).
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped (English stems). The deposit's own
#   "How UI_UX Design Influences - suppl material - Questionnaire .docx" tabulates every
#   item against its code (Table 1, "Variables, indicators, and questionnaire items"), so
#   the code -> stem tie is the authors' own and nothing is matched by position.
#
# One table: seven 3-4 item blocks of one 1-6 questionnaire, kept in one file.
# Covariates: none in the data file. The questionnaire lists demographic questions
#   (gender, age group, platform, shopping frequency, product category) but the response
#   workbook ships only the 27 items, so no covariate is recoverable.
# id: row index of the sheet.
#
# Note on the item codes: the deposit spells the third average-order-value item "AVO2"
# while its neighbours are "AOV1", "AOV3", "AOV4". The typo is kept as deposited -- the
# item set must match the workbook, and the item text table spells it the same way.
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

def books(all_cols, used: dict) -> None:
    """Every source column is either shipped or skipped for a printed reason."""
    seen = {}
    for reason, cols in used.items():
        for c in cols:
            assert c not in seen, (c, reason, seen[c])
            seen[c] = reason
    missing = [c for c in all_cols if c not in seen]
    assert not missing, f"unaccounted source columns: {missing}"
    extra = [c for c in seen if c not in all_cols]
    assert not extra, f"named columns not in the source: {extra}"
    for reason, cols in used.items():
        if reason != "shipped" and cols:
            print(f"    [skipped: {reason}] {len(cols)}: {', '.join(map(str, cols))[:300]}")


RAW_DIR = RAW_ROOT / "10_5281_zenodo_15628398"
FNAME = "How UI_UX Design Influences - suppl Material - Data.xlsx"
PRE = ["VD", "ND", "EOU", "US", "CR", "AOV", "AVO", "CLV"]


def main() -> None:
    d = pd.read_excel(zenodo_fetch(15628398, FNAME, RAW_DIR), sheet_name="Sheet1")
    assert len(d) == 201, len(d)
    src = list(d.columns)
    items = [c for c in src
             if any(c.startswith(p) and c[len(p):].isdigit() for p in PRE)]
    assert len(items) == 27, items
    books(src, {"shipped": items})
    d["id"] = range(1, len(d) + 1)
    emit({"maharani_2025_ecommerce_uiux":
          (long(d, items, [], valid=range(1, 7)), pv_for(items, range(1, 7)))})


if __name__ == "__main__":
    main()
