#!/usr/bin/env python3
# Source: https://doi.org/10.5061/dryad.jdfn2z3f0
# DOI: 10.12688/f1000research.125318.2
#   Purnama, S. G., Susanna, D., Achmadi, U. F., & Eryando, T. (2023). Attitude towards
#   dengue control efforts with the potential of digital technology during COVID-19:
#   partial least squares-structural equation modeling. F1000Research, 11, 1283.
# Data: Dryad 10.5061/dryad.jdfn2z3f0 (Purnama, Sang Gede; Susanna, Dewi), the article's
#       Extended data: SPSS_SEM_ok.sav, 515 adult residents of Denpasar (online Google
#       Form survey) x 46 five-point items var1a-var6i whose variable labels are the
#       English item statements; Data_Description.docx (the codebook: composite,
#       indicator, definition); README.md (the scale: "1, 2 3, 4, and 5 represent
#       strongly disagree, disagree, neutral, agree, and strongly agree");
#       characteristics.sav (sex, education, occupation of 515 respondents).
# License: CC0 1.0 (Dryad record).
#
# Item text: shipped for all six tables (English statements from the .sav variable
#   labels, checked against Data_Description.docx, whose wording is used where the
#   label is cut short (var6i); options from README.md). Label levels checked: variable
#   labels carry every statement; no value labels on any item. Language: the survey
#   ran in Denpasar, Bali; neither the article nor the deposit says which language the
#   Google Form used and only the English wording is published, so the item text is
#   the documented fallback (language = Indonesian, inferred; English base fields).
#   Built by automated_finding/itemtext_verification/make_itemtext_purnama_2023.py.
#
# Tables (1-5 as stored; item = the deposit's variable name; composites from
#   Data_Description.docx; the indicators it stars as dropped from the PLS model for
#   multicollinearity -- var2b, 2d, 3e-3h, 4h, 5c, 6g, 6h -- are kept, they were
#   administered):
#   purnama_2023_program_benefit   var1a-var1g  perception of program benefits
#   purnama_2023_threat            var2a-var2f  perception of being threatened with dengue
#   purnama_2023_constraints       var3a-var3h  perception of program constraints
#   purnama_2023_digital_need      var4a-var4h  perception of digital technology needs
#   purnama_2023_environment       var5a-var5h  perception of environmental factors
#   purnama_2023_attitude          var6a-var6i  attitude towards dengue control
# Not used: characteristics.sav. It has the same 515 rows but no respondent key, and
#   nothing in the deposit or the article says its rows are in the same order as
#   SPSS_SEM_ok.sav, so it is not joined.
# id: row index of SPSS_SEM_ok.sav (no id column).
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
import pyreadstat

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.5061_dryad.jdfn2z3f0"
P = "purnama_2023_"
TABLES = {"program_benefit": "var1", "threat": "var2", "constraints": "var3",
          "digital_need": "var4", "environment": "var5", "attitude": "var6"}
SIZES = {"var1": 7, "var2": 6, "var3": 8, "var4": 8, "var5": 8, "var6": 9}


def main() -> None:
    d, _ = pyreadstat.read_sav(str(dryad_file(RAW_DIR / "SPSS_SEM_ok.sav")))
    assert d.shape == (515, 46)
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    out = {}
    seen = []
    for suf, pre in TABLES.items():
        its = [c for c in d.columns if c.startswith(pre)]
        assert len(its) == SIZES[pre], (pre, its)
        seen += its
        out[P + suf] = (long(d, its, [], valid=range(1, 6)), {i: set(range(1, 6)) for i in its})
    assert sorted(seen) == sorted(c for c in d.columns if c != "id")
    emit(out)


if __name__ == "__main__":
    main()
