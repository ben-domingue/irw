#!/usr/bin/env python3
# Source: https://figshare.com/articles/dataset/_/33187878
# DOI: 10.6084/m9.figshare.33187878.v2 (dataset, 2026-08-11; Guerrero-Zambrano, Marcos; Castro-Castillo,
#   Graciela Josefina; Delgado Santillan, David Antonio). "Base de datos desidentificada sobre uso
#   pedagogico de inteligencia artificial, gestion de datos educativos y adaptacion e inclusion en
#   docentes".
# Data: "Baseanonimizada.xlsx", sheet Datos: 334 Ecuadorian teachers (Costa, Sierra, Amazonia): UP1-3
#       pedagogical use of AI, GD1-3 educational data management, AI1-3 technology-supported adaptation
#       and inclusion (1 totalmente en desacuerdo - 5 totalmente de acuerdo). Means/sums not shipped.
#       Sheet Codigos_y_claves prints every stem and the anchor labels.
# License: CC BY 4.0 (figshare).
#
# Item text: shipped (Spanish stems and anchors from sheet Codigos_y_claves, keyed by column name; IRW
#   English in the _translated columns).
#
# Tables: guerrero_zambrano_2026_ai_use (3), guerrero_zambrano_2026_data_mgmt (3),
#   guerrero_zambrano_2026_adaptation (3); 334 ids (row index; ID_publico not carried).
# Covariates: cov_region (1 Costa, 2 Sierra, 3 Amazonia), cov_zone (1 urbana, 2 rural), cov_gender
#   (1 masculino, 2 femenino), cov_education (1 tecnologo, 2 tercer nivel, 3 cuarto nivel),
#   cov_years_experience (1 0-5, 2 6-10, 3 11-20, 4 21+), cov_teaching_level (1 inicial, 2 basica,
#   3 bachillerato, 4 superior).
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
RAW_DIR = RAW_ROOT / "C_72_33187878"
FNAME = "Baseanonimizada.xlsx"
BLOCKS = {"ai_use": ["UP1", "UP2", "UP3"], "data_mgmt": ["GD1", "GD2", "GD3"],
          "adaptation": ["AI1", "AI2", "AI3"]}
COVS = {"Región": ("cov_region", {"Costa": 1, "Sierra": 2, "Amazonía": 3}),
        "Zona": ("cov_zone", {"Urbana": 1, "Rural": 2}),
        "Género": ("cov_gender", {"Masculino": 1, "Femenino": 2}),
        "Nivel_instrucción": ("cov_education", {"Tecnólogo": 1, "Tercer nivel": 2, "Cuarto nivel": 3}),
        "Años_experiencia": ("cov_years_experience", {"0 a 5 años": 1, "6 a 10 años": 2, "11 a 20 años": 3, "21 años o más": 4}),
        "Nivel_imparte": ("cov_teaching_level", {"Educación Inicial": 1, "Educación básica": 2, "Bachillerato": 3, "Superior": 4})}


def codebook():
    """{code: stem} and {code: anchor} from sheet Codigos_y_claves."""
    cb = pd.read_excel(figshare_fetch(33187878, FNAME, RAW_DIR), sheet_name="Codigos_y_claves", header=None)
    stems, anchors = {}, {}
    for _, r in cb.iterrows():
        k = str(r[0]).strip()
        if k in sum(BLOCKS.values(), []):
            stems[k] = str(r[2]).strip()
        elif k in {"1", "2", "3", "4", "5"} and isinstance(r[1], str):
            anchors[int(k)] = r[1].strip()
    assert len(stems) == 9 and len(anchors) == 5, (stems, anchors)
    return stems, anchors


def main() -> None:
    d = pd.read_excel(figshare_fetch(33187878, FNAME, RAW_DIR), sheet_name="Datos")
    assert len(d) == 334
    d["id"] = d.index + 1
    covs = []
    for s, (c, m) in COVS.items():
        d[c] = d[s].map(m).astype("Int64")
        assert d[c].notna().all(), (c, d[s].unique())
        covs.append(c)
    out = {}
    for k, cols in BLOCKS.items():
        out[f"guerrero_zambrano_2026_{k}"] = (long(d, cols, covs, valid=range(1, 6)), pv_for(cols, range(1, 6)))
    emit(out)


if __name__ == "__main__":
    main()
