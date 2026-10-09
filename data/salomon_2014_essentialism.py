#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/IH-ESS-SEM
# DOI: 10.1177/0146167214541659
#   Salomon, E., & Cimpian, A. (2014). The Inherence Heuristic as a Source of
#   Essentialist Thought. Personality and Social Psychology Bulletin, 40(10), 1297-1315.
# Data: Harvard Dataverse 10.7910/DVN/IH-ESS-SEM (Salomon, Erika; Cimpian, Andrei;
#       2014-06-25), ih-ess-sem.dta: the 240 MTurk respondents of Study 1 x 117 columns
#       -- Qualtrics ResponseID and start/end times, four scale averages, EXCLUDE (the
#       authors' exclusion code) and IHCatchWrong, Country (country of the IP address;
#       the IP itself was removed by the authors), the items, an attention check and four
#       free-text debriefing answers. Stata variable labels carry the item statements,
#       cut at Stata's 80 characters.
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Variable labels carry the statements for the IH, No et al. and
#   Rhodes & Gelman items but several are truncated at 80 characters ("If intelligent
#   organisms were discovered ... have two arms and two legs."); the 60 HRE items are
#   labelled only "HRE <dimension> <group>"; no value labels on any item (only EXCLUDE
#   and Attention have them); the 1-9 anchors are in the article. The full wording is in
#   the article's appendix (and PsycTESTS 10.1037/t48268-000 for the IH scale).
#
# Tables (1-9 as stored; item = the deposit's variable name):
#   salomon_2014_inherence            IH01Stop-IH15Sounds, the 15 Inherence Heuristic
#                                     Scale items
#   salomon_2014_race_essentialism    No01BioDet-No08Fluid (No et al. race lay theories;
#                                     No05-No08 are worded in the social-constructionist
#                                     direction and stored as worded)
#   salomon_2014_gender_essentialism  RGG01Impor-RGG08Femal (Rhodes & Gelman, gender)
#   salomon_2014_ethnic_essentialism  RGE01Impor-RGE07Under (Rhodes & Gelman, ethnicity)
#   salomon_2014_hre_informative      HREInf_*  } Haslam, Rothschild & Ernst essentialism
#   salomon_2014_hre_underlying       HREUnd_*  } dimensions, each rated for the same 12
#   salomon_2014_hre_uniformity       HREUni_*  } social categories (girls, Catholics, poor
#   salomon_2014_hre_innateness       HREInn_*  } people, athletes, shy, messy,
#   salomon_2014_hre_stability        HRESta_*  } schizophrenics, Asians, vegetarians,
#                                                 optimists, smart people, musicians)
# Skipped: IHC1Kill-IHC4Reproduce (the IH scale's four catch items; their error count
#   ships as cov_catch_wrong), IHAvg/HREAvg/RGAvg/NoAvg (averages), ResponseID (a Qualtrics
#   response ID; replaced by the row index), StartDate/EndDate, Country, Attention, and the
#   free-text Odd, Purpose, MoreEye, Comments.
# Covariates: cov_exclude (EXCLUDE: 0 include, 1 more than one catch item wrong,
#   2 non-US IP address, 3 missing data; 10 respondents are flagged, all are shipped and
#   the code lets a user apply the authors' rule), cov_catch_wrong (IHCatchWrong, 0-3).
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
import re

import pyreadstat

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_ih-ess-sem"
P = "salomon_2014_"
TABLES = {"inherence": r"IH\d\d", "race_essentialism": r"No\d\d", "gender_essentialism": r"RGG\d\d",
          "ethnic_essentialism": r"RGE\d\d", "hre_informative": r"HREInf_", "hre_underlying": r"HREUnd_",
          "hre_uniformity": r"HREUni_", "hre_innateness": r"HREInn_", "hre_stability": r"HRESta_"}
SIZES = {"inherence": 15, "race_essentialism": 8, "gender_essentialism": 8,
         "ethnic_essentialism": 7}
COVS = {"EXCLUDE": "cov_exclude", "IHCatchWrong": "cov_catch_wrong"}
SKIP = ["IHC1Kill", "IHC2Head", "IHC3Hotels", "IHC4Reproduce", "IHAvg", "HREAvg", "RGAvg",
        "NoAvg", "ResponseID", "StartDate", "EndDate", "Country", "Attention", "Odd",
        "Purpose", "MoreEye", "Comments"]


def main() -> None:
    d, _ = pyreadstat.read_dta(str(dv_fetch("10.7910/DVN/IH-ESS-SEM", "ih-ess-sem.dta", RAW_DIR)))
    assert d.shape == (240, 117) and d["ResponseID"].is_unique
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    groups = {}
    for suf, pat in TABLES.items():
        its = [c for c in d.columns if re.match(pat, c)]
        assert len(its) == SIZES.get(suf, 12), (suf, its)
        groups[suf] = its
    items = [c for its in groups.values() for c in its]
    assert set(items) | set(COVS) | set(SKIP) | {"id"} == set(d.columns)
    for c in items:  # two items were stored as text because of one blank cell
        d[c] = pd.to_numeric(d[c].replace("", float("nan")))
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    out = {P + suf: (long(d, its, covs, valid=range(1, 10)), {i: set(range(1, 10)) for i in its})
           for suf, its in groups.items()}
    emit(out)


if __name__ == "__main__":
    main()
