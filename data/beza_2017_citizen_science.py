#!/usr/bin/env python3
# Source: https://doi.org/10.5061/dryad.v51bv
# DOI: 10.1371/journal.pone.0175700
#   Beza, E., Steinke, J., van Etten, J., Reidsma, P., Fadda, C., Mittra, S., Mathur, P.,
#   & Kooistra, L. (2017). What are the prospects for citizen science in agriculture?
#   Evidence from three continents on motivation and mobile telephone use of
#   resource-poor farmers. PLOS ONE, 12(5), e0175700.
# Data: Dryad 10.5061/dryad.v51bv, Beza_et.al_2017_MotivationData.csv: 426 farmers
#       (India 300, Ethiopia 94, Honduras 32) x Number, Country, HHHead(1Yes2No),
#       Age(in years), Sex(1M2F), Education Level and seven motivation items rated 1-5
#       (Contributing, Pastime, Sharing, Expectation, ExpertInteraction,
#       CommunityInteraction, Helping), plus two empty trailing columns.
# License: CC0 1.0 (Dryad record).
#
# Item text: not shipped. Plain CSV: no variable or value labels; the headers are
#   one-word motive names, not stems. The statements are in the PLOS ONE article.
#
# Table beza_2017_motivation: the seven motive items, 1-5 as stored (the article's
#   five-point importance scale); item = the source header.
# Covariates: cov_country, cov_household_head (1 yes, 2 no), cov_age, cov_sex (1 male,
#   2 female), cov_education (Education Level, 1-5 as stored).
# id: Number (the deposit's respondent number, unique 1-426).
# Note: Dryad refuses scripted downloads; see dryad_file().

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
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5061_dryad.v51bv"
ITEMS = ["Contributing", "Pastime", "Sharing", "Expectation", "ExpertInteraction",
         "CommunityInteraction", "Helping"]
COVS = {"Country": "cov_country", "HHHead(1Yes2No)": "cov_household_head",
        "Age(in years)": "cov_age", "Sex(1M2F)": "cov_sex",
        "Education Level": "cov_education"}


def main() -> None:
    d = pd.read_csv(dryad_file(RAW_DIR / "Beza_et.al_2017_MotivationData.csv"))
    assert d.shape == (426, 15) and d["Number"].is_unique
    empty = [c for c in d.columns if c.startswith("Unnamed")]
    assert len(empty) == 2 and d[empty].replace(r"^\s*$", float("nan"), regex=True).isna().all().all()
    assert set(ITEMS) | set(COVS) | set(empty) | {"Number"} == set(d.columns)
    d["id"] = d["Number"].astype(int)
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs[1:]:
        d[c] = d[c].astype("Int64")
    emit({"beza_2017_motivation": (long(d, ITEMS, covs, valid=range(1, 6)),
                                   {i: set(range(1, 6)) for i in ITEMS})})


if __name__ == "__main__":
    main()
