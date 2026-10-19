#!/usr/bin/env python3

# Source: https://zenodo.org/records/5708255
# DOI: 10.5281/zenodo.5708255 (dataset; isSourceOf 10.5281/zenodo.4467957)
#   Lischer, S., Safi, N., & Dickson, C. (2021). Remote learning and students' mental
#   health during the Covid-19 pandemic: Dataset and questionnaire [Dataset]. Zenodo.
# Data: "Datensatz_Publikation_Lischer.sav": 557 Swiss students. The deposit also
#       carries its own questionnaire PDF ("Q Covid Students Lischer et al 2021.pdf"),
#       which is the codebook recorded at ingest.
# License: CC BY 4.0 (Zenodo record).
#
# Item text: SHIPPED (German as administered, with an English translation). Both label
#   levels checked and both are populated: the variable labels carry each PHQ stem and
#   the value labels carry the four frequency anchors. The PHQ family is an express
#   GRANT in itemtext/instrument_rights_register.csv -- "All PHQ, GAD-7 screeners and
#   translations are downloadable from this website and no permission is required to
#   reproduce, translate, display or distribute them" (phqscreeners.com) -- so this is
#   the one instrument in this batch whose wording is clearly free to redistribute.
#
# One table: lischer_2021_phq4, the 4-item PHQ-4, 1-4.
#   resp 5 ("Keine Angabe", no answer) is the deposit's missing code and is dropped.
# NOT shipped as items, deliberately:
#   SORGEN_AND, SORGEN_PSY -- ordinal worry ratings, but only two of them, which is
#     too thin to constitute a scale; carried as covariates instead.
#   AUSW_EINK, AUSW_SOZ, AUSW_PRUEF -- NOT ordinal. The anchors are "Bislang kein
#     Thema" / "Befuerchte ich" / "Ist bereits eingetreten" / "Betrifft mich nicht",
#     which is a nominal set (the last category is not an extreme of the first three),
#     so these cannot be `resp` under datastandard.md and are carried as covariates.
# Covariates: cov_age, cov_age_group, cov_gender, cov_gender_3cat,
#   cov_worry_others_health, cov_worry_own_mental_health, cov_impact_income,
#   cov_impact_social_contact, cov_impact_exams.
# Not shipped at all: EINVER, a consent flag with the single value 1 for every row.
# id: the deposit's "IFDN" (557 distinct over 557 rows).
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_5708255"
PHQ = [f"PHQ4_{i:02d}" for i in range(1, 5)]
COVS = {"AGE_num": "cov_age", "AGE_group": "cov_age_group",
        "GENDER": "cov_gender", "SEX": "cov_gender_3cat",
        "SORGEN_AND": "cov_worry_others_health",
        "SORGEN_PSY": "cov_worry_own_mental_health",
        "AUSW_EINK": "cov_impact_income",
        "AUSW_SOZ": "cov_impact_social_contact",
        "AUSW_PRUEF": "cov_impact_exams"}
MISSING_CODE = 5   # "Keine Angabe" on every 1-4 item in this deposit


def main() -> None:
    import pyreadstat
    d, meta = pyreadstat.read_sav(
        zenodo_fetch(5708255, "Datensatz_Publikation_Lischer.sav", RAW_DIR),
        apply_value_formats=False)
    assert len(d) == 557, len(d)
    books(list(d.columns), {
        "shipped": PHQ,
        "covariate": list(COVS),
        "respondent id": ["IFDN"],
        "consent flag, single value 1 for every row": ["EINVER"],
    })
    d = d.rename(columns={"IFDN": "id", **COVS})
    assert d["id"].nunique() == len(d), d["id"].nunique()
    for c in PHQ:
        d[c] = d[c].replace(MISSING_CODE, pd.NA)
    v = range(1, 5)
    emit({"lischer_2021_phq4":
          (long(d, PHQ, list(COVS.values()), valid=v), pv_for(PHQ, v))})


if __name__ == "__main__":
    main()
