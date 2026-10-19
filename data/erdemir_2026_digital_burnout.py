#!/usr/bin/env python3

# Source: https://zenodo.org/records/18595672
# DOI: 10.5281/zenodo.18595672 (dataset; the record names no published paper)
#   Erdemir, N. (2026). Digital burnout in teachers [Dataset]. Zenodo.
# Data: "CFA.sav" and "EFA.xlsx", 624 Turkish teachers x 10 digital-burnout items on a
#       1-5 scale. The two files are the SAME data under different column names: this
#       script asserts the 624x10 blocks are element-wise identical (DB1-10 in the
#       .sav, M1-10 in the .xlsx) and ships ONE table rather than a spurious pair.
#       The .sav is read because it is the format that could carry labels.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: NOT shipped. Both label levels checked and BOTH are empty in the .sav --
#   no variable labels and no value labels for any of the 13 columns -- and the .xlsx
#   headers are the bare codes. The deposit holds no codebook or questionnaire. The
#   wording is in the paper, which this record does not name.
#
# One table: erdemir_2026_digital_burnout, 10 items, 1-5.
# Covariates: cov_gender (CINSIYET), cov_seniority (KIDEM), cov_daily_tech_use_hours
#   (the deposit's "Gunluk ortalama dijital teknoloji araclarini kullanim sureniz",
#   self-reported average daily hours of digital-technology use, as a coded band).
# id: neither file carries a respondent identifier, so id is the row index (1-624).
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_18595672"
ITEMS = [f"DB{i}" for i in range(1, 11)]
TECH = "Günlükortalamadijitalteknolojiaraçlarınıkullanımsüreniz"
COVS = {"CİNSİYET": "cov_gender", "KIDEM": "cov_seniority",
        TECH: "cov_daily_tech_use_hours"}


def main() -> None:
    import pyreadstat
    sav = zenodo_fetch(18595672, "CFA.sav", RAW_DIR)
    d, meta = pyreadstat.read_sav(sav, apply_value_formats=False)
    assert len(d) == 624, len(d)
    # The two deposited files are the same data; prove it rather than assume it.
    xl = pd.read_excel(zenodo_fetch(18595672, "EFA.xlsx", RAW_DIR), sheet_name=0)
    a = d[ITEMS].to_numpy()
    b = xl[[f"M{i}" for i in range(1, 11)]].to_numpy()
    assert a.shape == b.shape and (a == b).all(), \
        "CFA.sav and EFA.xlsx differ; they are not the same 624 respondents"
    assert not (meta.column_names_to_labels or {}).get("DB1")
    assert not (meta.variable_value_labels or {})
    books(list(d.columns), {"shipped": ITEMS, "covariate": list(COVS)})
    d = d.rename(columns=COVS)
    d["id"] = range(1, len(d) + 1)
    v = range(1, 6)
    emit({"erdemir_2026_digital_burnout":
          (long(d, ITEMS, list(COVS.values()), valid=v), pv_for(ITEMS, v))})


if __name__ == "__main__":
    main()
