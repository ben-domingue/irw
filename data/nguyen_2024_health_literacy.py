#!/usr/bin/env python3

# Source: https://zenodo.org/records/13859254
# DOI: 10.5281/zenodo.13859254 (dataset)
#   AISDL Team (2024). Resources for "BMF CP 96: The roles of healthy eating information
#   seeking ability and e-health literacy in healthy eating" [Dataset]. Zenodo.
#   Paper: Nguyen, M.-H., Sari, N. P. W. P., Mazenda, A., Ogbekene, I., Katiyatiya, C. L. F.,
#   La, V.-P., & Vuong, Q.-H. Promoting healthy eating in Iran: The roles of
#   information-seeking ability and e-health literacy in the digital age.
# Data: "HL SH data.csv": 9,775 adults in Qazvin province, Iran, surveyed January-April
#       2022. Four published instruments are deposited at the item level.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: shipped for all four tables (English, from the deposit's own CODEBOOK.docx,
#   which tabulates every SPSS variable name against its stem AND its 1-5 anchor labels).
#   The survey was administered in Iran; the codebook publishes the instruments in English
#   only and does not give the Persian wording, so the English text is what the deposit
#   supplies -- recorded as text_source=study_materials, with no translated column.
#
# Four tables, one per instrument, because each has its own anchor wording even though all
# four run 1-5:
#   nguyen_2024_helia         33 items, Never..Always -- Health Literacy Instrument for
#                             Adults: Re reading (4), Atl access (6), Und understanding (7),
#                             App appraisal (4), DM decision-making/behaviour (12).
#   nguyen_2024_swemwbs        7 items, None of the time..All of the time -- Short
#                             Warwick-Edinburgh Mental Wellbeing Scale (D1-D7).
#   nguyen_2024_sleep_hygiene  3 items, None of the time..All of the time (SHI1, SHI2, SH3;
#                             the codebook calls them SH1-SH3).
#   nguyen_2024_eheals         8 items, Strongly Disagree..Strongly agree -- eHealth
#                             Literacy Scale (EHL1-EHL8).
# Not shipped: Re, AC, Un, Ap, De (subscale means), TOTALHL, SHB, eHEALS, WEMWBS (totals).
# Covariates: cov_age, cov_gender, cov_education, cov_accommodation, cov_marital, cov_city.
# id: row index of the csv; the deposit carries no respondent identifier.
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_13859254"
HELIA = ([f"Re{i}" for i in (1, 2, 3, 4)] + [f"Atl{i}" for i in range(1, 7)]
         + [f"Und{i}" for i in range(1, 8)] + [f"App{i}" for i in range(1, 5)]
         + [f"DM{i}" for i in range(1, 13)])
SWEMWBS = [f"D{i}" for i in range(1, 8)]
SLEEP = ["SHI1", "SHI2", "SH3"]
EHEALS = [f"EHL{i}" for i in range(1, 9)]
COVS = {"age": "cov_age", "gender": "cov_gender", "education": "cov_education",
        "accomodation": "cov_accommodation", "marital": "cov_marital",
        "city": "cov_city"}


def main() -> None:
    d = pd.read_csv(zenodo_fetch(13859254, "HL SH data.csv", RAW_DIR))
    assert len(d) == 9775, len(d)
    src = list(d.columns)
    books(src, {
        "shipped": HELIA + SWEMWBS + SLEEP + EHEALS,
        "covariate": list(COVS),
        "subscale mean, not an item response": ["Re", "AC", "Un", "Ap", "De"],
        "instrument total score": ["WEMWBS", "TOTALHL", "SHB", "eHEALS"],
    })
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    d["id"] = range(1, len(d) + 1)
    v = range(1, 6)
    emit({
        "nguyen_2024_helia": (long(d, HELIA, covs, valid=v), pv_for(HELIA, v)),
        "nguyen_2024_swemwbs": (long(d, SWEMWBS, covs, valid=v), pv_for(SWEMWBS, v)),
        "nguyen_2024_sleep_hygiene": (long(d, SLEEP, covs, valid=v), pv_for(SLEEP, v)),
        "nguyen_2024_eheals": (long(d, EHEALS, covs, valid=v), pv_for(EHEALS, v)),
    })


if __name__ == "__main__":
    main()
