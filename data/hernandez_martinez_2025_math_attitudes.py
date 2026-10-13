#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/Actitudes_hacia_las_matem_ticas_y_su_relaci_n_con_el_rendimiento_acad_mico_validaci_n_de_un_instrumento_en_el_contexto_ecuatoriano_/28352018
# DOI: 10.6084/m9.figshare.28352018 (dataset; the record names no paper)
#   Hernández-Martínez, M., Posso-Yépez, M., Arciniegas-Romero, G., & Rivadeneira-Flores, J.
#   (2025). Actitudes hacia las matemáticas y su relación con el rendimiento académico:
#   validación de un instrumento en el contexto ecuatoriano [Dataset]. figshare.
# Data: DATOS_AFE.sav (3,629 rows) and DATOS_AFC.sav (2,449 rows): a stratified probability
#       sample of 6,078 Ecuadorian bachillerato students from 11 institutions, split at random
#       (V_Aleatoria <= 0.4 -> AFC, > 0.4 -> AFE) for the exploratory and confirmatory factor
#       analyses. Same 25 attitude-toward-mathematics items in both halves, 1-5 (Totalmente en
#       desacuerdo .. Totalmente de acuerdo), with an attention check (CONTROL, "choose 5")
#       and per-factor sums (SUMA_*) that are not shipped. Items are named by the original
#       five-factor design: UT utilidad (6), AN ansiedad (9), AG agrado (4), MO motivación (3),
#       CO confianza (3); the paper reduces these to three factors.
# License: CC BY 4.0 (figshare record).
#
# Item text: not shipped -- the .sav variable labels are the codes themselves ("UT1") and the
#   value labels give only the five agreement anchors; the stems are not in the deposit (the
#   paper, not located from the record, would have them).
#
# One table: hernandez_martinez_2025_math_attitudes, item = the deposit's column name, resp
# 1-5, both halves merged (identical administration: one sample randomly split) with
# cov_sample afe / afc and ids offset 100000 for the AFC half.
# Covariates: cov_institution (1-11, labelled in the file), cov_gender (1 masculino,
#   2 femenino, 4 unlabelled as coded), cov_ethnicity (1 blanco, 2 mestizo, 3 afrodescendiente,
#   4 indígena, 5 otro), cov_grade (1-3, año de bachillerato), cov_career_plan (1-7).
#   Edad is not shipped: it mixes category codes 1-7 with ages in years (13-35) and the file
#   does not say which coding applies to which row.
# id: row index within each half (+100000 for AFC).

import os
import sys
from pathlib import Path

import pandas as pd
import pyreadstat
import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import irw_validate  # noqa: E402
from irw_validate._checks import run_qc  # noqa: E402

OUT_DIR = REPO_ROOT / "automated_finding" / "irw_output"
RAW_ROOT = Path(os.environ.get("IRW_RAW_DIR", REPO_ROOT / "automated_finding" / "runs" / "raw"))
RAW_DIR = RAW_ROOT / "figshare_28352018"
UA = {"User-Agent": "IRW-Finder/1.0 (ben.domingue@gmail.com)"}


def download(url: str, path: Path) -> Path:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        r = requests.get(url, headers=UA, timeout=300)
        r.raise_for_status()
        path.write_bytes(r.content)
    return path


def figshare_fetch(article: int, fname: str, raw_dir: Path) -> Path:
    p = raw_dir / fname
    if not p.exists():
        j = requests.get(f"https://api.figshare.com/v2/articles/{article}", headers=UA, timeout=120).json()
        url = [f["download_url"] for f in j["files"] if f["name"] == fname][0]
        download(url, p)
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


ITEMS = [f"UT{i}" for i in range(1, 7)] + [f"AN{i}" for i in range(1, 10)] + \
        [f"AG{i}" for i in range(1, 5)] + [f"MO{i}" for i in range(1, 4)] + [f"CO{i}" for i in range(1, 4)]
COVS = {"INSTITUCIÓN": "cov_institution", "Género": "cov_gender", "Etnia": "cov_ethnicity",
        "Curso": "cov_grade", "CARRERAS": "cov_career_plan"}


def half(fname: str, label: str, offset: int) -> pd.DataFrame:
    d, _ = pyreadstat.read_sav(str(figshare_fetch(28352018, fname, RAW_DIR)))
    assert set(ITEMS) <= set(d.columns), fname
    d = d.reset_index(drop=True)
    d["id"] = d.index + 1 + offset
    d = d.rename(columns=COVS)
    covs = list(COVS.values())
    for c in covs:
        d[c] = d[c].astype("Int64")
    d["cov_sample"] = label
    t = d.melt(id_vars=["id", "cov_sample"] + covs, value_vars=ITEMS, var_name="item",
               value_name="resp").dropna(subset=["resp"])
    t["resp"] = t["resp"].astype(int)
    assert t["resp"].between(1, 5).all()
    return t


def main() -> None:
    afe = half("DATOS_AFE.sav", "afe", 0)
    afc = half("DATOS_AFC.sav", "afc", 100000)
    assert afe["id"].nunique() == 3629 and afc["id"].nunique() == 2449
    t = pd.concat([afe, afc], ignore_index=True)
    covs = ["cov_sample"] + list(COVS.values())
    t = t[["id", "item", "resp"] + covs].sort_values(["id", "item"]).reset_index(drop=True)
    emit({"hernandez_martinez_2025_math_attitudes": (t, {i: set(range(1, 6)) for i in ITEMS})})


if __name__ == "__main__":
    main()
