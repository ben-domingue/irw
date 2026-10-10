#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/M93O7B
# DOI: 10.7910/DVN/M93O7B (dataset; the record names no paper)
#   Gunandran, Sarrvesh; Mahalingam, Dinesh (2023). Quality of life in low-income
#   households among residents in Perumahan Awam Sri Johor, Cheras. Harvard Dataverse.
# Data: QoL2023.xlsx (format=original): 170 adult residents of a low-cost public housing
#       estate in Kuala Lumpur (Google Form survey run by third-year medical students,
#       5-6 August 2023) x 44 columns: ten background columns, Q1-Q26 and four domain
#       totals with their percentage conversions.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped -- rights. Headers are Q1-Q26 only, and WHOQOL is a `block`
#   row in itemtext/instrument_rights_register.csv.
#
# Table gunandran_2023_whoqol_bref: Q1-Q26, 1-5 as stored (WHOQOL-BREF numbering).
#   The deposit's domain totals equal the plain sums of the stored items (physical =
#   Q3+Q4+Q10+Q15+Q16+Q17+Q18, psychological = Q5+Q6+Q7+Q11+Q19+Q26, social =
#   Q20-Q22, environment = Q8+Q9+Q12+Q13+Q14+Q23-Q25; asserted), so the three
#   negatively worded items Q3, Q4 and Q26 are either stored already reversed or were
#   never reversed; their item-rest correlations are about zero (-.08 to .08), so the
#   data cannot tell which. Shipped as stored.
# Skipped: the four domain totals and four percentage scores; Smoker Status (a
#   collapse of Smoking Status, which ships); Age Group (Age ships).
# Covariates (as worded in the file): cov_gender, cov_age, cov_ethnicity, cov_education,
#   cov_marital, cov_income (household income band, RM), cov_b40 (B40 sub-band),
#   cov_smoking (smoker / vaper / both / non-smoker).
# id: row index (no id column).

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
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def emit(tables: dict) -> None:
    names = list(tables)
    assert len(set(names)) == len(names) and max(map(len, names)) <= 40, names
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, (t, pv) in tables.items():
        assert not t.duplicated(["id", "item"] + (["wave"] if "wave" in t else [])).any()
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


def long(d: pd.DataFrame, items: list, covs: list, valid=None, extra=()) -> pd.DataFrame:
    """Melt, drop missing, check integer codes inside `valid`, order columns."""
    t = d.melt(id_vars=["id", *extra] + covs, value_vars=items, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = pd.to_numeric(t["resp"])
    assert (t["resp"] % 1 == 0).all(), "fractional resp"
    t["resp"] = t["resp"].astype(int)
    if valid is not None:
        bad = t[~t["resp"].isin(list(valid))]
        assert bad.empty, bad["resp"].value_counts().to_dict()
    t = t[["id", "item", "resp", *extra] + covs]
    return t.sort_values(["id", "item"]).reset_index(drop=True)


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


def dryad_file(path: Path) -> Path:
    """Dryad file downloads need a browser session (an Anubis challenge, then a 403 to
    plain HTTP clients), so the file is placed by hand: open the dataset page in a
    browser, download the file, and put it at `path`."""
    if not path.exists():
        raise SystemExit(f"missing {path}: download it from the Dryad dataset page "
                         "(plain HTTP downloads are refused) and rerun")
    return path

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_m93o7b"
ITEMS = [f"Q{i}" for i in range(1, 27)]
COVS = {"Gender": "cov_gender", "Age": "cov_age", "Ethnicity": "cov_ethnicity",
        "Education Level": "cov_education", "Marital Status": "cov_marital",
        "Household Income (RM)": "cov_income", "B40 Grouping": "cov_b40",
        "Smoking Status": "cov_smoking"}
DOMAINS = {"Total Physical Score": [3, 4, 10, 15, 16, 17, 18],
           "Total Psychological Score": [5, 6, 7, 11, 19, 26],
           "Total Social Score": [20, 21, 22],
           "Total Environment Score": [8, 9, 12, 13, 14, 23, 24, 25]}
SKIP = list(DOMAINS) + ["Physical Percentage", "Psychological Percentage",
                        "Social Percentage", "Environment Percentage", "Smoker Status",
                        "Age Group"]


def main() -> None:
    d = pd.read_excel(dv_fetch("10.7910/DVN/M93O7B", "QoL2023.xlsx", RAW_DIR))
    assert d.shape == (170, 44)
    assert set(ITEMS) | set(COVS) | set(SKIP) == set(d.columns)
    for dom, nums in DOMAINS.items():
        assert (d[[f"Q{i}" for i in nums]].sum(axis=1) == d[dom]).all(), dom
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    emit({"gunandran_2023_whoqol_bref": (long(d, ITEMS, covs, valid=range(1, 6)),
                                         {i: set(range(1, 6)) for i in ITEMS})})


if __name__ == "__main__":
    main()
