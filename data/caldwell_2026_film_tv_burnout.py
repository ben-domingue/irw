#!/usr/bin/env python3
# Source: https://zenodo.org/records/22679502
# DOI: 10.5281/zenodo.22679502 (dataset, 2026; Caldwell). The record names a manuscript on occupational
#   burnout in the UK film and television industry (no DOI given).
# Data: burnout_uk_film_tv_data.csv, 415 UK film/TV workers (online survey, May-July 2022), responses
#       as option labels: MBI-GS B1EE-B16PE (16 items; Never .. Every day -> 0-6), SF-12 v1 Q1-Q12
#       (item-specific option sets -> 1-5 / 1-3 / 1-2 / 1-6 in the printed option order), STIG-9
#       MHS1-9 (Disagree .. Agree -> 0-3), EIJQI JQ1-11 (Strongly Disagree .. Strongly Agree -> 0-4),
#       SEQ-DoD-s SE1-16 (harassment subsample n = 297; Never .. Very often -> 0-4). The *r reversed
#       copies, the GH1_/PF/RP/RE/BP/MH/VT/SF dummy columns and all totals are not shipped.
# License: CC BY 4.0 (Zenodo; README).
#
# Item text: not shipped -- the file carries codes and option labels only, no stems and no codebook
#   beyond the README's variable list; MBI-GS and SF-12 are blocked in the rights register anyway.
#
# Tables: caldwell_2026_mbi_gs (415 x 16, 0-6), caldwell_2026_sf12 (415 x 12, item-specific sets),
#   caldwell_2026_stig9 (415 x 9, 0-3), caldwell_2026_eijqi (415 x 11, 0-4), caldwell_2026_seq_dod
#   (297 x 16, 0-4).
# Covariates: cov_age, cov_gender, cov_employment, cov_hours_worked, cov_disability,
#   cov_leaving_industry (labels as deposited).
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

RAW_DIR = RAW_ROOT / "zn_22679502"
FNAME = "burnout_uk_film_tv_data.csv"
FREQ = {"Never": 0, "A few times a year or less": 1, "Once a month or less": 2, "A few times a month": 3,
        "Once a week": 4, "A few times a week": 5, "Every day": 6, "Everyday": 6}
AGREE4 = {"Disagree": 0, "Somewhat Disagree": 1, "Somewhat Agree": 2, "Agree": 3}
AGREE5 = {"Strongly Disagree": 0, "Disagree": 1, "Neutral": 2, "Agree": 3, "Strongly Agree": 4}
OFTEN = {"Never": 0, "Once or twice": 1, "Sometimes": 2, "Often": 3, "Very often": 4}
LIM = {"Yes limited a lot": 1, "Yes limited a little": 2, "No not limited at all": 3}
YN = {"Yes": 1, "No": 2}
T6 = {"All of the time": 1, "Most of the time": 2, "A good bit of the time": 3, "Some of the time": 4,
      "A little of the time": 5, "None of the time": 6}
SF12 = {"Q1": {"Excellent": 1, "Very Good": 2, "Good": 3, "Fair": 4, "Poor": 5},
        "Q2": LIM, "Q3": LIM, "Q4": YN, "Q5": YN, "Q6": YN, "Q7": YN,
        "Q8": {"Not at all": 1, "A little bit": 2, "Moderately": 3, "Quite a bit": 4, "Extremely": 5},
        "Q9": T6, "Q10": T6, "Q11": T6,
        "Q12": {"All of the time": 1, "Most of the time": 2, "Some of the time": 3, "A little of the time": 4, "None of the time": 5}}
MBI = ["B1EE", "B2EE", "B3EE", "B4EE", "B5PE", "B6EE", "B7PE", "B8DP", "B9DP", "B10PE", "B11PE", "B12PE",
       "B13DP", "B14DP", "B15DP", "B16PE"]
STIG = [f"MHS{i}" for i in range(1, 10)]
JQ = [f"JQ{i}" for i in range(1, 12)]
SE = [f"SE{i}" for i in range(1, 17)]
COVS = {"Age": "cov_age", "Gender": "cov_gender", "Employment": "cov_employment", "Hours_Worked": "cov_hours_worked",
        "Disability": "cov_disability", "Leaving_the_Industry": "cov_leaving_industry"}


def recode(d, cols, mapping):
    for c in cols:
        m = mapping[c] if isinstance(mapping, dict) and c in mapping else mapping
        bad = set(d[c].dropna().unique()) - set(m)
        assert not bad, (c, bad)
        d[c] = d[c].map(m)


def main() -> None:
    d = pd.read_csv(zenodo_fetch(22679502, FNAME, RAW_DIR))
    assert len(d) == 415
    d["id"] = d.index + 1
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    recode(d, MBI, FREQ)
    recode(d, STIG, AGREE4)
    recode(d, JQ, AGREE5)
    recode(d, SE, OFTEN)
    recode(d, list(SF12), SF12)
    # reversed copies in the file confirm the direction of the raw coding
    assert (d["B5PE"] + d["B5rPE"] == 6).all() and (d["JQ8"] + d["JQ8r"] == 4).all()
    sf = long(d, list(SF12), covs)
    emit({"caldwell_2026_mbi_gs": (long(d, MBI, covs, valid=range(0, 7)), pv_for(MBI, range(0, 7))),
          "caldwell_2026_sf12": (sf, {q: set(m.values()) for q, m in SF12.items()}),
          "caldwell_2026_stig9": (long(d, STIG, covs, valid=range(0, 4)), pv_for(STIG, range(0, 4))),
          "caldwell_2026_eijqi": (long(d, JQ, covs, valid=range(0, 5)), pv_for(JQ, range(0, 5))),
          "caldwell_2026_seq_dod": (long(d, SE, covs, valid=range(0, 5)), pv_for(SE, range(0, 5)))})


if __name__ == "__main__":
    main()
