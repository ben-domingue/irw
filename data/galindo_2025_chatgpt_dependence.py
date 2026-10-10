#!/usr/bin/env python3
# Source: https://doi.org/10.7910/DVN/WTMZID
# DOI: 10.5944/ried.45497
#   Galindo-Dominguez, H., Sainz-de-la-Maza, M., Campo, L., & Losada-Iglesias, D. (2025).
#   The influence of learning motivation and procrastination on ChatGPT dependence.
#   RIED-Revista Iberoamericana de Educacion a Distancia.
# Data: Harvard Dataverse 10.7910/DVN/WTMZID (Galindo Dominguez, Hector; 2025-01-08),
#       "Main DB - Motivation-Procrastination-GPT.sav" (format=original): 467 Spanish
#       education-degree students x 27 columns -- Edad, Genero, Estudios_cursando, Curso,
#       18 five-point items whose column names are the item code run into the Spanish
#       stem, and five subscale means (*_TT).
# License: CC0 1.0 (Dataverse record).
#
# Item text: not shipped. Cheap at one level only: the SPSS variable labels carry
#   every Spanish stem ("IM01: Yo estudio por el placer que experimento cuando descubro
#   cosas nuevas ..."); the value labels are empty for all 18 items (they exist only on
#   Genero, Estudios_cursando, Curso), so the 1-5 anchors would have to come from the
#   RIED article, and the English would be IRW's.
#
# Item codes: the code before the stem in each column name and variable label (IM01,
#   EM02, PRC03, ADC05, ...), recovered from the label's "CODE:" prefix and asserted to
#   be the column name's own prefix.
# Tables (1-5 as stored):
#   galindo_2025_intrinsic_motiv   IM01-IM04  intrinsic motivation  } the three short
#   galindo_2025_extrinsic_motiv   EM01-EM02  extrinsic motivation  } learning-motivation
#   galindo_2025_amotivation       AM01-AM02  amotivation           } subscales (r < .3
#                                                                     between them)
#   galindo_2025_procrastination   PRC01-PRC05
#   galindo_2025_chatgpt_dependence ADC01-ADC05
# Skipped: GPT_TT, PRC_TT, IM_TT, EM_TT, AM_TT (subscale means).
# Covariates: cov_age (Edad), cov_gender (0 femenino, 1 masculino), cov_degree
#   (Estudios_cursando: 1 Educacion Infantil, 2 Educacion Primaria, 3 Master, 4 otro),
#   cov_year (Curso: 1-4, 5 Master).
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
import re

import pyreadstat

RAW_DIR = Path(os.environ.get("IRW_RAW_DIR",
                              REPO_ROOT / "automated_finding" / "runs" / "raw")) / "10.7910_dvn_wtmzid"
FNAME = "Main DB - Motivation-Procrastination-GPT.sav"
P = "galindo_2025_"
TABLES = {"intrinsic_motiv": "IM", "extrinsic_motiv": "EM", "amotivation": "AM",
          "procrastination": "PRC", "chatgpt_dependence": "ADC"}
COVS = {"Edad": "cov_age", "Género": "cov_gender", "Estudios_cursando": "cov_degree",
        "Curso": "cov_year"}


def main() -> None:
    d, meta = pyreadstat.read_sav(str(dv_fetch("10.7910/DVN/WTMZID", FNAME, RAW_DIR)))
    assert d.shape == (467, 27)
    lab = meta.column_names_to_labels
    code = {}
    for c in d.columns:
        m = re.match(r"([A-Z]+\d\d): ", lab.get(c) or "")
        if m:
            assert c.startswith(m.group(1)), c
            code[c] = m.group(1)
    assert len(code) == 18
    means = [c for c in d.columns if c.endswith("_TT")]
    assert set(code) | set(means) | set(COVS) == set(d.columns)
    for c in means:
        print(f"  [skip] {c}: subscale mean")
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1
    d = d.rename(columns={**COVS, **code})
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    out = {}
    for suf, pre in TABLES.items():
        its = sorted(v for v in code.values() if re.fullmatch(pre + r"\d\d", v))
        out[P + suf] = (long(d, its, covs, valid=range(1, 6)), {i: set(range(1, 6)) for i in its})
    assert sum(len(set(t["item"])) for t, _ in out.values()) == 18
    emit(out)


if __name__ == "__main__":
    main()
