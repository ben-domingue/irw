#!/usr/bin/env python3
# Source: https://zenodo.org/records/22040756
# DOI: 10.5281/zenodo.22040756 (dataset; the record names no published paper)
#   Bi, Y., Li, L., & Han, D. (2026). Anonymized Dataset for "From AI Literacy to the
#   Creative Application of AI in Teaching: Serial Mediation through Trust Calibration and
#   Agency Maintenance among Preservice Teachers". Zenodo.
# Data: AI_Literacy_618_Final_Public_Dataset.xlsx, sheet Public_Data: 618 Chinese preservice
#       teachers (single institution), the 30 substantive items Q7-Q36 on a 1-5 Likert scale,
#       no missing values. The six demographic items were withheld by the depositors. The
#       Data_Dictionary sheet gives each item's Chinese wording; the blocks below follow the
#       four constructs the title names, in questionnaire order (Q7-Q22 AI literacy: knowledge
#       7-10, application 11-16, ethics/verification 17-22; Q23-Q26 trust calibration; Q27-Q31
#       agency maintenance; Q32-Q36 creative application of AI in teaching).
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped (the Data_Dictionary sheet's Chinese stems, with IRW English translations
#   in item_text_translated; the sheet gives no option labels beyond "1-5 Likert response", so
#   option_text is blank; built by
#   automated_finding/itemtext_verification/make_itemtext_bi_2026.py, which imports stems()).
#
# Tables (item = the deposit's Q-code, resp 1-5): bi_2026_ai_literacy (16 items),
#   bi_2026_trust_calibration (4), bi_2026_agency_maintenance (5), bi_2026_creative_ai_use (5).
# Covariates: none (withheld at source).
# id: the deposit's anonymous_id (1-618).
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

RAW_DIR = RAW_ROOT / "10_5281_zenodo_22040756"
FNAME = "AI_Literacy_618_Final_Public_Dataset.xlsx"
BLOCKS = {  # table suffix -> (item numbers, instrument)
    "ai_literacy": (range(7, 23), "AI literacy (knowledge, application, evaluation and ethics of AI in teaching)"),
    "trust_calibration": (range(23, 27), "Trust calibration toward AI-generated teaching content"),
    "agency_maintenance": (range(27, 32), "Agency maintenance when co-preparing lessons with AI"),
    "creative_ai_use": (range(32, 37), "Creative application of AI in teaching"),
}


def stems() -> dict:
    """Q-code -> Chinese stem from the deposit's Data_Dictionary sheet (leading number stripped)."""
    dd = pd.read_excel(zenodo_fetch(22040756, FNAME, RAW_DIR), sheet_name="Data_Dictionary")
    out = {}
    for _, r in dd.iterrows():
        if str(r["Variable"]).startswith("Q"):
            out[r["Variable"]] = re.sub(r"^\d+、", "", str(r["Source questionnaire item"])).strip()
    return out


def main() -> None:
    d = pd.read_excel(zenodo_fetch(22040756, FNAME, RAW_DIR), sheet_name="Public_Data")
    assert len(d) == 618 and d["anonymous_id"].is_unique
    d["id"] = d["anonymous_id"].astype(int)
    out = {}
    for suffix, (nums, _) in BLOCKS.items():
        items = [f"Q{k}" for k in nums]
        out[f"bi_2026_{suffix}"] = (long(d, items, [], valid=range(1, 6)), pv_for(items, range(1, 6)))
    emit(out)


if __name__ == "__main__":
    main()
