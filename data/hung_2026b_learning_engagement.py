#!/usr/bin/env python3

# Source: https://zenodo.org/records/19784338
# DOI: 10.5281/zenodo.19784338 (dataset; the record names no published paper)
#   Hung (2026). Growth and Fixed Mindsets as Correlates of Learning Engagement: A
#   Two-Study Investigation of the Serial Mediating Roles of the Two Dimensions of
#   Grit [Dataset]. Zenodo.
# Data: "727.sav" and "669.sav" -- the paper's two studies, 727 and 669 Chinese
#       students, SAME four instruments and SAME 1-7 response format. Per
#       datastandard.md's confirmed-identical-administration guidance they ship as one
#       file per instrument with cov_study distinguishing them, not as split files.
#       The item SETS differ slightly between studies (study 1 has AE12-14 and POE6,
#       study 2 has AE12-17 and COI11), which long format carries without padding.
# License: CC BY 4.0 (Zenodo record).
#
# NAMING: this author has a SECOND 2026 Zenodo deposit (10.5281/zenodo.18113188, 522
# students) already in the IRW as hung_2026_swls / hung_2026_uwes_s / hung_2026_grit /
# hung_2026_growth_mindset, carrying the same four instruments. These are different
# respondents from a different paper, so they are different tables; the `2026b` marks
# the second deposit and keeps the names from colliding. They must NOT be merged with
# the 18113188 tables: different paper, different samples, and this deposit's codes
# carry no R/F direction suffix.
#
# Item text: SHIPPED for the MINDSET table only; HELD for the other three, all on the
#   rights register. Both label levels were checked and the English stems are present
#   for every item, so all four are extraction-solved and ship immediately on a ruling.
#     LS1-5    = Satisfaction With Life Scale -> register verdict BLOCK.
#     VE/DE/AE = Utrecht Work Engagement Scale-Student -> register verdict BLOCK.
#     POE/COI  = Grit scale -> register verdict BLOCK (both the 12-item and Grit-S rows).
#   None of those three code prefixes is matched by the register's own code patterns
#   (^swls, ^s?wemwbs, ^uwes have no hit on LS1/VE1/POE1), so they were resolved by
#   reading the item text, not by code name.
#   FM/GM are Dweck implicit-theories-of-intelligence items, which this project has
#   already shipped from the sibling deposit (hung_2026_growth_mindset), so the mindset
#   wording ships here on the same basis.
#
# Four tables, all 1-7:
#   hung_2026b_swls       5 items (LS1-LS5).
#   hung_2026b_uwes_s    up to 16 items: VE vigour, DE dedication, AE absorption.
#   hung_2026b_grit      up to 11 items: POE perseverance of effort, COI consistency
#                        of interest.
#   hung_2026b_mindset    6 items: FM1-3 fixed-mindset wording, GM4-6 growth.
# Not shipped: the (av) columns -- GM, FM, POE, COI, LS and LE subscale means.
# Covariates: cov_gender, cov_age, cov_ethnicity, cov_grade, cov_location, cov_study.
# id: the deposit's "ID" is only unique WITHIN a study, so ids are prefixed with the
#   study ("s1-", "s2-") -- stacking two samples on a bare id would silently merge
#   two different people (feedback_id_collision_prefix).
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


RAW_DIR = RAW_ROOT / "10_5281_zenodo_19784338"
SWLS = [f"LS{i}" for i in range(1, 6)]
UWES = ([f"VE{i}" for i in range(1, 7)] + [f"DE{i}" for i in range(8, 12)]
        + [f"AE{i}" for i in range(12, 18)])
GRIT = [f"POE{i}" for i in (1, 4, 6, 9, 10)] + [f"COI{i}" for i in (3, 5, 7, 8, 11)]
MINDSET = ["FM1", "FM2", "FM3", "GM4", "GM5", "GM6"]
COVS = {"gender": "cov_gender", "age": "cov_age", "ethnicity": "cov_ethnicity",
        "grade": "cov_grade", "location": "cov_location"}
FILES = {"s1": "727.sav", "s2": "669.sav"}


def main() -> None:
    import pyreadstat
    frames = []
    for study, fname in FILES.items():
        d, meta = pyreadstat.read_sav(zenodo_fetch(19784338, fname, RAW_DIR),
                                      apply_value_formats=False)
        means = [c for c in d.columns if "av" in str(c)]
        assert len(means) == 6, means
        present = [c for c in SWLS + UWES + GRIT + MINDSET if c in d.columns]
        books(list(d.columns), {
            "shipped": present,
            "covariate": list(COVS),
            "respondent id": ["ID"],
            "subscale mean computed by the depositor": means,
        })
        d = d.rename(columns={"ID": "id", **COVS})
        assert d["id"].nunique() == len(d), (study, d["id"].nunique())
        # ID restarts per study, so it is prefixed rather than trusted across files.
        d["id"] = study + "-" + d["id"].astype("int64").astype(str)
        d["cov_study"] = study
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    assert d["id"].nunique() == len(d), d["id"].nunique()
    covs = list(COVS.values()) + ["cov_study"]
    v = range(1, 8)
    out = {}
    for name, items in (("hung_2026b_swls", SWLS), ("hung_2026b_uwes_s", UWES),
                        ("hung_2026b_grit", GRIT), ("hung_2026b_mindset", MINDSET)):
        cols = [c for c in items if c in d.columns]
        out[name] = (long(d, cols, covs, valid=v), pv_for(cols, v))
    emit(out)


if __name__ == "__main__":
    main()
