#!/usr/bin/env python3

# Source: https://zenodo.org/records/13926316
# DOI: 10.5281/zenodo.13926316 (dataset; the record names no published paper)
#   Duplaga, M. (2024). The role of technology anxiety in the use of e-health
#   solutions in Polish society [Dataset]. Zenodo.
# Data: "Dataset.xlsx": 1,661 Polish respondents. Three instruments at the item level
#       on two different response formats, so three tables.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: NOT shipped. The source is an .xlsx whose headers are the bare codes
#   TAS1-11 / EH1-10 / E-SERV1-8 and there is no codebook, questionnaire or README in
#   the deposit -- so neither a label level nor a document carries the stems. The
#   wording is in the paper, which the record does not name.
#
# Three tables:
#   duplaga_2024_technology_anxiety 11 items, TAS, 1-5 agreement.
#   duplaga_2024_ehealth_attitudes  10 items, EH,  1-5 agreement.
#   duplaga_2024_eservice_use        8 items, E-SERV, 0/1 use of a given e-service.
# The E-SERV block is dichotomous, which belongs in core rather than the nominal
# standard: with exactly two options the ordered/unordered distinction is vacuous.
# Covariates: cov_gender, cov_residence, cov_education, cov_marital, cov_vocational,
#   cov_income, cov_age, cov_chronic_disease, cov_status.
# id: the deposit's "ID" (1,661 distinct over 1,661 rows).
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_13926316"
TAS = [f"TAS{i}" for i in range(1, 12)]
EH = [f"EH{i}" for i in range(1, 11)]
ESERV = [f"E-SERV{i}" for i in range(1, 9)]
# "E-SERV1" carries a hyphen, which is kept out of the shipped code so the item
# reads as a plain token; the mapping is explicit rather than positional.
RENAME_ESERV = {c: f"ESERV{i}" for i, c in enumerate(ESERV, 1)}
COVS = {"GENDER": "cov_gender", "RESID": "cov_residence", "EUC": "cov_education",
        "MARITAL": "cov_marital", "VOCAT": "cov_vocational", "INCOME": "cov_income",
        "AGE": "cov_age", "CHRONIC": "cov_chronic_disease", "STATUS": "cov_status"}


def main() -> None:
    p = zenodo_fetch(13926316, "Dataset.xlsx", RAW_DIR)
    d = pd.read_excel(p, sheet_name=0)
    assert len(d) == 1661, len(d)
    src = list(d.columns)
    books(src, {
        "shipped": TAS + EH + ESERV,
        "covariate": list(COVS),
        "respondent id": ["ID"],
    })
    d = d.rename(columns={"ID": "id", **COVS})
    covs = list(COVS.values())
    assert d["id"].nunique() == len(d), d["id"].nunique()
    v5, v2 = range(1, 6), range(0, 2)
    emit({
        "duplaga_2024_technology_anxiety": (long(d, TAS, covs, valid=v5), pv_for(TAS, v5)),
        "duplaga_2024_ehealth_attitudes": (long(d, EH, covs, valid=v5), pv_for(EH, v5)),
        "duplaga_2024_eservice_use": (long(d, ESERV, covs, valid=v2, rename=RENAME_ESERV),
                                      pv_for(RENAME_ESERV.values(), v2)),
    })


if __name__ == "__main__":
    main()
