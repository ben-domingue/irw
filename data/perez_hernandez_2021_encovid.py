#!/usr/bin/env python3
# Source: https://zenodo.org/records/4602374 (July 2020 wave), https://zenodo.org/records/4776828 (October 2020 wave)
#         and https://zenodo.org/records/4602365 (June 2020 wave, added 2026-10-10)
# DOI: 10.5281/zenodo.4602374, 10.5281/zenodo.4776828 and 10.5281/zenodo.4602365 (datasets; the records name no paper)
#   Pérez Hernández, Víctor Hugo; Teruel Belismelis, Graciela; et al. (2021). Encuesta
#   Nacional sobre los Efectos del COVID-19 en el Bienestar de los Hogares Mexicanos
#   (ENCOVID-19), July and October 2020 [Datasets]. EQUIDE, Universidad Iberoamericana. Zenodo.
# Data: base_covid_julio2020.dta (1,584 households), base_covid_octubre2020.dta (1,592) and
#       base_covid_junio2020.dta (1,674; June asked GAD-2 p81-p82, ELCSA p76a-h and CES-D-7
#       p83-p89, in the same item order as October):
#       monthly cross-sectional telephone surveys, one adult respondent per household,
#       independent samples. Variable labels carry the Spanish stems and the value labels
#       the anchors. Shipped blocks:
#         GAD-7 (July p68-p74; October asked only GAD-2, p76-p77): 0 nunca .. 3 casi todos
#         los dias; ELCSA food insecurity, 8 adult items (July p66a-h, October p75a-h): 0/1;
#         CES-D-7 (October only, p78-p84): 0 rara vez .. 3 (5-7 dias).
#       9 = NS/NR (labelled) and an unlabelled 4 on the October GAD-2/CES-D-7 items are
#       dropped as non-responses (counts printed).
# License: CC BY 4.0 (both Zenodo records).
#
# Item text: shipped (Spanish stems from the .dta variable labels, anchors from the value
#   labels; IRW English translation). Built by
#   automated_finding/itemtext_verification/make_itemtext_perez_hernandez_2021.py.
#
# Tables (item = the instrument's item number, mapped from the variable names below;
#   cov_wave_month = july / october; the two waves are different respondents):
#   perez_hernandez_2021_gad7   gad1-gad7 (June and October rows carry gad1-gad2 only), 0-3
#   perez_hernandez_2021_elcsa  elcsa1-elcsa8, 0/1
#   perez_hernandez_2021_cesd7  cesd1-cesd7 (June and October), 0-3
# Covariates: cov_wave_month (june / july / october; three different samples), cov_sex
#   (0 hombre, 1 mujer), cov_age, cov_state (ent, 1-32), cov_household_size.
# id: 1000000 * wave (1 July, 2 October, 3 June) + the file's id.
# 2026-10-10: the June wave was added (repos batch B, lead 10.5281/zenodo.4602365). The three
#   tables gain rows; a re-upload must delete-then-recreate them, since Redivis uploads append.

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

import pyreadstat  # noqa: E402

WAVES = {  # month -> (record, file, wave number, {ship item: source var})
    "july": (4602374, "base_covid_julio2020.dta", 1,
             {**{f"gad{k}": f"p{67 + k}_ansiedad" for k in range(1, 8)},
              **{f"elcsa{k}": f"p66{c}_segalim" for k, c in enumerate("abcdefgh", 1)}}),
    "october": (4776828, "base_covid_octubre2020.dta", 2,
                {"gad1": "p76_ansiedad", "gad2": "p77_ansiedad",
                 **{f"elcsa{k}": f"p75{c}_segalim" for k, c in enumerate("abcdefgh", 1)},
                 **{f"cesd{k}": f"p{77 + k}_salud" for k in range(1, 8)}}),
    "june": (4602365, "base_covid_junio2020.dta", 3,
             {"gad1": "p81_ansiedad", "gad2": "p82_ansiedad",
              **{f"elcsa{k}": f"p76{c}_segalim" for k, c in enumerate("abcdefgh", 1)},
              **{f"cesd{k}": f"p{82 + k}_depresion" for k in range(1, 8)}}),
}
COVS = ["cov_wave_month", "cov_sex", "cov_age", "cov_state", "cov_household_size"]
TABLES = {"perez_hernandez_2021_gad7": ("gad", range(0, 4)),
          "perez_hernandez_2021_elcsa": ("elcsa", (0, 1)),
          "perez_hernandez_2021_cesd7": ("cesd", range(0, 4))}


def main() -> None:
    frames = []
    for month, (rec, fname, wave, vmap) in WAVES.items():
        raw = RAW_ROOT / f"10_5281_zenodo_{rec}"
        d, meta = pyreadstat.read_dta(str(zenodo_fetch(rec, fname, raw)))
        assert d["id"].is_unique
        d = d.rename(columns={v: k for k, v in vmap.items()})
        d["id"] = 1000000 * wave + d["id"].astype(int)
        d["cov_wave_month"] = month
        d = d.rename(columns={"sexo": "cov_sex", "edad": "cov_age", "ent": "cov_state", "tam_hog": "cov_household_size"})
        for c in ("cov_sex", "cov_age", "cov_state", "cov_household_size"):
            d[c] = pd.to_numeric(d[c], errors="coerce").astype("Int64")
        items = list(vmap)
        for it in items:
            valid = (0, 1) if it.startswith("elcsa") else (0, 1, 2, 3)
            bad = d[it].notna() & ~d[it].isin(valid)
            if bad.any():
                print(f"  {month} {it}: dropped {bad.sum()} responses coded "
                      f"{sorted(d.loc[bad, it].unique().tolist())} (NS/NR or unlabelled)")
            d.loc[bad, it] = pd.NA
        frames.append(d[["id", *COVS, *items]])
    d = pd.concat(frames, ignore_index=True)
    out = {}
    for name, (pre, valid) in TABLES.items():
        items = [c for c in d.columns if c.startswith(pre) and c[len(pre):].isdigit()]
        out[name] = (long(d, items, COVS, valid=valid), pv_for(items, valid))
    emit(out)


if __name__ == "__main__":
    main()
