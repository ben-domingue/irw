#!/usr/bin/env python3

# Source: https://zenodo.org/records/22592
# DOI: 10.5281/zenodo.22592 (dataset)
#   Purizaca-Amaya, Maria (2015, data collected 2012). Estilos educativos parentales y
#   autoestima en alumnos de quinto ciclo de primaria de una institucion educativa del
#   Callao [Dataset]. Zenodo.
# Data: the deposit's single .sav file: 100 fifth-cycle primary pupils in Callao, Peru.
#       Two instruments are deposited at the item level.
# License: CC0 1.0 (Zenodo record).
#
# Item text: not shipped. The file carries no variable labels and no value labels for any
#   item -- both levels checked, both empty -- and the deposit holds no codebook or
#   questionnaire. The wording is in the author's Spanish-language thesis, which is not
#   part of the deposit.
#
# Two tables, because the two instruments use different response widths:
#   purizaca_2012_parenting_styles  45 items, 1-4. The item codes are the deposit's own
#     and carry the subscale in their prefix: ED democratic, EA authoritarian,
#     EP permissive.
#   purizaca_2012_self_esteem       16 items, 1-5 (AUTOESTIMA1-16).
# resp cleaning: ED45 carries a single 5 where every other parenting item runs 1-4. The
#   out-of-range value is isolated to one item, which is the signature of a data-entry
#   slip rather than a wider coding scheme, so those cells are blanked.
# Not shipped: PUNTAJEAUTO, PUNTAJEDEMOC, PUNTAJEPERMISIVO, PUNTAJEAUTOESTIMA -- subscale
#   and scale totals.
# Covariates: none -- the file ships no demographics.
# id: the deposit's INFORMANTE (100 distinct over 100 rows).
#
# This is one of a set of CC0 theses deposited together from the same Peruvian collection;
# arista_2010_achievement_motivation, calla_2010_self_esteem and
# vasquez_2013_reading_comprehension are already in the IRW from the same family.
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_22592"
FNAME = ("2012_Purizaca_Estilos_educativos_parentales_y_autoestima_en_alumnos_de_"
         "quinto_ciclo_de_primaria_de_una_institucion_educativa_del_Callao.sav")
ESTEEM = [f"AUTOESTIMA{i}" for i in range(1, 17)]
TOTALS = ["PUNTAJEAUTO", "PUNTAJEDEMOC", "PUNTAJEPERMISIVO", "PUNTAJEAUTOESTIMA"]


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(zenodo_fetch(22592, FNAME, RAW_DIR),
                                  apply_value_formats=False)
    assert len(d) == 100, len(d)
    src = list(d.columns)
    parenting = [c for c in src
                 if c[:2] in ("ED", "EA", "EP") and c[2:].isdigit()]
    assert len(parenting) == 45, parenting
    books(src, {
        "shipped": parenting + ESTEEM,
        "respondent id": ["INFORMANTE"],
        "subscale or scale total": TOTALS,
    })
    n_bad = int((~d["ED45"].isin(range(1, 5))).sum())
    assert n_bad >= 1
    print(f"    [ED45] blanked {n_bad} out-of-range value(s): "
          f"{sorted(d.loc[~d['ED45'].isin(range(1, 5)), 'ED45'].unique())}")
    d.loc[~d["ED45"].isin(range(1, 5)), "ED45"] = None
    d = d.rename(columns={"INFORMANTE": "id"})
    assert d["id"].nunique() == len(d)
    emit({
        "purizaca_2012_parenting_styles":
            (long(d, parenting, [], valid=range(1, 5)), pv_for(parenting, range(1, 5))),
        "purizaca_2012_self_esteem":
            (long(d, ESTEEM, [], valid=range(1, 6)), pv_for(ESTEEM, range(1, 6))),
    })


if __name__ == "__main__":
    main()
