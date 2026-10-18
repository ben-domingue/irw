#!/usr/bin/env python3

# Source: https://zenodo.org/records/13117893
# DOI: 10.5281/zenodo.13117893 (dataset; the record names no published paper)
#   Syahputra, W., Widhiastuti, I., Baydhowi, Yundianto, D., & Ali, M. (2024).
#   Psychometric properties of the prosocial behavior scale in a sample of Indonesian
#   adolescents [Dataset]. Zenodo.
# Data: "datariset.xlsx": 742 Indonesian adolescents x 16 prosocial-behaviour items,
#       each on a 1-4 scale.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: NOT shipped. The .xlsx headers are positional ("Item1".."Item16") and the
#   deposit holds no codebook, questionnaire or README -- so the published instrument
#   is needed to know what was asked. The wording is in the paper, which this record
#   does not name.
#
# One table: syahputra_2024_prosocial, 16 items, 1-4.
# Covariates: cov_age, cov_gender. cov_age runs 3-19; the deposit documents no coding
#   for it, so it ships as the source recorded it rather than being reinterpreted.
# id: the deposit carries no respondent identifier, so id is the row index (1-742).
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_13117893"
ITEMS = [f"Item{i}" for i in range(1, 17)]
COVS = {"Age": "cov_age", "Gender": "cov_gender"}


def main() -> None:
    p = zenodo_fetch(13117893, "datariset.xlsx", RAW_DIR)
    d = pd.read_excel(p, sheet_name=0)
    assert len(d) == 742, len(d)
    books(list(d.columns), {"shipped": ITEMS, "covariate": list(COVS)})
    d = d.rename(columns=COVS)
    d["id"] = range(1, len(d) + 1)
    v = range(1, 5)
    emit({"syahputra_2024_prosocial":
          (long(d, ITEMS, list(COVS.values()), valid=v), pv_for(ITEMS, v))})


if __name__ == "__main__":
    main()
