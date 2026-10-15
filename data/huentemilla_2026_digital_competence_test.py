#!/usr/bin/env python3
# Source: https://zenodo.org/records/22256717
# DOI: 10.5281/zenodo.22256717 (dataset, 2026-09-02; Huentemilla, Gonzalo; Manzano Leon, Ana). "Bata base
#   Gamification versus traditional teaching in the development of digital competence in higher
#   education: A quasi-experimental study".
# Data: "Gamification versus traditional teaching ... .xlsx", sheet FINAL: 104 Chilean first-year
#       university students, a 63-item digital-competence knowledge test scored 0/1 (P1_PRE..P63_PRE,
#       P1_POST..P63_POST; 99 with a pre-test, 85 with a post-test), three arms (Gamificacion, Teorico
#       Practico, Control). Sheet Hoja2 holds the 63 item stems; sheet PREVIO the chosen option text and
#       the per-item score ("1.00 / 1") from which FINAL was built. Column names carry stray spaces
#       ("P5 _PRE") that are stripped.
# License: CC BY 4.0 (Zenodo).
#
# Item text: shipped (Spanish stems from sheet Hoja2, keyed by the printed item number = Pk; IRW English in
#   the _translated columns; items 47 and 54 are cut at 255 characters in the deposit; option text not shipped -- the test is behaviour-scored 0/1 and the
#   deposit records each respondent's chosen option, not the option list).
#
# Table: huentemilla_2026_digital_competence_test, 63 items 0/1, wave 1 = pre-test, 2 = post-test
#   (184 person-waves over 104 ids = the file's ID), treat = 1 for the two taught arms (gamification
#   and traditional teaching), 0 for the no-course control; cov_condition names the arm (1 gamification,
#   2 traditional teaching, 3 control). Covariates: cov_gender (1 femenino, 2 masculino),
#   cov_school_type (1 municipal, 2 particular subvencionado, 3 particular pagado), cov_school_track
#   (1 cientifico humanista, 2 tecnico profesional), cov_mother_edu / cov_father_edu (1 basica,
#   2 media, 3 superior, 4 post grado).
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


def dans_fetch(doi: str, fname: str, raw_dir: Path) -> Path:
    """Download one original-format file of a DANS Data Station (Dataverse) dataset."""
    return dv_fetch(doi, fname, raw_dir, host="ssh.datastations.nl")
import re  # noqa: E402

RAW_DIR = RAW_ROOT / "C_57_22256717"
FNAME = ("Gamification versus traditional teaching in the development of digital competence in "
         "higher education.xlsx")
COND = {"Gamificación": 1, "Teorico Práctico": 2, "Control": 3}
EDU = {"Enseñanza Básica": 1, "Enseñanza Media": 2, "Enseñanza Superior": 3, "Post Grado": 4}


def stems():
    h = pd.read_excel(zenodo_fetch(22256717, FNAME, RAW_DIR), sheet_name="Hoja2", header=None)
    out = {}
    for s in h[0].dropna():
        s = " ".join(str(s).split())
        m = re.match(r"\s*(\d+)\.?-?\s*(.*?)\s*(\[PRE\])?\s*$", s)
        assert m, s
        out[f"P{int(m.group(1))}"] = m.group(2)
    # Items 47 and 54 are cut at 255 characters in every sheet of the deposit (an Excel import limit);
    # Hoja2 holds a 253-character copy ending in a stray digit, PREVIO's header the 255-character one.
    for k in ("P47", "P54"):
        assert len(out[k]) >= 240 and out[k][-1].isdigit(), out[k]
        out[k] = out[k][:-1].rstrip()
    assert len(out) == 63
    return out


def main() -> None:
    d = pd.read_excel(zenodo_fetch(22256717, FNAME, RAW_DIR), sheet_name="FINAL").copy()
    d = pd.concat([d], axis=1)
    d.columns = [re.sub(r"\s+", "", str(c)) for c in d.columns]
    assert len(d) == 104 and d["ID"].is_unique
    d["id"] = d["ID"].astype(int)
    d["cov_condition"] = d["Tipo_Intervención"].map(COND).astype("Int64")
    d["treat"] = (d["cov_condition"] < 3).astype(int)
    d["cov_gender"] = d["Sexo"].map({"Femenino": 1, "Masculino": 2}).astype("Int64")
    d["cov_school_type"] = d["Establecimiento_Egreso"].map(
        {"Municipal": 1, "Particular Subvencionado": 2, "Particular Pagado": 3}).astype("Int64")
    d["cov_school_track"] = d["Establecimiento_Egreso2"].map(
        {"Científico Humanista": 1, "Técnico Profesional": 2}).astype("Int64")
    d["cov_mother_edu"] = d["Estudio_máx_madre"].map(EDU).astype("Int64")
    d["cov_father_edu"] = d["Estudio_máx_padre"].map(EDU).astype("Int64")
    covs = ["cov_condition", "cov_gender", "cov_school_type", "cov_school_track", "cov_mother_edu",
            "cov_father_edu"]
    parts = []
    for w, suf in ((1, "_PRE"), (2, "_POST")):
        cols = [f"P{i}{suf}" for i in range(1, 64)]
        assert all(c in d.columns for c in cols), [c for c in cols if c not in d.columns]
        t = long(d, cols, covs, valid=(0, 1), extra=["treat"], rename={c: c[:-len(suf)] for c in cols})
        t.insert(3, "wave", w)
        parts.append(t)
    t = pd.concat(parts, ignore_index=True)
    t = t[["id", "item", "resp", "wave", "treat"] + covs].sort_values(["id", "wave", "item"]).reset_index(drop=True)
    assert t.groupby("wave")["id"].nunique().to_dict() == {1: 99, 2: 85}
    emit({"huentemilla_2026_digital_competence_test": (t, pv_for([f"P{i}" for i in range(1, 64)], (0, 1)))})


if __name__ == "__main__":
    main()
