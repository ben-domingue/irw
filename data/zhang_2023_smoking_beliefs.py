#!/usr/bin/env python3
# Source: https://doi.org/10.3389/fpsyg.2023.1260561.s002 (Frontiers Supplementary Table 1, figshare)
# DOI: 10.3389/fpsyg.2023.1260561
#   Zhang, Liu, Li, Yuan et al. (2023). How do self-exempt beliefs affect intentions to
#   quit smoking? An exploration of the mediating role of threat appraisal and coping
#   appraisal. Frontiers in Psychology 14: 1260561.
# Data: Table_1_... .xlsx, sheet "Dataset S1": 488 current male smokers (Gender all 1), a
#       protection-motivation-theory questionnaire on 1-7 scales plus the self-exempt
#       beliefs scale and a 4-item 1-5 block (IQS, the deposit's code; intention to quit).
#       Codes: PS perceived severity, PV perceived vulnerability, IR intrinsic rewards, ER
#       extrinsic rewards (threat appraisal, 3 each); RE response efficacy, SE self-efficacy,
#       RC response costs (coping appraisal, 3 each); SB skeptic (5), BB bulletproof (5),
#       WB worth-it (3), JB jungle (4) self-exempt beliefs; TA/CA are composite scores.
# License: CC BY 4.0 (Frontiers article and its supplementary material).
#
# Item text: not shipped. Headers are codes only; the item wording is in the article's
#   tables, not in the deposit (positional mapping would be needed).
#
# Tables (item = the deposit's column code): zhang_2023_self_exempt (SB/BB/WB/JB, 17, 1-7),
#   zhang_2023_threat_appraisal (PS/PV/IR/ER, 12, 1-7), zhang_2023_coping_appraisal
#   (RE/SE/RC, 9, 1-7), zhang_2023_quit_intention (IQS1-4, 1-5).
# Covariates (integer codes as deposited): cov_age_group, cov_education, cov_resident,
#   cov_occupation, cov_chronic_disease, cov_cigarettes_per_day (Amount).
# id: the deposit's "Number".

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

RAW_DIR = RAW_ROOT / "10_3389_fpsyg_2023_1260561_s002"
FNAME = ("Table_1_How do self-exempt beliefs affect intentions to quit smoking? An exploration of the "
         "mediating role of threat appraisal and coping appraisal.xlsx")
URL = "https://doi.org/10.3389/fpsyg.2023.1260561.s002"
COVS = {"Age": "cov_age_group", "Education": "cov_education", "Resident": "cov_resident",
        "Occupation": "cov_occupation", "Chronic": "cov_chronic_disease", "Amount": "cov_cigarettes_per_day"}
BLOCKS = {"zhang_2023_self_exempt": (["SB", "BB", "WB", "JB"], range(1, 8)),
          "zhang_2023_threat_appraisal": (["PS", "PV", "IR", "ER"], range(1, 8)),
          "zhang_2023_coping_appraisal": (["RE", "SE", "RC"], range(1, 8)),
          "zhang_2023_quit_intention": (["IQS"], range(1, 6))}


def main() -> None:
    p = RAW_DIR / FNAME
    if not p.exists():
        download(URL, p)
    d = pd.read_excel(p, sheet_name="Dataset S1")
    assert len(d) == 488 and d["Number"].is_unique and (d["Gender"] == 1).all()
    d = d.rename(columns={"Number": "id", **COVS})
    covs = list(COVS.values())
    out = {}
    for name, (pres, valid) in BLOCKS.items():
        items = [c for c in d.columns if any(c.startswith(p) and c[len(p):].isdigit() for p in pres)]
        out[name] = (long(d, items, covs, valid=valid), pv_for(items, valid))
    assert [len(out[n][1]) for n in BLOCKS] == [17, 12, 9, 4]
    emit(out)


if __name__ == "__main__":
    main()
