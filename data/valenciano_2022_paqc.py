#!/usr/bin/env python3

# Source: https://zenodo.org/records/10608935
# DOI: 10.5281/zenodo.10608935 (dataset)
#   Valenciano Valcarcel, Javier; Jimenez-Loaisa, Alejandro; Rieiro, Ignacio;
#   Martinez-Martinez, Jesus (2022). Data From: Convergent validity of the Physical
#   Activity Questionnaire for Children (PAQ-C): assessing moderate-to-vigorous or
#   total physical activity? [Dataset]. Zenodo.
# Data: "Dataset_PAQ-C.sav": 430 Spanish schoolchildren aged 9-12 who wore a wGT3X-BT
#       accelerometer and completed the PAQ-C. Seven PAQ-C items are deposited at the
#       item level on a 1-5 scale (PAQ_2 .. PAQ_8).
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped (SPSS variable labels AND value labels, both present for PAQ_2..PAQ_8;
#   Spanish, as administered, with an English translation in *_translated).
#
# One table: valenciano_2022_paqc, 7 items, resp 1-5.
# Not shipped from this file:
#   PAQ_1 and PAQ_9 are the PAQ-C's two multi-part items reduced by the authors to a mean
#     over sub-parts (fractional: PAQ_1 spans 0.92-2.88, PAQ_9 1.57-5.00), so they are
#     derived scores, not item responses. The sub-part responses are not deposited.
#   PAQ_FINAL_SCORE / PAQ_FINAL_ORTODOXA / PAQ_ZFINAL_ORTODOXA and every Z* column are
#     scale scores or z-transforms of a column already handled.
#   Sedentary/Light/Moderate/Vigorous/MVPA/Total_PA/StepCount_week and the VR*/R_* columns
#     are accelerometer minute counts and their recodes -- device output, not responses.
# Covariates: cov_gender (Genero), cov_grade (Curso), cov_age (Edad).
# id: row index of the file. "Codigo" is an initials-plus-school participant code that
#   collides -- 430 rows carry only 363 distinct codes, with two codes used three times --
#   so it cannot identify a child, and the paper reports 430 participants with valid data.
#   It is dropped rather than carried: IRW's id is a row index anyway, and the column is
#   the one place in the file that could be read back towards a named child.
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_10608935"
ITEMS = [f"PAQ_{i}" for i in range(2, 9)]


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(zenodo_fetch(10608935, "Dataset_PAQ-C.sav", RAW_DIR),
                                  apply_value_formats=False)
    assert len(d) == 430, len(d)
    src = list(d.columns)
    assert all(c in src for c in ITEMS), ITEMS
    books(src, {
        "shipped": ITEMS,
        "covariate": ["Género", "Curso", "Edad"],
        "colliding participant code, superseded by the row index": ["Código"],
        "author mean over undeposited sub-parts, not an item response":
            ["PAQ_1", "PAQ_9"],
        "scale score or z-transform":
            ["PAQ_FINAL_SCORE", "PAQ_FINAL_ORTODOXA", "PAQ_ZFINAL_ORTODOXA"]
            + [c for c in src if c.startswith("Z")],
        "accelerometer minute counts and their recodes":
            ["Sedentary_week", "Light_week", "Moderate_week", "Vigorous_week",
             "MVPA_week", "Total_PA_week", "StepCount_week", "VRPAQ", "VRMA",
             "VRMA1", "MVPA", "VRMA_1", "VRSUMALVM", "VRMA_1_SLVM",
             "R_Moderate_week", "R_Vigorous_week", "R_MVPA", "VRMA2"],
    })
    d = d.rename(columns={"Género": "cov_gender", "Curso": "cov_grade",
                          "Edad": "cov_age"})
    covs = ["cov_gender", "cov_grade", "cov_age"]
    d["id"] = range(1, len(d) + 1)
    emit({"valenciano_2022_paqc":
          (long(d, ITEMS, covs, valid=range(1, 6)), pv_for(ITEMS, range(1, 6)))})


if __name__ == "__main__":
    main()
