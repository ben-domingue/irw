#!/usr/bin/env python3

# Source: https://zenodo.org/records/20779
# DOI: 10.5281/zenodo.20779 (dataset, 2010; Guerra-La-Torre, Jose Luis).
#   "Niveles de resiliencia en docentes de inicial, primaria y secundaria de la Region
#   Callao" (thesis data, Peru).
# Data: the single .sav, 710 Peruvian schoolteachers x 71 items on a 1-5 scale, named
#       VAR00001..VAR00071 by SPSS.
# License: CC0 1.0 (Zenodo record).
#
# Item text: NOT shipped. Both label levels checked: value labels exist for the
#   covariates (Genero, Nivel, Turno, Discapacidad and the rest) but for NONE of the 71
#   items, and no item carries a variable label either -- the columns are SPSS's own
#   VAR000NN placeholders, so the deposit documents neither stems nor anchors. The
#   questionnaire is not in the deposit. This matches its already-shipped siblings from
#   the same Callao thesis series (calla_2010_self_esteem,
#   arista_2010_achievement_motivation, vasquez_2013_reading_comprehension).
#
# One table: guerra_2010_teacher_resilience, 71 items, 1-5. The deposit gives no
# subscale structure, so the block ships as one table under the 2026-10-15 ruling that
# opaque blocks ship as-is.
#
# One data-entry error is dropped, found by checking values PER ITEM rather than on the
# merged block: VAR00019 holds a single 22 among 710 responses while its other 709 are
# 1-5, and every one of the other 70 items is 1-5 throughout. That one cell is dropped.
#
# Covariates: cov_gender, cov_level (inicial/primaria/secundaria), cov_shift,
#   cov_age, cov_disability, cov_has_degree, cov_employment_status, cov_years_service,
#   cov_grade, cov_district, cov_group.
# id: the deposit carries no respondent identifier, so id is the row index (1-710).
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_20779"
FNAME = ("2010_Guerra_Niveles_de_resiliencia_en_docentes_de_inicial_primaria_y_"
         "secundaria_de_la_Region_Callao.sav")
ITEMS = [f"VAR{i:05d}" for i in range(1, 72)]
COVS = {"Genero": "cov_gender", "Nivel": "cov_level", "Turno": "cov_shift",
        "Edad": "cov_age", "Discapacidad": "cov_disability",
        "Título": "cov_has_degree", "Situacion": "cov_employment_status",
        "Antiguedad": "cov_years_service", "Grado": "cov_grade",
        "Distrito": "cov_district", "Grupo": "cov_group"}


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(zenodo_fetch(20779, FNAME, RAW_DIR),
                                  apply_value_formats=False)
    assert len(d) == 710, len(d)
    vl = meta.variable_value_labels or {}
    assert not (set(vl) & set(ITEMS)), sorted(set(vl) & set(ITEMS))
    assert not any((meta.column_names_to_labels or {}).get(c) for c in ITEMS)
    books(list(d.columns), {"shipped": ITEMS, "covariate": list(COVS)})
    d = d.rename(columns=COVS)
    d["id"] = range(1, len(d) + 1)

    bad = d["VAR00019"] > 5
    assert bad.sum() == 1, bad.sum()
    print(f"    [dropped] 1 cell: VAR00019 = {d.loc[bad, 'VAR00019'].iloc[0]:g}, "
          f"off the 1-5 scale every other item uses")
    d.loc[bad, "VAR00019"] = pd.NA

    v = range(1, 6)
    emit({"guerra_2010_teacher_resilience":
          (long(d, ITEMS, list(COVS.values()), valid=v), pv_for(ITEMS, v))})


if __name__ == "__main__":
    main()
