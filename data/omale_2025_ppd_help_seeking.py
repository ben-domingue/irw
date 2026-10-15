#!/usr/bin/env python3
# Source: https://data.mendeley.com/datasets/2tzj5m5kp4
# DOI: 10.17632/2tzj5m5kp4 (dataset, 2025; the record names no published paper)
#   Omale, G., Oyesomi, K., Oladosun, M., & Bamigbolayin-Afolabi, O. (2025). Dataset on
#   socio-demographic predictors of help-seeking for postpartum depression in Northern
#   Nigeria. Mendeley Data, V1.
# Data: GLORIA MASS COM THESIS DATA.sav, 519 women in Yobe and Niger states; a Theory of Planned
#       Behaviour questionnaire on postpartum depression (PPD) with the stem in each variable
#       label and SD/D/U/A/SA value labels (1-5). Six agreement blocks ship, in questionnaire
#       order: knowledge/awareness (VAR00023-33, 11), media and interpersonal information
#       sources (VAR00079-93, 14), beliefs about PPD (VAR00094-103, 10), cultural/subjective
#       norms (VAR00105-114, 10), perceived control and barriers (VAR00115-129, 15),
#       help-seeking intention (VAR00130-140, 11). The categorical/multi-select items do not
#       ship.
# License: CC BY 4.0 (Mendeley Data record).
#
# Item text: shipped (variable labels = stems, value labels = SD/D/U/A/SA, expanded to
#   Strongly disagree .. Strongly agree; English administration). Built by
#   automated_finding/itemtext_verification/make_itemtext_omale_2025.py from stems().
#
# Tables: omale_2025_ppd_knowledge, omale_2025_ppd_info_sources, omale_2025_ppd_beliefs,
#   omale_2025_ppd_norms, omale_2025_ppd_control, omale_2025_ppd_intention; all 1-5, item =
#   the deposit's VARxxxxx name.
# Covariates: cov_state (1 Yobe, 2 Niger), cov_age (1 18-25, 2 26-33, 3 34-41, 4 42-49),
#   cov_education (1-7), cov_employment (1-6), cov_income (1-5), cov_marital_status (1-4),
#   cov_religion (1 Christianity, 2 Islam, 3 traditional), cov_children (1 none .. 4 5+).
# id: row index (no respondent identifier in the file).
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

RAW_DIR = RAW_ROOT / "10_17632_2tzj5m5kp4"
FNAME = "GLORIA MASS COM THESIS DATA.sav"
COVS = {"States": "cov_state", "Age": "cov_age", "Educational_qualification": "cov_education",
        "Employement_Status": "cov_employment", "Monthly_Income_Earning": "cov_income",
        "Marital_Status": "cov_marital_status", "Religion": "cov_religion", "Number_of_Children": "cov_children"}


def v(a, b, skip=()):
    return [f"VAR{i:05d}" for i in range(a, b + 1) if i not in skip]


BLOCKS = {"omale_2025_ppd_knowledge": v(23, 33),
          "omale_2025_ppd_info_sources": v(79, 93, skip=(92,)),
          "omale_2025_ppd_beliefs": v(94, 103),
          "omale_2025_ppd_norms": v(105, 114),
          "omale_2025_ppd_control": v(115, 129),
          "omale_2025_ppd_intention": v(130, 140)}
ANCHORS = {"SD": "Strongly disagree", "D": "Disagree", "U": "Undecided", "A": "Agree", "SA": "Strongly agree"}


def stems() -> dict:
    _, meta = pyreadstat.read_sav(str(mendeley_fetch("2tzj5m5kp4", FNAME, RAW_DIR)), metadataonly=True)
    return {t: [(c, meta.column_names_to_labels[c].strip(),
                 {int(k): ANCHORS[lab] for k, lab in meta.variable_value_labels[c].items()}) for c in items]
            for t, items in BLOCKS.items()}


def main() -> None:
    d, meta = pyreadstat.read_sav(str(mendeley_fetch("2tzj5m5kp4", FNAME, RAW_DIR)))
    assert len(d) == 519
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d.loc[d[c] == 0, c] = pd.NA
        d[c] = d[c].astype("Int64")
    emit({t: (long(d, items, covs, valid=range(1, 6)), pv_for(items, range(1, 6))) for t, items in BLOCKS.items()})


if __name__ == "__main__":
    main()
